#!/usr/bin/env python3
"""
Generate a simple token icon for Moltiverse Zoo
"""
from PIL import Image, ImageDraw, ImageFont
import sys

def create_token_icon(output_path="zoo_token.png", size=512):
    """Create a colorful token icon with ZOO text."""
    
    # Create image with gradient background
    img = Image.new('RGB', (size, size), color='#0a0f0b')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient circle background
    center = size // 2
    radius = size // 2 - 20
    
    # Create circular gradient
    for r in range(radius, 0, -2):
        # Color gradient from teal to green
        ratio = r / radius
        color_r = int(10 + (137 - 10) * (1 - ratio))
        color_g = int(15 + (240 - 15) * (1 - ratio))
        color_b = int(11 + (197 - 11) * (1 - ratio))
        
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(color_r, color_g, color_b)
        )
    
    # Draw outer ring
    ring_width = 15
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        outline=(137, 240, 197),
        width=ring_width
    )
    
    # Draw inner decorative circles
    for angle in [0, 90, 180, 270]:
        import math
        x = center + int(radius * 0.6 * math.cos(math.radians(angle)))
        y = center + int(radius * 0.6 * math.sin(math.radians(angle)))
        mini_r = 25
        draw.ellipse(
            [x - mini_r, y - mini_r, x + mini_r, y + mini_r],
            fill=(91, 167, 255, 200),
            outline=(137, 240, 197),
            width=3
        )
    
    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 140)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 140)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Draw "ZOO" text
    text = "ZOO"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 20
    
    # Draw text shadow
    draw.text((text_x + 3, text_y + 3), text, fill=(0, 0, 0, 180), font=font)
    # Draw main text
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
    
    # Draw emoji/icon at top
    emoji = "🦞"
    emoji_bbox = draw.textbbox((0, 0), emoji, font=font_small)
    emoji_width = emoji_bbox[2] - emoji_bbox[0]
    emoji_x = (size - emoji_width) // 2
    emoji_y = 60
    draw.text((emoji_x, emoji_y), emoji, font=font_small, embedded_color=True)
    
    # Save with proper format for web upload
    # Optimize for web and ensure compatibility
    img = img.convert('RGB')  # Ensure RGB mode
    img.save(output_path, 'PNG', optimize=True, quality=95)
    print(f"✓ Token icon created: {output_path}")
    print(f"  Size: {size}x{size}px")
    print(f"  Format: PNG (RGB)")
    return output_path

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "zoo_token.png"
    create_token_icon(output)
