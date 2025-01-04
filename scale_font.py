import os
import time
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Identity
import multiprocessing as mp
from multiprocessing.managers import SyncManager
from functools import partial

def print_progress(current, total, width=50):
    progress = current / total
    filled = int(width * progress)
    bar = f"\r处理进度: [{'=' * filled}{'>' if filled < width else ''}{' ' * (width - filled)}] "
    bar += f"{current}/{total} ({progress:.1%})"
    print(bar, end='', flush=True)
    if current == total:
        print()

def list_ttf_files(directory):
    """Return TTF files sorted by modification time (newest first)"""
    # Get files with timestamps
    ttf_files = []
    for f in os.listdir(directory):
        if f.lower().endswith('.ttf'):
            path = os.path.join(directory, f)
            mtime = os.path.getmtime(path)
            ttf_files.append((mtime, f))
    
    # Sort by timestamp descending
    ttf_files.sort(reverse=True)
    
    # Return only filenames
    return [f for _, f in ttf_files]

def fix_gvar_table(font):
    if "gvar" not in font:
        return
    broken = []
    for glyph_name in list(font["gvar"].variations.keys()):
        try:
            _ = font["gvar"].variations[glyph_name]
        except AssertionError:
            broken.append(glyph_name)
    for glyph_name in broken:
        del font["gvar"].variations[glyph_name]

def process_glyph_chunk(chunk_data):
    chunk, scale, glyf_table = chunk_data
    results = {}

    # show start of chunk work with thread id
    print(f"开始处理字形块, {len(chunk)}个字形，线程ID: {mp.current_process().name}")

    for glyph_name, glyph in chunk:
        if glyph.isComposite():
            continue
            
        pen = TTGlyphPen(None)
        transform = Identity.scale(scale)
        transform_pen = TransformPen(pen, transform)
        # Pass glyf_table to draw()
        glyph.draw(transform_pen, glyf_table)
        results[glyph_name] = pen.glyph()
            
    return results

def adjust_weight(font, scale):
    # Start timing for gvar fix
    fix_start = time.time()
    print("开始修复 gvar...")
    fix_gvar_table(font)
    fix_time = time.time() - fix_start
    print(f"修复 gvar 耗时: {fix_time:.2f}s")
    
    # Start timing for scaling
    scale_start = time.time()
    print("\n开始缩放处理...")
    
    glyf_table = font['glyf']
    glyphs = [(name, glyf_table[name]) for name in font.getGlyphOrder()]
    total_glyphs = len(glyphs)
    
    # Split work into chunks
    cpu_count = mp.cpu_count()
    chunk_size = max(1, total_glyphs // cpu_count)
    chunks = [glyphs[i:i + chunk_size] for i in range(0, len(glyphs), chunk_size)]
    chunks_with_data = [(chunk, scale, glyf_table) for chunk in chunks]
    
    # Process in parallel
    with mp.Pool(cpu_count) as pool:
        results = pool.map(process_glyph_chunk, chunks_with_data)
    
    # Merge results
    processed = 0
    for chunk_result in results:
        for glyph_name, new_glyph in chunk_result.items():
            glyf_table[glyph_name] = new_glyph
            processed += 1
            # Show progress every 10 glyphs
            if processed % 1000 == 0 or processed == total_glyphs:
                print_progress(processed, total_glyphs)
            
    scale_time = time.time() - scale_start
    print(f"\n缩放完成，耗时: {scale_time:.2f}s")
    
    return fix_time, scale_time

def main():
    overall_start = time.time()
    current_directory = os.getcwd()
    ttf_files = list_ttf_files(current_directory)

    if not ttf_files:
        print("当前目录未找到TTF。")
        return

    print("可用TTF:")
    for i, f in enumerate(ttf_files):
        print(f"{i}: {f}")

    print("\n读取输入中...")
    step_start = time.time()
    try:
        choice = int(input("请输入TTF编号: "))
        if not 0 <= choice < len(ttf_files):
            print("选择无效。")
            return
    except ValueError:
        print("输入无效。")
        return

    try:
        scale_input = input("请输入缩放比例(如1.2或80%)：")
        if scale_input.endswith('%'):
            scale = float(scale_input[:-1]) / 100
        else:
            scale = float(scale_input)
        if scale <= 0:
            print("缩放比例必须>0。")
            return
    except ValueError:
        print("输入无效。")
        return
    input_time = time.time() - step_start
    print(f"输入处理耗时: {input_time:.2f}s\n")

    selected_file = ttf_files[choice]
    print("加载字体中...")
    step_start = time.time()
    font = TTFont(selected_file)
    load_time = time.time() - step_start
    print(f"字体加载耗时: {load_time:.2f}s\n")

    fix_time, scale_time = adjust_weight(font, scale)

    print("保存字体中...")
    step_start = time.time()
    scale_percentage = f"{int(scale * 100)}%"
    new_file_name = f"{scale_percentage}_{os.path.basename(selected_file)}"
    font.save(new_file_name)
    save_time = time.time() - step_start
    print(f"保存字体耗时: {save_time:.2f}s\n")

    overall = time.time() - overall_start
    print("全部步骤完成。")
    print(f"总耗时: {overall:.2f}s")
    print(f"已保存: {new_file_name}")

if __name__ == "__main__":
    main()