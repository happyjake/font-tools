from fontTools.ttLib import TTFont
import os
import sys
from tqdm import tqdm
from collections import defaultdict

def get_unicode_range(range_str):
    """Parse unicode range from string with multiple formats."""
    codepoints = set()
    
    # Split by spaces first
    for part in range_str.split():
        # Handle hex range format
        if '-' in part:
            start, end = part.split('-')
            start = int(start, 16) if '0x' in start else int(start)
            end = int(end, 16) if '0x' in end else int(end)
            codepoints.update(range(start, end + 1))
        else:
            # Handle character list
            for char in part.split(','):
                if len(char.strip()) > 0:
                    codepoints.add(ord(char[0]))
    
    return sorted(codepoints)  # Return sorted list for consistent processing

def merge_fonts(main_font_path, secondary_font_path, unicode_range):
    """Merge glyphs from secondary font into main font with performance tracking."""
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024

    print(f"开始合并字体...")
    stats = {'total_glyphs': 0, 'processed': 0, 'deps': 0, 'cmap_updates': 0}

    # Load and cache font tables
    main_font = TTFont(main_font_path)
    secondary_font = TTFont(secondary_font_path)
    main_glyf = main_font['glyf']
    secondary_glyf = secondary_font['glyf']
    main_hmtx = main_font['hmtx'].metrics
    secondary_hmtx = secondary_font['hmtx'].metrics

    # Pre-process data
    codepoints = set(get_unicode_range(unicode_range))
    print(f"合并范围: {min(codepoints):#x} 到 {max(codepoints):#x} （共 {len(codepoints)} 个字符）")
    
    secondary_cmap = secondary_font['cmap'].getBestCmap()
    main_glyphs = {name: True for name in main_font.getGlyphOrder()}
    glyph_queue = set()
    cmap_updates = {}

    # Build dependency graph
    print("分析字形依赖关系...")
    t0 = time.time()
    dep_graph = defaultdict(set)
    for codepoint in tqdm(codepoints):
        if codepoint not in secondary_cmap:
            continue
        glyph_name = secondary_cmap[codepoint]
        if glyph_name not in secondary_glyf:
            continue
        
        glyph_queue.add(glyph_name)
        cmap_updates[codepoint] = glyph_name
        
        glyph = secondary_glyf[glyph_name]
        if hasattr(glyph, 'components'):
            deps = {c.glyphName for c in glyph.components}
            dep_graph[glyph_name].update(deps)
            stats['deps'] += len(deps)

    stats['dep_time'] = time.time() - t0
    stats['total_glyphs'] = len(glyph_queue)

    # Copy glyphs with dependencies
    print(f"复制字形数据...")
    t0 = time.time()
    processed = set()
    
    with tqdm(total=len(glyph_queue)) as pbar:
        while glyph_queue:
            glyph_name = glyph_queue.pop()
            if glyph_name in processed:
                continue

            # Process dependencies first
            deps = dep_graph[glyph_name]
            if deps:
                missing_deps = deps - processed
                if missing_deps:
                    glyph_queue.add(glyph_name)
                    for dep in missing_deps:
                        if dep not in main_glyphs:
                            main_glyf[dep] = secondary_glyf[dep]
                            main_hmtx[dep] = secondary_hmtx[dep]
                            main_glyphs[dep] = True
                            processed.add(dep)
                            stats['processed'] += 1
                    continue

            # Copy main glyph
            main_glyf[glyph_name] = secondary_glyf[glyph_name]
            main_hmtx[glyph_name] = secondary_hmtx[glyph_name]
            main_glyphs[glyph_name] = True
            processed.add(glyph_name)
            stats['processed'] += 1
            pbar.update(1)

    stats['copy_time'] = time.time() - t0

    # Update cmap
    print("更新字符映射...")
    t0 = time.time()
    main_font['cmap'].getBestCmap().update(cmap_updates)
    stats['cmap_time'] = time.time() - t0
    stats['cmap_updates'] = len(cmap_updates)

    # Save result
    output_file = f'合并完成_{os.path.splitext(os.path.basename(main_font_path))[0]}.ttf'
    main_font.save(output_file)

    # Print performance stats
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024
    total_time = end_time - start_time

    print(f"\n性能统计:")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"依赖分析: {stats['dep_time']:.2f}秒")
    print(f"字形复制: {stats['copy_time']:.2f}秒")
    print(f"映射更新: {stats['cmap_time']:.2f}秒")
    print(f"内存使用: {end_memory-start_memory:.1f}MB")
    print(f"总字形数: {stats['total_glyphs']}")
    print(f"依赖字形: {stats['deps']}")
    print(f"处理字形: {stats['processed']}")
    print(f"字符映射: {stats['cmap_updates']}")
    print(f"处理速度: {stats['processed']/total_time:.1f}字形/秒")
    print(f"输出文件: {output_file}")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python merge_fonts.py <主字体路径> <辅助字体路径> <Unicode范围>")
        print("例如: python merge_fonts.py main.ttf secondary.ttf 0x4E00-0x9FFF")
        sys.exit(1)
        
    merge_fonts(sys.argv[1], sys.argv[2], sys.argv[3])