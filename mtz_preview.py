import os
import sys
import tempfile
import atexit
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont, TTCollection

# Cache already-extracted subfonts so we don't extract multiple times
_extracted_paths = {}

def cleanup_temp_files():
    """Delete all temporary extracted font files."""
    for path in _extracted_paths.values():
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            print(f"Warning: Failed to delete temp file {path}: {e}")
    _extracted_paths.clear()

# Register cleanup function to run on exit
atexit.register(cleanup_temp_files)

def _extract_subfont_if_ttc(font_path, subfont_index=0):
    """
    If font_path is a TTC, extract the subfont at subfont_index
    to a temporary TTF file, returning its path. Otherwise return font_path.
    """
    # Check cache
    cache_key = (font_path, subfont_index)
    if cache_key in _extracted_paths:
        return _extracted_paths[cache_key]

    with open(font_path, 'rb') as f:
        signature = f.read(4)
    if signature == b'ttcf':
        ttc = TTCollection(font_path)
        if subfont_index < 0 or subfont_index >= len(ttc.fonts):
            raise ValueError(f"Subfont index {subfont_index} out of range.")
        tf = tempfile.NamedTemporaryFile(suffix=".ttf", delete=False)
        ttc.fonts[subfont_index].save(tf.name)
        tf.close()
        _extracted_paths[cache_key] = tf.name
        return tf.name
    # Not TTC, return original
    return font_path

def get_full_font_name(font_path, subfont_index=0):
    extracted_path = _extract_subfont_if_ttc(font_path, subfont_index)
    tt = TTFont(extracted_path)
    full_name = os.path.basename(font_path)
    if 'name' in tt:
        for record in tt['name'].names:
            if record.nameID == 4:
                try:
                    return record.toUnicode()
                except:
                    pass
    return full_name

def create_preview(font_path, output_file="preview_fonts_0.jpg", subfont_index=0):
    with open("preview.txt", "r", encoding='utf-8') as f:
        sample_text = f.read().strip()
    extracted_path = _extract_subfont_if_ttc(font_path, subfont_index)
    img = Image.new('RGB', (1080, 2340), 'white')
    draw = ImageDraw.Draw(img)
    title = get_full_font_name(font_path, subfont_index)
    title_font = ImageFont.truetype(extracted_path, 60)
    draw.text((40, 40), title, fill='black', font=title_font)

    y = 140
    for size in [18, 24, 36, 48, 60, 72]:
        try:
            label_font = ImageFont.truetype(extracted_path, 32)
            draw.text((40, y), f"{size}pt", fill='black', font=label_font)
            body_font = ImageFont.truetype(extracted_path, size)
            bbox = draw.textbbox((0, 0), sample_text, font=body_font)
            text_height = bbox[3] - bbox[1]
            draw.text((160, y), sample_text, fill='black', font=body_font)
            y += max(text_height + 40, size + 40)
        except Exception as e:
            print(f"Error drawing size {size}pt: {e}")

    img.save(output_file, quality=95)
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mtz_preview.py <font_path> [subfont_index]")
        sys.exit(1)
    font_file = sys.argv[1]
    index = 0
    if len(sys.argv) > 2:
        index = int(sys.argv[2])
    out = create_preview(font_file, subfont_index=index)
    print(f"Generated preview: {out}")