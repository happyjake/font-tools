#!/bin/bash

# 查找当前目录下所有 TTX 文件并按日期排序
TTX_FILES=($(ls -t *.ttx 2>/dev/null))

# 检查是否找到 TTX 文件
if [ ${#TTX_FILES[@]} -eq 0 ]; then
    echo "错误: 当前目录下没有找到 TTX 文件."
    exit 1
fi

# 列出文件并提供选择
echo "找到以下 TTX 文件："
for i in "${!TTX_FILES[@]}"; do
    echo "$((i + 1)): ${TTX_FILES[i]}"
done

# 提示用户选择文件
read -p "请输入要打包的字体编号 (1-${#TTX_FILES[@]}): " choice

# 检查用户输入是否有效
if ! [[ "$choice" =~ ^[1-9][0-9]*$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "${#TTX_FILES[@]}" ]; then
    echo "错误: 选择无效."
    exit 1
fi

# 获取用户选择的 TTX 文件
SELECTED_TTX="${TTX_FILES[$((choice - 1))]}"

# 打包 TTX 文件为 TTF 格式
ttx "$SELECTED_TTX"

# 检查打包是否成功
if [ $? -eq 0 ]; then
    echo "打包成功: $SELECTED_TTX -> ${SELECTED_TTX%.ttx}.ttf"
else
    echo "打包失败."
    exit 1
fi