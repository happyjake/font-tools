#!/bin/bash

# 遍历当前目录下的 TTF 文件
counter=1
files=()
for file in *.ttf; do
    echo "${counter}. ${file}"
    files+=("$file")
    counter=$((counter + 1))
done

echo "请输入要修改的 TTF 的编号："
read choice

if [[ $choice -le 0 || $choice -gt ${#files[@]} ]]; then
    echo "无效的选择，请重新运行脚本。"
    exit 1
fi

selected_file="${files[$choice-1]}"
new_file="VIVO度量_${selected_file}"

# 调用 Python 脚本修改度量
python3 v_modify_metrics.py "$selected_file" "$new_file"
if [ $? -eq 0 ]; then
    echo "度量数据修改完成！新文件已保存为：${new_file}"
else
    echo "修改失败，请检查错误信息。"
fi
