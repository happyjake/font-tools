import sys
from fontTools.ttLib import TTFont

def get_unicode_range(range_str):
    """获取 Unicode 范围"""
    codepoints = []
    for part in range_str.split(' '):
        if len(part) == 1:  # 如果是单个字符
            codepoints.append(ord(part))
        elif part.startswith('U+'):
            start_end = part[2:].split('-')
            if len(start_end) == 2:
                start = int(start_end[0], 16)
                end = int(start_end[1], 16)
                codepoints.extend(range(start, end + 1))
            else:
                codepoints.append(int(part[2:], 16))
        else:
            start, end = part.split('-')
            codepoints.extend(range(int(start, 16), int(end, 16) + 1))
    return codepoints

def merge_fonts(main_font_path, secondary_font_path, unicode_range):
    try:
        main_font = TTFont(main_font_path)
        secondary_font = TTFont(secondary_font_path)

        codepoints = get_unicode_range(unicode_range)

        print(f"合并范围: {min(codepoints):#x} 到 {max(codepoints):#x} （共 {len(codepoints)} 个字符）")

        processed_count = 0

        for codepoint in codepoints:
            glyph_name = secondary_font['cmap'].tables[0].cmap.get(codepoint)
            if glyph_name:
                processed_count += 1

                # 替换或添加字形
                if glyph_name in secondary_font['glyf'].keys():
                    # 确保在主字体中有相应的字形
                    if glyph_name not in main_font['glyf'].keys():
                        main_font['glyf'][glyph_name] = secondary_font['glyf'][glyph_name]
                        # 复制宽度信息
                        if glyph_name in secondary_font['hmtx'].metrics:
                            main_font['hmtx'].metrics[glyph_name] = secondary_font['hmtx'].metrics[glyph_name]
                    else:
                        # 如果主字体已有字形，替换它
                        main_font['glyf'][glyph_name] = secondary_font['glyf'][glyph_name]
                        if glyph_name in secondary_font['hmtx'].metrics:
                            main_font['hmtx'].metrics[glyph_name] = secondary_font['hmtx'].metrics[glyph_name]

        # 处理 .notdef 字形
        if '.notdef' in secondary_font['glyf'].keys():
            main_font['glyf']['.notdef'] = secondary_font['glyf']['.notdef']

        # 更新字符映射表
        for codepoint in codepoints:
            glyph_name = secondary_font['cmap'].tables[0].cmap.get(codepoint)
            if glyph_name:
                main_font['cmap'].tables[0].cmap[codepoint] = glyph_name

        output_file = f'合并完成_{main_font_path}'
        main_font.save(output_file)
        print(f'合并完成，已将文件另存为：{output_file}')

    except Exception as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python merge_fonts.py <主字体路径> <辅助字体路径> <Unicode范围>")
        print("例如: python merge_fonts.py main.ttf secondary.ttf 0x4E00-0x9FFF 或者 '我的,045,gj'")
    else:
        main_font_path = sys.argv[1]
        secondary_font_path = sys.argv[2]
        unicode_range = sys.argv[3]

        merge_fonts(main_font_path, secondary_font_path, unicode_range)