#!/bin/bash

TTF_FILES=(*.ttf)

# 如果当前目录没有 ttf 文件
if [ ${#TTF_FILES[@]} -eq 0 ]; then
  echo "当前目录没有 ttf 文件。"
  exit 1
fi

echo "可用的 TTF 文件:"
for i in "${!TTF_FILES[@]}"; do
  echo "$i) ${TTF_FILES[$i]}"
done

read -p "请输入要添加字距调整的 TTF 文件编号: " choice
if [[ -z "$choice" || "$choice" -lt 0 || "$choice" -ge "${#TTF_FILES[@]}" ]]; then
  echo "无效的选择。"
  exit 1
fi

selected_file="${TTF_FILES[$choice]}"
output_file="标点间距_${selected_file}"

python3 modify_kerning.py "$selected_file" "$output_file"
echo "已生成: $output_file"