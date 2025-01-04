from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.misc.transform import Identity

def add_weight(font_path, weight_factor=1.2):
    """Add weight to font by scaling glyphs horizontally"""
    
    font = TTFont(font_path)
    glyf = font['glyf']
    
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if glyph.numberOfContours > 0:  # Skip empty glyphs
            # Create pens for transformation
            pen = TTGlyphPen(None)
            transform = Identity.scale(weight_factor, 1)
            transform_pen = TransformPen(pen, transform)
            
            # Draw glyph through transform
            glyph.draw(transform_pen)
            
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
    output_path = font_path.replace('.ttf', f'_w{int(weight_factor*100)}.ttf')
    font.save(output_path)
    return output_path

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python add_weight.py <font.ttf> <weight_factor>")
        sys.exit(1)
        
    font_path = sys.argv[1]
    weight_factor = float(sys.argv[2])
    output = add_weight(font_path, weight_factor)
    print(f"Saved weighted font to: {output}")