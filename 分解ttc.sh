#!/bin/bash

# Python脚本路径（假设Python脚本和shell脚本在同一目录下）
UNPACK_SCRIPT="./unpack_all_ttc_fonts.py"

# 查找当前目录下的TTC文件
TTC_FILES=$(find . -maxdepth 1 -type f -name "*.ttc")

# 检查是否找到TTC文件
if [ -z "$TTC_FILES" ]; then
  echo "没有找到TTC字体!"
  exit 1
fi

# 列出找到的TTC文件并编号
echo "找到ttc字体:"
TTC_FILE_ARRAY=()
INDEX=0
for TTC_FILE in $TTC_FILES; do
  echo "$INDEX: $(basename $TTC_FILE)"
  TTC_FILE_ARRAY+=("$TTC_FILE")
  INDEX=$((INDEX + 1))
done

# 读取用户输入的TTC文件索引
read -p "请输入要解包的TTC字体编号: " TTC_INDEX

# 检查输入是否为有效的数字
if ! [[ "$TTC_INDEX" =~ ^[0-9]+$ ]] || [ "$TTC_INDEX" -ge ${#TTC_FILE_ARRAY[@]} ]; then
  echo "错误❌！请输入正确的数字."
  exit 1
fi

# 选定的TTC文件路径
TTC_FILE="${TTC_FILE_ARRAY[$TTC_INDEX]}"

# 检查Python脚本是否存在
if [ ! -f "$UNPACK_SCRIPT" ]; then
  echo "未找到Python脚本!"
  exit 1
fi

# 调用Python脚本来解包TTC中的所有字体
echo "正在从选定的TTC文件中提取字体...
请耐心等待 时间长短取决于ttc字体文件以及手机CPU超大核单核性能"
python3 "$UNPACK_SCRIPT" "$TTC_FILE"

# 检查Python脚本是否成功执行
if [ $? -ne 0 ]; then
  echo "无法解包所选字体！"
  exit 1
fi

echo "所选字体解包成功!"