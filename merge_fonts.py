import sys
import traceback
import os
import time
from collections import deque
from fontTools.ttLib import TTFont

def get_unicode_range(range_str):
    """Parse a Unicode range string. Splits by space, supports formats like:
    U+4E00-U+9FFF or 4E00-9FFF or single chars 'a', 'U+4E00', etc."""
    codepoints = set()
    parts = range_str.strip().split()
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start_str, end_str = part.replace('U+', '').split('-')
            start = int(start_str, 16)
            end = int(end_str, 16)
            codepoints.update(range(start, end + 1))
        else:
            part = part.replace('U+', '')
            if len(part) == 1:
                codepoints.add(ord(part))
            else:
                codepoints.add(int(part, 16))
    return codepoints

def merge_fonts(main_font_path, secondary_font_path, unicode_range):
    """Merge glyphs from secondary_font into main_font for given codepoints, showing progress."""
    try:
        start_time = time.time()

        # Load fonts
        main_font = TTFont(main_font_path)
        secondary_font = TTFont(secondary_font_path)

        # Convert range to a set of codepoints
        codepoints = get_unicode_range(unicode_range)
        if not codepoints:
            print("未指定有效的合并范围，退出。")
            return

        print(f"合并范围: {hex(min(codepoints))} 到 {hex(max(codepoints))} （共 {len(codepoints)} 个字符）")

        # Cache tables for speed
        main_glyf = main_font['glyf']
        main_hmtx = main_font['hmtx'].metrics
        sec_glyf = secondary_font['glyf']
        sec_hmtx = secondary_font['hmtx'].metrics

        sec_best_cmap = secondary_font['cmap'].getBestCmap()
        main_best_cmap = main_font['cmap'].getBestCmap()

        # Collect glyphs to merge
        glyphs_to_merge = set()
        for cp in codepoints:
            gname = sec_best_cmap.get(cp)
            if gname and gname in sec_glyf:
                glyphs_to_merge.add(gname)

        print(f"需要处理的字形数: {len(glyphs_to_merge)}")

        # BFS approach to copy glyphs + dependencies
        visited = set()
        queue = deque(glyphs_to_merge)
        processed_count = 0
        progress_interval = 50

        while queue:
            glyph_name = queue.pop()
            if glyph_name in visited:
                continue
            visited.add(glyph_name)

            # Copy glyph data
            if glyph_name in sec_glyf:
                main_glyf[glyph_name] = sec_glyf[glyph_name]
            if glyph_name in sec_hmtx:
                main_hmtx[glyph_name] = sec_hmtx[glyph_name]
            processed_count += 1

            # Print progress every N glyphs
            if processed_count % progress_interval == 0:
                print(f"已处理 {processed_count} 个字形...")

            # If it's composite, enqueue dependencies
            glyph_obj = sec_glyf[glyph_name]
            if hasattr(glyph_obj, 'components') and glyph_obj.components:
                for comp in glyph_obj.components:
                    if comp.glyphName not in visited:
                        queue.appendleft(comp.glyphName)

        # Update cmap for all codepoints, show progress
        print("\n更新 CMap...")
        cmap_count = 0
        for cp in codepoints:
            gname = sec_best_cmap.get(cp)
            if gname:
                main_best_cmap[cp] = gname
            cmap_count += 1
            if cmap_count % progress_interval == 0:
                print(f"已更新 {cmap_count} / {len(codepoints)} 个 codepoint 映射...")

        # Copy .notdef if present
        if '.notdef' in sec_glyf:
            main_glyf['.notdef'] = sec_glyf['.notdef']
            print("已复制 .notdef 字形")

        # Save output
        base_main_name = os.path.splitext(os.path.basename(main_font_path))[0]
        base_secondary_name = os.path.splitext(os.path.basename(secondary_font_path))[0]
        output_file = f'合并完成_{base_main_name}_{base_secondary_name}.ttf'
        # log before saving
        print(f"\n保存合并后文件中...")
        main_font.save(output_file)

        elapsed = time.time() - start_time
        print(f"\n合并完成，处理 {processed_count} 个字形，共耗时 {elapsed:.2f} 秒。")
        print(f"已将文件另存为：{output_file}")

    except Exception as e:
        print(f"发生错误：{e}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python merge_fonts.py <主字体路径> <辅助字体路径> <Unicode范围>")
        print("例如: python merge_fonts.py main.ttf secondary.ttf 'U+4E00-U+9FFF'")
        sys.exit(1)

    merge_fonts(sys.argv[1], sys.argv[2], sys.argv[3])