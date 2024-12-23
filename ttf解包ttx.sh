#!/bin/bash

# 查找当前目录下所有 TTF 文件并按日期排序
TTF_FILES=($(ls -t *.ttf 2>/dev/null))

# 检查是否找到 TTF 文件
if [ ${#TTF_FILES[@]} -eq 0 ]; then
    echo "错误: 当前目录下没有找到 TTF 文件."
    exit 1
fi

# 列出文件并提供选择
echo "找到以下 TTF 文件："
for i in "${!TTF_FILES[@]}"; do
    echo "$((i + 1)): ${TTF_FILES[i]}"
done

# 提示用户选择文件
read -p "请输入要解包的字体编号 (1-${#TTF_FILES[@]}): " choice

# 检查用户输入是否有效
if ! [[ "$choice" =~ ^[1-9][0-9]*$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "${#TTF_FILES[@]}" ]; then
    echo "错误: 选择无效."
    exit 1
fi

# 获取用户选择的 TTF 文件
SELECTED_TTF="${TTF_FILES[$((choice - 1))]}"

# 解包 TTF 文件为 TTX 格式
ttx -z extfile "$SELECTED_TTF"

# 检查解包是否成功
if [ $? -eq 0 ]; then


    echo "解包成功: $SELECTED_TTF -> $FONT_NAME/${FONT_NAME}.ttx"
else
    echo "解包失败."
    exit 1
fi