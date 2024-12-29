import sys
from fontTools.ttLib import TTFont

def get_glyph_name_for_unicode(font, unicode_value):
    """Get glyph name for a unicode value"""
    try:
        for table in font['cmap'].tables:
            if unicode_value in table.cmap:
                return table.cmap[unicode_value]
    except TypeError:
        print(f"警告: 无法处理 Unicode {hex(unicode_value)}")
    return None

def modify_glyph_width(font, unicode_value, width_adjustment):
    """Modify the advance width of a glyph"""
    glyph_name = get_glyph_name_for_unicode(font, unicode_value)
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
    
    # Unicode values for quotes and punctuation
    quotes = [
        0x0027,  # ' APOSTROPHE
        0x0022,  # " QUOTATION MARK
        0x2018,  # ' LEFT SINGLE QUOTATION MARK
        0x2019,  # ' RIGHT SINGLE QUOTATION MARK
        0x201C,  # " LEFT DOUBLE QUOTATION MARK
        0x201D,  # " RIGHT DOUBLE QUOTATION MARK
    ]
    
    punctuation = [
        0x002C,  # , COMMA
        0x002E,  # . FULL STOP
        0x003B,  # ; SEMICOLON
        0x003A,  # : COLON
        0x0021,  # ! EXCLAMATION MARK
        0x003F,  # ? QUESTION MARK
    ]
    
    # Adjust width for each character
    for unicode_value in quotes:
        modify_glyph_width(font, unicode_value, -40)
    for unicode_value in punctuation:
        modify_glyph_width(font, unicode_value, -20)
        
    font.save(output_ttf)
    print(f"字体'{input_ttf}'已修改字符宽度，并保存为'{output_ttf}'。")

if __name__ == "__main__":
    main()