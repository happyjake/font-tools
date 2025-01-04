import os
import time
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Identity
import multiprocessing as mp
from multiprocessing import Pool, Value, Lock
from functools import partial

def print_progress(current, total, width=50):
    """Print progress bar without dependencies"""
    progress = current / total
    filled = int(width * progress)
    bar = f"\r处理进度: [{'=' * filled}{'>' if filled < width else ''}{' ' * (width - filled)}] "
    bar += f"{current}/{total} ({progress:.1%})"
    print(bar, end='', flush=True)
    if current == total:
        print()  # New line on completion

def list_ttf_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith('.ttf')]

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

def process_glyph_chunk(args):
    chunk, scale, progress_counter, total_glyphs, lock = args
    results = {}
    
    for glyph_name, glyph in chunk:
        if glyph.isComposite():
            continue
            
        # Process glyph
        pen = TTGlyphPen(None)  # No font needed for basic pen
        transform = Identity.scale(scale)
        transform_pen = TransformPen(pen, transform)
        glyph.draw(transform_pen)
        results[glyph_name] = pen.glyph()
        
        # Update progress safely
        with lock:
            progress_counter.value += 1
            progress = progress_counter.value
            # Show progress every 10 glyphs
            if progress % 100 == 0 or progress == total_glyphs:
                print_progress(progress, total_glyphs)
            
    return results

def adjust_weight(font, scale):
    print("开始修复 gvar...")
    step_start = time.time()
    fix_gvar_table(font)
    fix_time = time.time() - step_start
    print(f"修复 gvar 耗时: {fix_time:.2f}s\n")

    glyf_table = font['glyf']
    print("开始并行缩放轮廓...")
    step_start = time.time()

    # Prepare data for parallel processing
    glyphs = [(name, glyf_table[name]) for name in font.getGlyphOrder()]
    total_glyphs = len(glyphs)
    
    # Split into chunks for each CPU core
    cpu_count = mp.cpu_count()
    chunk_size = max(1, total_glyphs // cpu_count)
    chunks = [glyphs[i:i + chunk_size] for i in range(0, len(glyphs), chunk_size)]
    
    # Shared progress counter
    progress_counter = Value('i', 0)
    lock = Lock()
    
    # Process chunks in parallel
    pool = Pool(cpu_count)
    process_func = partial(process_glyph_chunk, 
                         scale=scale,
                         progress_counter=progress_counter,
                         total_glyphs=total_glyphs,
                         lock=lock)
    
    results = pool.map(process_func, chunks)
    pool.close()
    pool.join()
    
    # Merge results back to font
    for chunk_result in results:
        for glyph_name, new_glyph in chunk_result.items():
            glyf_table[glyph_name] = new_glyph

    scale_time = time.time() - step_start
    print(f"\n缩放轮廓耗时: {scale_time:.2f}s\n")
    
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