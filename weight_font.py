from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
import os
import sys

def fake_bold_glyph(glyph, glyfTable, weight_factor):
    """Approximate 'bold' by shifting each point horizontally away from the center."""
    coords = glyph.coordinates
    if len(coords) == 0 or glyph.numberOfContours <= 0:
        return glyph

    # Compute original bounding box
    xmin = min(x for x, y in coords)
    xmax = max(x for x, y in coords)
    ymin = min(y for x, y in coords)
    ymax = max(y for x, y in coords)

    if xmax <= xmin:
        return glyph  # Avoid dividing by zero if glyph is degenerate

    # Horizontal center
    x_center = (xmax + xmin) / 2.0

    # Calculate how far we push each coordinate horizontally
    # For example, if weight_factor=1.2 => push points 20% further from center.
    # Then clamp each point to remain within [xmin, xmax].
    new_coords = []
    for (x, y) in coords:
        offset = x - x_center
        # Scale offset horizontally
        offset *= weight_factor
        nx = x_center + offset
        # Clamp to keep bounding box the same
        if nx < xmin:
            nx = xmin
        elif nx > xmax:
            nx = xmax
        new_coords.append((nx, y))

    # Build a new glyph from these adjusted coordinates
    # We copy over contours/endpoints from the original glyph, just altering coords
    pen = TTGlyphPen(None)
    contours = glyph.endPtsOfContours
    # 'contours' is a list of endpoint indices. We'll replicate the moves in order.
    current_point_index = 0

    for end_index in contours:
        pen.moveTo(new_coords[current_point_index])
        current_point_index += 1
        while current_point_index <= end_index:
            pen.lineTo(new_coords[current_point_index])
            current_point_index += 1
        pen.closePath()

    # Return the newly built glyph
    return pen.glyph()

def make_font_bolder(font_path, weight_factor):
    """
    Naive approach:
    - For each glyph, shift points horizontally out from center by weight_factor.
    - Clamp bounding box so it matches the original xmin/xmax.
    - The shape is “thicker” in the middle but doesn’t exceed original width.
    """
    font = TTFont(font_path)
    glyf = font["glyf"]
    hmtx = font["hmtx"].metrics

    glyph_names = font.getGlyphOrder()
    print(f"开始处理 {len(glyph_names)} 个字形...")

    for glyph_name in glyph_names:
        old_glyph = glyf[glyph_name]
        if old_glyph.numberOfContours <= 0:
            continue

        new_glyph = fake_bold_glyph(old_glyph, glyf, weight_factor)
        glyf[glyph_name] = new_glyph

        # Keep original advance width (optionally adjust LSB)
        if glyph_name in hmtx:
            width, lsb = hmtx[glyph_name]
            # Example LSB tweak: shrink side-bearing slightly
            # new_lsb = int(lsb - width*(weight_factor-1)*0.05)
            # hmtx[glyph_name] = (width, new_lsb)
            hmtx[glyph_name] = (width, lsb)

    # Optionally update OS/2 weight class
    if "OS/2" in font:
        os2 = font["OS/2"]
        new_weight = max(100, min(1000, int(os2.usWeightClass * weight_factor)))
        os2.usWeightClass = new_weight

    # Save the new font
    base_dir = os.path.dirname(font_path)
    base_name = os.path.basename(font_path)
    new_name = f"修改字重w{int(weight_factor*100)}_{base_name}"
    output_path = os.path.join(base_dir, new_name) if base_dir else new_name
    font.save(output_path)
    print(f"已生成伪加粗字体: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python weight_font.py <字体文件.ttf> <字重系数(>1的浮点数)>")
        sys.exit(1)

    input_font = sys.argv[1]
    factor = float(sys.argv[2])
    make_font_bolder(input_font, factor)