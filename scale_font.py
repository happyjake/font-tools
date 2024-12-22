import os
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Identity

def list_ttf_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.ttf')]

def adjust_weight(font, scale):
    glyf_table = font['glyf']
    for glyph_name in font.getGlyphOrder():
        glyph = glyf_table[glyph_name]
        if glyph.isComposite():
            continue

        pen = TTGlyphPen(font.getGlyphSet())
        transform = Identity.scale(scale)  # Create a scaling transform

        # Draw the original glyph with transformation applied
        transform_pen = TransformPen(pen, transform)
        glyph.draw(transform_pen, glyf_table)
        
        # Replace the original glyph with the transformed one
        glyf_table[glyph_name] = pen.glyph()

def main():
    current_directory = os.getcwd()
    ttf_files = list_ttf_files(current_directory)

    if not ttf_files:
        print("当前目录没有找到TTF文件。")
        return

    print("可用的TTF文件:")
    for index, file in enumerate(ttf_files):
        print(f"{index}: {file}")

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
            scale = float(scale_input[:-1]) / 100  # 去掉百分号并转换为浮点数
        else:
            scale = float(scale_input)  # 直接转换为浮点数

        if scale <= 0:
            print("缩放比例必须大于0。")
            return
    except ValueError:
        print("输入无效。请输入一个数字。")
        return

    selected_file = ttf_files[choice]
    font = TTFont(selected_file)
    
    adjust_weight(font, scale)

    # 生成新的文件名，缩放比例转换为百分比格式
    scale_percentage = f"{int(scale * 100)}%"  # 将小数转换为百分比格式
    new_file_name = f"{scale_percentage}_{os.path.basename(selected_file)}"
    font.save(new_file_name)
    print(f"修改后的字体已保存为: {new_file_name}")

if __name__ == "__main__":
    main()
