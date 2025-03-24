import sys
import time
import math
import multiprocessing
from itertools import permutations
from collections import Counter
from multiprocessing import Pool, cpu_count, Value, Event
from threading import Thread
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

def calc_total(seq):
    cnt = Counter(seq)
    total = math.factorial(len(seq))
    for v in cnt.values():
        total //= math.factorial(v)
    return total

def unique_permutations(seq):
    seen = set()
    cnt = Counter(seq)
    for p in permutations(seq):
        if p not in seen:
            seen.add(p)
            yield p

def chunked(gen, size):
    chunk = []
    for item in gen:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def derive_address(perm):
    try:
        mnemonic = " ".join(perm)
        seed = Bip39SeedGenerator(mnemonic).Generate()
        bip44_mst = Bip44.FromSeed(seed, Bip44Coins.TRON)
        addr = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        return addr, perm
    except Exception:
        return None, None

def worker_init(target, counter, found):
    global g_target, g_counter, g_found
    g_target = target
    g_counter = counter
    g_found = found

def worker(chunk):
    results = []
    for perm in chunk:
        if g_found.is_set():
            return None
        addr, _ = derive_address(perm)
        with g_counter.get_lock():
            g_counter.value += 1
        if addr == g_target:
            g_found.set()
            return perm
    return None

def progress_monitor(total, counter, found):
    start_time = time.time()
    while not found.is_set():
        with counter.get_lock():
            count = counter.value
        if count >= total:
            break
        elapsed = time.time() - start_time
        speed = count / (elapsed + 1e-9)
        print(f"\r进度: {count}/{total} ({count/total*100:.4f}%) | 速度: {speed:.1f}组合/秒", end="")
        time.sleep(0.1)
    print()

if __name__ == "__main__":
    print("请输入12个助记词（空格分隔）:")
    words = sys.stdin.readline().strip().split()
    if len(words) != 12:
        print("必须输入12个助记词")
        sys.exit(1)

    print("请输入目标TRON地址:")
    target = sys.stdin.readline().strip()

    # 初始检查
    initial_perm = tuple(words)
    addr, _ = derive_address(initial_perm)
    if addr == target:
        print("正确顺序:", " ".join(initial_perm))
        sys.exit(0)

    total = calc_total(words)
    print(f"需要检查的组合总数: {total}")

    # 共享变量初始化
    counter = Value('i', 0)
    found = Event()

    # 创建进程池
    pool = Pool(
        processes=cpu_count(),
        initializer=worker_init,
        initargs=(target, counter, found)
    )

    # 启动进度监控
    monitor = Thread(target=progress_monitor, args=(total, counter, found))
    monitor.start()

    # 生成任务
    try:
        chunk_size = 1000
        gen = chunked(unique_permutations(words), chunk_size)
        
        for result in pool.imap_unordered(worker, gen):
            if result:
                print("\n找到正确组合:", " ".join(result))
                found.set()
                break
    finally:
        pool.close()
        pool.join()
        monitor.join()

    if not found.is_set():
        print("\n未找到匹配的组合")