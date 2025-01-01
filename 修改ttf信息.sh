#!/bin/bash

# 遍历当前目录下的 TTF 文件
counter=1
files=()
for file in *.ttf; do
    echo "${counter}. ${file}"
    files+=("$file")
    counter=$((counter + 1))
done

if [ ${#files[@]} -eq 0 ]; then
    echo "当前目录下没有找到 TTF 文件。"
    exit 1
fi

echo "请输入要修改信息的字体编号："
read choice

if [[ $choice -le 0 || $choice -gt ${#files[@]} ]]; then
    echo "无效的选择，请重新运行脚本。"
    exit 1
fi

selected_file="${files[$choice-1]}"

# 调用 Python 脚本修改字体信息
python3 modify_font_info.py "$selected_file"
if [ $? -eq 0 ]; then
    echo "字体信息修改完成！"
else
    echo "修改失败，请检查错误信息。"
fi