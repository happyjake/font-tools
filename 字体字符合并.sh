#!/bin/bash


# 列出当前目录中的 TTF 文件
echo "

不同UPM单位的字体合并到一起会有显示问题
如果合并完成有bug
请先运行改《查看UPM脚本》确定是否是统一的1000
如果不是，再运行《修改UPM脚本》改为统一1000再来合并！！！

当主字体是可变字体 次字体是单字重字体时
两者必须都包含需要合并的符号 否则无法正确合并
"
ttf_files=(*.ttf)

if [ ${#ttf_files[@]} -eq 0 ]; then
    echo "当前目录没有找到 TTF 文件。"
    exit 1
fi

# 显示可用的字体文件
for i in "${!ttf_files[@]}"; do
    echo "$((i + 1)): ${ttf_files[i]}"
done

# 选择主字体
read -p "请选择主字体文件的序号 (1-${#ttf_files[@]}): " main_index
if [[ $main_index -lt 1 || $main_index -gt ${#ttf_files[@]} ]]; then
    echo "无效的序号"
    exit 1
fi
main_font="${ttf_files[$((main_index - 1))]}"

# 选择次字体
read -p "请选择次字体文件的序号 (1-${#ttf_files[@]}): " secondary_index
if [[ $secondary_index -lt 1 || $secondary_index -gt ${#ttf_files[@]} || $secondary_index -eq main_index ]]; then
    echo "无效的序号或选择了相同的字体"
    exit 1
fi
secondary_font="${ttf_files[$((secondary_index - 1))]}"

# 显示符号范围供用户选择, 查找字符编码参考链接
# https://www.babelstone.co.uk/Unicode/whatisit.html
# https://codepoints.net/U+2019?lang=en
# 0x0021-0x007E 是基本拉丁文字符，包含了英文标点，数字，大小写字母等。 见 https://codepoints.net/basic_latin
# 0x2018-0x2019 是中文引号 ‘’，但的英文文章里也经常用到。 见 https://codepoints.net/general_punctuation
#               如果不加上，合并后的字体在显示英文文章时会留下巨大的空格。
# 0x2000-0x206F 整个general puctuation。 见 https://codepoints.net/general_punctuation
symbol_ranges=("0x0030-0x0039" "0x0021-0x007E 0x2000-0x206F" "0x2800-0x28FF" "自定义输入")
echo "可用的符号编码范围：1 仅数字 2 基本拉丁文 3 盲文 4 自定义输入"
for i in "${!symbol_ranges[@]}"; do
    echo "$((i + 1)): ${symbol_ranges[i]}"
done

# 选择符号范围
read -p "请选择要替换的符号范围编号 (1-${#symbol_ranges[@]}): " range_index

if [[ $range_index -lt 1 || $range_index -gt ${#symbol_ranges[@]} ]]; then
    echo "无效的范围编号"
    exit 1
fi

if [[ $range_index -eq 4 ]]; then
    read -p "请输入字符 支持以下几种格式
    单个字符
    多个字符用空格分隔  比如《我 饿 了》
    字符范围 比如0-8 输入0x0030-0x0038
    ： " custom_input
    selected_range="$custom_input"
else
    selected_range=${symbol_ranges[$((range_index - 1))]}
fi

# 调用 Python 脚本进行合并替换
python merge_fonts.py "$main_font" "$secondary_font" "$selected_range"