import sys
from fontTools.ttLib import TTFont

def modify_metrics(input_ttf, output_ttf):
    try:
        # 打开 TTF 文件
        font = TTFont(input_ttf)

        # 修改 OS/2 表
        if 'OS/2' in font:
            OS2_table = font['OS/2']
            OS2_table.sCapHeight = 709
            OS2_table.usWinAscent = 928
            OS2_table.usWinDescent = 244
            OS2_table.sTypoAscender = 850
            OS2_table.sTypoDescender = -150
            OS2_table.sTypoLineGap = 0
            OS2_table.sxHeight = 505
            OS2_table.ySubscriptXSize = 500
            OS2_table.ySubscriptYSize = 500
            OS2_table.ySubscriptXOffset = 0
            OS2_table.ySubscriptYOffset = 62
            OS2_table.ySuperscriptXSize = 500
            OS2_table.ySuperscriptYSize = 500
            OS2_table.ySuperscriptXOffset = 0
            OS2_table.ySuperscriptYOffset = 500
            OS2_table.yStrikeoutSize = 45
            OS2_table.yStrikeoutPosition = 250
   
        # 修改 hhea 表
        if 'hhea' in font:
            hhea_table = font['hhea']
            hhea_table.ascent = 928
            hhea_table.descent = -244
            
        # 修改 post 表
        if 'post' in font:
            post_table = font['post']
            post_table.underlinePosition = -100

        # 修改 vhea 表
        if 'vhea' in font:
            vhea_table = font['vhea']
            vhea_table.ascent = 500
            vhea_table.descent = -500
            vhea_table.lineGap = 0

        # 保存新的 TTF 文件
        font.save(output_ttf)
        font.close()
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python modify_metrics.py <输入TTF文件> <输出TTF文件>")
        sys.exit(1)

    input_ttf = sys.argv[1]
    output_ttf = sys.argv[2]
    success = modify_metrics(input_ttf, output_ttf)
    if not success:
        sys.exit(1)