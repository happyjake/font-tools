import sys
import traceback
import os
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

def copy_glyph_and_components(src_font, dst_font, glyph_name):
    from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
    if glyph_name not in src_font['glyf']:
        return
    dst_font['glyf'][glyph_name] = src_font['glyf'][glyph_name]
    if glyph_name in src_font['hmtx'].metrics:
        dst_font['hmtx'].metrics[glyph_name] = src_font['hmtx'].metrics[glyph_name]

    # If the glyph is composite, copy its components recursively
    glyph = src_font['glyf'][glyph_name]
    if hasattr(glyph, 'components') and glyph.components:
        for comp in glyph.components:
            copy_glyph_and_components(src_font, dst_font, comp.glyphName)

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
                # 复制该字形及其所有组件
                copy_glyph_and_components(secondary_font, main_font, glyph_name)
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

        base_main_name = os.path.splitext(os.path.basename(main_font_path))[0]
        base_secondary_name = os.path.splitext(os.path.basename(secondary_font_path))[0]
        output_file = f'合并完成_{base_main_name}_{base_secondary_name}.ttf'
        main_font.save(output_file)
        print(f'合并完成，已将文件另存为：{output_file}')

    except Exception as e:
        # more detailed error
        print(f"发生错误：{e}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python merge_fonts.py <主字体路径> <辅助字体路径> <Unicode范围>")
        print("例如: python merge_fonts.py main.ttf secondary.ttf 0x4E00-0x9FFF 或者 '我的,045,gj'")
    else:
        main_font_path = sys.argv[1]
        secondary_font_path = sys.argv[2]
        unicode_range = sys.argv[3]

        merge_fonts(main_font_path, secondary_font_path, unicode_range)