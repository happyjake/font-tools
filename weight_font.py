from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.misc.transform import Identity
import sys
import os

def add_weight(font_path, weight_factor):
    """Add weight to font by scaling glyphs horizontally"""
    font = TTFont(font_path)
    glyf = font['glyf']
    
    print(f"正在处理字形...")
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if glyph.numberOfContours > 0:  # Skip empty glyphs
            # Create pens for transformation
            pen = TTGlyphPen(None)
            transform = Identity.scale(weight_factor, 1)
            transform_pen = TransformPen(pen, transform)
            
            # Pass glyf table to draw()
            glyph.draw(transform_pen, glyf)
            
            # Replace glyph with transformed version
            glyf[glyph_name] = pen.glyph()
            
    # Update horizontal metrics
    if 'hmtx' in font:
        hmtx = font['hmtx']
        for glyph_name in font.getGlyphOrder():
            width, lsb = hmtx[glyph_name]
            hmtx[glyph_name] = (int(width * weight_factor), int(lsb * weight_factor))
    
    # Update OS/2 weights
    if 'OS/2' in font:
        os2 = font['OS/2']
        os2.usWeightClass = min(1000, int(os2.usWeightClass * weight_factor))
    
    # Save modified font    

    # Get directory and filename
    dir_path = os.path.dirname(font_path)
    base_name = os.path.basename(font_path)

    # Create new filename with weight prefix
    new_name = f"修改字重w{int(weight_factor*100)}_{base_name}"

    # Combine path
    output_path = os.path.join(dir_path, new_name) if dir_path else new_name
    
    print(f"正在保存字体...")
    font.save(output_path)
    return output_path

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python weight_font.py <字体文件.ttf> <字重系数>")
        sys.exit(1)
        
    font_path = sys.argv[1]
    weight_factor = float(sys.argv[2])
    output = add_weight(font_path, weight_factor)
    print(f"已保存修改后的字体: {output}")