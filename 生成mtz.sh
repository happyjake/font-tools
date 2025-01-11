#!/bin/bash

# Get TTF/TTC files sorted by modification time
declare -A file_times
for file in *.ttf *.ttc; do
    [[ -f "$file" ]] || continue
    file_times["$file"]=$(stat -c %Y "$file")
done

# Check for TTF/TTC files
if [ ${#file_times[@]} -eq 0 ]; then
    echo "当前目录没有找到 TTF/TTC 文件。"
    exit 1
fi

# Sort by modification time (newest first)
readarray -t files < <(
    for file in "${!file_times[@]}"; do
        echo "${file_times[$file]}|$file"
    done | sort -rn | cut -d'|' -f2
)

# Display sorted files with dates
for i in "${!files[@]}"; do
    counter=$((i + 1))
    mtime=$(date -r "${files[i]}" "+%Y-%m-%d %H:%M:%S")
    echo "${counter}. ${files[i]} ($mtime)"
done

if [ ${#files[@]} -eq 0 ]; then
    echo "当前目录下没有找到 TTF/TTC 文件。"
    exit 1
fi

echo "请输入要生成 MTZ 的字体编号："
read choice

if [[ $choice -le 0 || $choice -gt ${#files[@]} ]]; then
    echo "无效的选择，请重新运行脚本。"
    exit 1
fi

selected_file="${files[$choice-1]}"

# 调用 Python 脚本生成 MTZ
python3 mtz_make.py "$selected_file"
if [ $? -eq 0 ]; then
    echo "MTZ 生成完成！"
else
    echo "生成失败，请检查错误信息。"
fi