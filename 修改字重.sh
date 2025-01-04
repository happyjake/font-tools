#!/bin/bash

counter=1
declare -A file_times
files=()

# Get files with modification times
for file in *.ttf; do
    mtime=$(stat -c %Y "$file")
    file_times["$file"]=$mtime
done

# Sort files by modification time (newest first)
readarray -t sorted_files < <(
    for file in "${!file_times[@]}"; do
        echo "${file_times[$file]}|$file"
    done | sort -rn | cut -d'|' -f2
)

# Display sorted files with dates
for file in "${sorted_files[@]}"; do
    mtime=$(date -r "$file" "+%Y-%m-%d %H:%M:%S")
    echo "${counter}. ${file} (${mtime})"
    files+=("$file")
    counter=$((counter + 1))
done

if [ ${#files[@]} -eq 0 ]; then
    echo "当前目录下没有找到 TTF 文件。"
    exit 1
fi

echo "请输入要修改字重的字体编号："
read choice

if [[ $choice -le 0 || $choice -gt ${#files[@]} ]]; then
    echo "无效的选择，请重新运行脚本。"
    exit 1
fi

selected_file="${files[$choice-1]}"

# Prompt for weight scale
echo "请输入字重缩放比例 (例如: 1.2 或 120%)："
read scale_input

# Convert percentage to decimal if needed
if [[ $scale_input == *"%" ]]; then
    scale=$(echo "scale=2; ${scale_input%\%}/100" | bc)
else
    scale=$scale_input
fi

# Validate scale input
if (( $(echo "$scale <= 0" | bc -l) )); then
    echo "缩放比例必须大于0"
    exit 1
fi

# Call Python script with scale parameter
python3 weight_font.py "$selected_file" "$scale"
if [ $? -eq 0 ]; then
    echo "字体字重修改完成！"
else
    echo "修改失败，请检查错误信息。"
fi