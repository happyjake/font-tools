import os
import time
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Identity

def list_ttf_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith('.ttf')]

def fix_gvar_table(font):
    """Remove only glyph variations that fail to parse."""
    if "gvar" not in font:
        return
    broken = []
    for glyph_name in list(font["gvar"].variations.keys()):
        try:
            _ = font["gvar"].variations[glyph_name]  # Force parse
        except AssertionError:
            broken.append(glyph_name)
    for glyph_name in broken:
        del font["gvar"].variations[glyph_name]

def adjust_weight(font, scale):
    """Scale outlines by 'scale' and fix gvar table if needed."""
    t0 = time.time()
    fix_gvar_table(font)
    fix_time = time.time() - t0

    glyf_table = font['glyf']
    t0 = time.time()
    for glyph_name in font.getGlyphOrder():
        glyph = glyf_table[glyph_name]
        if glyph.isComposite():
            continue

        pen = TTGlyphPen(font.getGlyphSet())
        transform = Identity.scale(scale)
        transform_pen = TransformPen(pen, transform)
        glyph.draw(transform_pen, glyf_table)

        glyf_table[glyph_name] = pen.glyph()
    scale_time = time.time() - t0

    return fix_time, scale_time

def main():
    overall_start = time.time()
    current_directory = os.getcwd()
    ttf_files = list_ttf_files(current_directory)

    if not ttf_files:
        print("当前目录没有找到TTF文件。")
        return

    print("可用的TTF文件:")
    for index, file in enumerate(ttf_files):
        print(f"{index}: {file}")

    input_start = time.time()
    try:
        choice = int(input("请输入要修改的TTF文件编号: "))
        if choice < 0 or choice >= len(ttf_files):
            print("选择无效。")
            return
    except ValueError:
        print("输入无效。请输入一个数字。")
        return

    try:
        scale_input = input("请输入缩放比例 并耐心等待（120%输入1.2，80%输入0.8）：")
        if scale_input.endswith('%'):
            scale = float(scale_input[:-1]) / 100
        else:
            scale = float(scale_input)
        if scale <= 0:
            print("缩放比例必须大于0。")
            return
    except ValueError:
        print("输入无效。请输入一个数字。")
        return
    input_time = time.time() - input_start

    selected_file = ttf_files[choice]
    load_start = time.time()
    font = TTFont(selected_file)
    load_time = time.time() - load_start

    fix_time, scale_time = adjust_weight(font, scale)
    
    save_start = time.time()
    scale_percentage = f"{int(scale * 100)}%"
    new_file_name = f"{scale_percentage}_{os.path.basename(selected_file)}"
    font.save(new_file_name)
    save_time = time.time() - save_start

    overall = time.time() - overall_start

    print(f"\n性能统计:")
    print(f"输入处理耗时: {input_time:.2f}s")
    print(f"字体加载耗时: {load_time:.2f}s")
    print(f"修复 gvar 耗时: {fix_time:.2f}s")
    print(f"缩放轮廓耗时: {scale_time:.2f}s")
    print(f"保存字体耗时: {save_time:.2f}s")
    print(f"总耗时: {overall:.2f}s\n")
    print(f"修改后的字体已保存为: {new_file_name}")

if __name__ == "__main__":
    main()
