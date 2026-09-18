import os
from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    canvas_size = 512
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Pitch-Black Matte Squircle
    bg_rect = [16, 16, 496, 496]
    corner_radius = 90
    draw.rounded_rectangle(
        bg_rect, 
        radius=corner_radius, 
        fill=(0, 0, 0, 255),       # Pitch Black #000000
        outline=(35, 35, 35, 255),  # Subtle dark border for edge definition
        width=2
    )

    # 2. Minimalist Bold Aperture Reticle
    center_x = 256
    center_y = 195

    # Heavy outer ring
    r_outer = 72
    draw.ellipse(
        [center_x - r_outer, center_y - r_outer, center_x + r_outer, center_y + r_outer],
        outline=(0, 240, 255, 255),
        width=7  # Thick, bold stroke
    )

    # Center solid pupil
    r_core = 20
    draw.ellipse(
        [center_x - r_core, center_y - r_core, center_x + r_core, center_y + r_core],
        fill=(255, 255, 255, 255)
    )

    # Tactical corner brackets around the glyph
    bracket_offset = 96
    bracket_len = 18
    bracket_color = (0, 240, 255, 180)
    b_width = 4

    # Top-Left
    draw.line([(center_x - bracket_offset, center_y - bracket_offset), (center_x - bracket_offset + bracket_len, center_y - bracket_offset)], fill=bracket_color, width=b_width)
    draw.line([(center_x - bracket_offset, center_y - bracket_offset), (center_x - bracket_offset, center_y - bracket_offset + bracket_len)], fill=bracket_color, width=b_width)
    # Top-Right
    draw.line([(center_x + bracket_offset, center_y - bracket_offset), (center_x + bracket_offset - bracket_len, center_y - bracket_offset)], fill=bracket_color, width=b_width)
    draw.line([(center_x + bracket_offset, center_y - bracket_offset), (center_x + bracket_offset, center_y - bracket_offset + bracket_len)], fill=bracket_color, width=b_width)
    # Bottom-Left
    draw.line([(center_x - bracket_offset, center_y + bracket_offset), (center_x - bracket_offset + bracket_len, center_y + bracket_offset)], fill=bracket_color, width=b_width)
    draw.line([(center_x - bracket_offset, center_y + bracket_offset), (center_x - bracket_offset, center_y + bracket_offset - bracket_len)], fill=bracket_color, width=b_width)
    # Bottom-Right
    draw.line([(center_x + bracket_offset, center_y + bracket_offset), (center_x + bracket_offset - bracket_len, center_y + bracket_offset)], fill=bracket_color, width=b_width)
    draw.line([(center_x + bracket_offset, center_y + bracket_offset), (center_x + bracket_offset, center_y + bracket_offset - bracket_len)], fill=bracket_color, width=b_width)

    # 3. Bold Monospace "IRIS"
    font_candidates = [
        r"C:\Windows\Fonts\consolab.ttf",          # Consolas Bold
        r"C:\Windows\Fonts\CascadiaMono-Bold.otf", # Cascadia Mono Bold
        r"C:\Windows\Fonts\courbd.ttf",            # Courier New Bold
        r"C:\Windows\Fonts\lucon.ttf"              # Lucida Console
    ]
    
    font_path = None
    for path in font_candidates:
        if os.path.exists(path):
            font_path = path
            break

    font_size = 76
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

    label = "IRIS"
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (canvas_size - text_w) / 2
    text_y = 345

    # Multi-pass rendering to force an extra-bold weight
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            draw.text((text_x + dx, text_y + dy), label, fill=(255, 255, 255, 255), font=font)

    # Final crisp overlay
    draw.text((text_x, text_y), label, fill=(255, 255, 255, 255), font=font)

    # 4. Export
    img.save("logo.png", format="PNG")
    img.save("icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Pitch-black extra-bold logo & icon generated successfully.")

if __name__ == "__main__":
    generate_logo()