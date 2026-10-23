#!/usr/bin/env python3
"""
build_figure1_composite.py
Assembles Figure1.png composite preserving the published visual layout,
with an honest, subtle status footer:
- Panels 1A-1C: PUBLISHED REFERENCE (External microscopy, Hayashi et al., 2018)
- Panels 1D-1F: CONCEPTUAL SCHEMATICS (5-Lobe Kernel Organization)
- Panels 1G-1H: REFERENCE ONLY / AUTHOR CODE UNAVAILABLE (1D continuum model unreleased in BergLab/SpinalProjectome)
"""

import os
from PIL import Image, ImageDraw, ImageFont

def build_figure1():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    pub_path = os.path.join(root_dir, 'figures', 'published_figures', 'published_figure1.jpeg')
    out_dir = os.path.join(root_dir, 'figures', 'main_figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'Figure1.png')

    if not os.path.exists(pub_path):
        raise FileNotFoundError(f"Published reference missing: {pub_path}")

    pub_img = Image.open(pub_path)
    w, h = pub_img.size

    # Subtle footer bar (36 px) preserving original paper layout
    footer_h = 36
    canvas = Image.new('RGB', (w, h + footer_h), color=(255, 255, 255))
    canvas.paste(pub_img, (0, 0))

    draw = ImageDraw.Draw(canvas)
    # Thin divider line
    draw.line([(0, h), (w, h)], fill='#CBD5E0', width=1)
    # Subtle footer background
    draw.rectangle([(0, h + 1), (w, h + footer_h)], fill='#F7FAFC')

    try:
        font_footer = ImageFont.truetype('arial.ttf', 16)
    except Exception:
        font_footer = ImageFont.load_default()

    footer_text = (
        "Figure 1 Provenance: 1A-1C: External Reference (Hayashi et al., 2018) | "
        "1D-1F: Conceptual Schematics | 1G-1H: Reference Only (1D Rate Model Unreleased in BergLab/SpinalProjectome)"
    )
    draw.text((20, h + 8), footer_text, fill='#4A5568', font=font_footer)

    canvas.save(out_path, quality=95)
    print(f"Successfully generated Figure 1 composite: {out_path} (Size: {canvas.size})")
    return out_path

if __name__ == '__main__':
    build_figure1()

