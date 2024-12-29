import sys
from fontTools.ttLib import TTFont

def get_glyph_name_for_char(font, char):
    """Get glyph name for a given character"""
    for table in font['cmap'].tables:
        if ord(char) in table.cmap:
            return table.cmap[ord(char)]
    return None

def modify_glyph_width(font, char, width_adjustment):
    """Modify the advance width of a glyph"""
    glyph_name = get_glyph_name_for_char(font, char)
    if glyph_name and glyph_name in font['hmtx'].metrics:
        advance, lsb = font['hmtx'].metrics[glyph_name]
        font['hmtx'].metrics[glyph_name] = (advance + width_adjustment, lsb)

def main():
    if len(sys.argv) != 3:
        print("用法: python modify_kerning.py <输入TTF文件> <输出TTF文件>")
        sys.exit(1)

    input_ttf = sys.argv[1]
    output_ttf = sys.argv[2]
    
    font = TTFont(input_ttf)
    
    # Target characters to modify
    quotes = ["'", '"', ''', ''', '"', '"', "‘", "’"]
    punctuation = [',', '.', ';', ':', '!', '?']
    
    # Adjust width for each character
    for char in quotes:
        modify_glyph_width(font, char, -40)  # Reduce width by 40 units
    for char in punctuation:
        modify_glyph_width(font, char, -20)  # Reduce width by 20 units
        
    font.save(output_ttf)
    print(f"字体'{input_ttf}'已修改字符宽度，并保存为'{output_ttf}'。")

if __name__ == "__main__":
    main()