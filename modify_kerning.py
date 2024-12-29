import sys
from fontTools.ttLib import TTFont

if len(sys.argv) != 3:
    print("用法: python kerning_adjustment.py <输入TTF文件> <输出TTF文件>")
    sys.exit(1)

input_ttf = sys.argv[1]
output_ttf = sys.argv[2]

font = TTFont(input_ttf)

# 检查是否有 GPOS 表
if 'GPOS' in font:
    gpos_table = font['GPOS'].table
    kerning_pairs = gpos_table.LookupList.Lookup[0].SubTable[0].kernTable
    
    # 为 `'` 与所有字母添加字距调整规则
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
        kerning_pairs[("'", char)] = -20

font.save(output_ttf)
print(f"字体'{input_ttf}'已添加字距调整，并保存为'{output_ttf}'。")