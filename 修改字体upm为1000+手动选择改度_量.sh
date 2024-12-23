#!/bin/bash

# 查找当前文件夹下的所有 TTF 文件
font_files=(*.ttf)

# 检查是否有 TTF 文件
if [ ${#font_files[@]} -eq 0 ]; then
    echo "当前文件夹内没有 TTF 字体文件。"
    exit 1
fi

# 打印可用的 TTF 文件
echo "可用的 TTF 字体文件："
for i in "${!font_files[@]}"; do
    echo "$((i + 1)): ${font_files[i]}"
done

# 提示用户输入要修改的字体编号
read -p "请输入要修改的字体编号: " font_index

# 检查输入是否有效
if ! [[ "$font_index" =~ ^[0-9]+$ ]] || [ "$font_index" -lt 1 ] || [ "$font_index" -gt "${#font_files[@]}" ]; then
    echo "无效的输入，请输入有效的字体编号。"
    exit 1
fi

# 获取选中的字体文件
selected_font="${font_files[$((font_index - 1))]}"

# 运行 Python 脚本修改 UPM 值
modified_font="UPM1000_${selected_font%.ttf}.ttf"
python3 change_upm_and_scale.py "$selected_font" "$modified_font"

# 检查 Python 脚本是否成功执行
if [ $? -eq 0 ]; then
    echo "UPM 值修改成功！"
else
    echo "UPM 值修改失败。"
    exit 1
fi

# 查找当前文件夹下的所有包含“modify_metrics”的 Python 脚本
metric_scripts=(*modify_metrics*.py)

# 检查是否有包含 modify_metrics 的 Python 脚本
if [ ${#metric_scripts[@]} -eq 0 ]; then
    echo "当前文件夹内没有包含 modify_metrics 的 Python 脚本。"
    exit 1
fi

# 定义文件名与中文名称的映射
declare -A script_names=(
    ["h_modify_metrics.py"]="华为度量"
    ["m_modify_metrics.py"]="小米度量"
    ["o_modify_metrics.py"]="oppo度量"
    ["r_modify_metrics.py"]="荣耀度量"
    ["v_modify_metrics.py"]="vivo度量"
)

# 打印可用的 Python 脚本
echo "可用的包含 modify_metrics 的 Python 脚本："
for i in "${!metric_scripts[@]}"; do
    script_name="${metric_scripts[i]}"
    if [ -n "${script_names[$script_name]}" ]; then
        echo "$((i + 1)): ${script_names[$script_name]}"
    fi
done

# 提示用户输入要执行的脚本编号
read -p "请输入要执行的脚本编号: " script_index

# 检查输入是否有效
if ! [[ "$script_index" =~ ^[0-9]+$ ]] || [ "$script_index" -lt 1 ] || [ "$script_index" -gt "${#metric_scripts[@]}" ]; then
    echo "无效的输入，请输入有效的脚本编号。"
    exit 1
fi

# 获取选中的脚本
selected_script="${metric_scripts[$((script_index - 1))]}"

# 获取原文件名（不带扩展名）
base_name=$(basename "$selected_font" .ttf)

# 生成输出文件名，保留 UPM1000 信息
output_file="UPM1000_${script_names[$selected_script]}_${base_name}.ttf"

# 执行选中的脚本，并将修改后的字体文件作为参数传递
python3 "$selected_script" "$modified_font" "$output_file"

# 检查脚本是否成功执行
if [ $? -eq 0 ]; then
    echo "脚本执行成功！输出文件：$output_file"
else
    echo "脚本执行失败。"
fi

# 删除中间修改的 TTF 文件（如果需要）
#rm -f "$modified_font"
#echo "已删临时文件：$modified_font"