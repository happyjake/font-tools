from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import sys
import os

def get_full_font_name(font_path):
    """Retrieve the font's Full Name; fallback to file name if not found."""
    tt = TTFont(font_path)
    full_name = os.path.basename(font_path)
    if 'name' in tt:
        for record in tt['name'].names:
            if record.nameID == 4:
                try:
                    full_name = record.toUnicode()
                    break
                except:
                    pass
    return full_name

def verify_font_support(font_path, text):
    """Verify font supports all characters in text"""
    tt = TTFont(font_path)
    cmap = tt.getBestCmap()
    unsupported = []
    
    for char in text:
        if ord(char) not in cmap:
            unsupported.append(char)
    return unsupported

def create_preview(font_path, output_file="preview_fonts_0.jpg"):
    WIDTH, HEIGHT = 1080, 2340
    PADDING = 40
    TEXT_WIDTH = WIDTH - PADDING * 4  # Leave space for size labels
    
    sizes = [18,24,36,48,60,72]
    
    with open("preview.txt", "r", encoding='utf-8') as file:
        SAMPLE_TEXT = file.read().strip()
        
    img = Image.new('RGB', (WIDTH, HEIGHT), 'white')
    draw = ImageDraw.Draw(img)
    font_name = get_full_font_name(font_path)

    # Draw title
    title_font = ImageFont.truetype(font_path, 60)
    draw.text((PADDING, PADDING), font_name, fill='black', font=title_font)

    y = PADDING + 100

    # Draw samples in different sizes
    for size in sizes:
        try:
            font = ImageFont.truetype(font_path, size)
            
            # Draw size label
            label_font = ImageFont.truetype(font_path, 32)
            draw.text((PADDING, y), f"{size}pt", fill='black', font=label_font)
            
            # Calculate text bbox for this size
            bbox = draw.textbbox((0, 0), SAMPLE_TEXT, font=font)
            text_height = bbox[3] - bbox[1]
            
            # Draw sample text with proper spacing
            draw.text((PADDING + 120, y), SAMPLE_TEXT, fill='black', font=font)
            
            # Move to next position with padding based on text height
            y += max(text_height + PADDING, size + PADDING)

        except Exception as e:
            print(f"Error drawing size {size}pt: {e}")

    img.save(output_file, quality=95)
    return output_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mtz_preview.py <font_path>")
        sys.exit(1)

    output = create_preview(sys.argv[1])
    print(f"Generated preview: {output}")