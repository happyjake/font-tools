import os
import time
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Identity

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

def adjust_weight(font, scale):
    print("开始修复 gvar...")
    step_start = time.time()
    fix_gvar_table(font)
    fix_time = time.time() - step_start
    print(f"修复 gvar 耗时: {fix_time:.2f}s\n")

    glyf_table = font['glyf']
    print("开始缩放轮廓...")
    step_start = time.time()

    glyphs = font.getGlyphOrder()
    total_glyphs = len(glyphs)
    processed = 0

    for i, glyph_name in enumerate(glyphs, 1):
        glyph = glyf_table[glyph_name]
        if glyph.isComposite():
            continue
        pen = TTGlyphPen(font.getGlyphSet())
        transform = Identity.scale(scale)
        transform_pen = TransformPen(pen, transform)
        glyph.draw(transform_pen, glyf_table)
        glyf_table[glyph_name] = pen.glyph()
        processed += 1
        
        # Show progress every 10 glyphs
        if i % 100 == 0 or i == total_glyphs:
            # Update progress bar
            print_progress(processed, total_glyphs)

    scale_time = time.time() - step_start
    print(f"缩放轮廓耗时: {scale_time:.2f}s\n")

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