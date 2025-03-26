# -Mnemonic-word-sorting
助记词排序，钱包找回，输入12位顺序混乱的助记词，输入对应的TRON地址，可以自动完成助记词的排列组合使其对应输入的地址，使用的是BIP44标准派生路径 m/44'/195'/0'/0/0，符合imtoken钱包的规范，如果你记得你的助记词但是不记得顺序，你可以使用这个脚本排序，如果你的助记词不重复的话，应该只会有四亿多种组合，基本上一两个小时就能出结果，可以完全离线本地运行，技术交流：飞机Telegram[@jiutong9999](https://t.me/jiutong9999)




需安装以下必要的库：

pip install bip-utils

pip install numpy

pip install multiprocess
