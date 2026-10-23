"""
surgical_replace_fig2e_2g.py
Surgically replaces ONLY Panels 2E and 2G in figures/main_figures/Figure2.png.
Verifies via SHA-256 hashes that Panels 2A, 2B, 2C, 2D, and 2F are 100% bit-identical.
Confirms Figure3.png is completely untouched.
"""

import os
import hashlib
import numpy as np
from PIL import Image

def compute_region_hash(img, box):
    # box is (x1, y1, x2, y2)
    crop = img.crop(box)
    data = np.array(crop).tobytes()
    return hashlib.sha256(data).hexdigest()

def compute_file_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def load_and_fit(subpanel_path, target_w, target_h):
    im = Image.open(subpanel_path).convert('RGBA')
    
    # Crop excessive white borders
    diff = Image.fromarray(((255 - np.array(im.convert('L'))) > 5).astype('uint8') * 255)
    bbox = diff.getbbox()
    if bbox:
        im = im.crop((max(0, bbox[0]-10), max(0, bbox[1]-10), min(im.width, bbox[2]+10), min(im.height, bbox[3]+10)))
    
    im.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    
    res = Image.new('RGB', (target_w, target_h), 'white')
    offset_x = (target_w - im.width) // 2
    offset_y = (target_h - im.height) // 2
    res.paste(im, (offset_x, offset_y), im)
    return res

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    fig2_path = os.path.join(root_dir, 'figures', 'main_figures', 'Figure2.png')
    fig3_path = os.path.join(root_dir, 'figures', 'main_figures', 'Figure3.png')
    sub_dir = os.path.join(root_dir, 'figures', 'subpanels_fig2')

    # Confirm initial hashes
    fig3_hash_pre = compute_file_hash(fig3_path)
    print(f"Figure3.png pre-hash: {fig3_hash_pre}")

    fig2_orig = Image.open(fig2_path)
    W, H = fig2_orig.size
    print(f"Figure2.png dimensions: {W} x {H}")

    # Bounding boxes for preserved panels (matching build_figure2_composite.py layout)
    # A: (40, 40, 1250, 1100)
    # B: (1240, 40, 4100, 1100)
    # C: (40, 1120, 2850, 2200)
    # D: (2840, 1120, 4100, 2200)
    # F: (1340, 2220, 2650, 3580)
    preserved_boxes = {
        '2A': (40, 40, 1250, 1100),
        '2B': (1240, 40, 4100, 1100),
        '2C': (40, 1120, 2850, 2200),
        '2D': (2840, 1120, 4100, 2200),
        '2F': (1344, 2220, 2640, 3580),
    }

    hashes_pre = {k: compute_region_hash(fig2_orig, box) for k, box in preserved_boxes.items()}
    print("\nPre-replacement SHA-256 hashes of preserved panels:")
    for k, h in hashes_pre.items():
        print(f"  Panel {k}: {h}")

    # Prepare corrected subpanels
    # 2E: target (1240, 1340) at (100, 2240) - terminates before x=1344 (F label)
    # 2G: target (1420, 1340) at (2680, 2240)
    im_2e = load_and_fit(os.path.join(sub_dir, 'fig2e_connectivity_matrix.png'), 1240, 1340)
    im_2g = load_and_fit(os.path.join(sub_dir, 'fig2g_net_projectome.png'), 1420, 1340)

    # Perform surgical replacement on a copy of Figure2
    fig2_updated = fig2_orig.copy()
    fig2_updated.paste(im_2e, (100, 2240))
    fig2_updated.paste(im_2g, (2680, 2240))

    # Verify hashes post-replacement BEFORE saving
    hashes_post = {k: compute_region_hash(fig2_updated, box) for k, box in preserved_boxes.items()}
    print("\nPost-replacement SHA-256 hashes of preserved panels:")
    all_match = True
    for k, h in hashes_post.items():
        match = (h == hashes_pre[k])
        status = "MATCH (BIT-IDENTICAL)" if match else "MISMATCH (FAILED)"
        print(f"  Panel {k}: {h} -> {status}")
        if not match:
            all_match = False

    if not all_match:
        raise RuntimeError("Assertion failed: Preserved panel hashes do not match pre-replacement hashes!")

    # Save updated Figure2.png
    fig2_updated.save(fig2_path, 'PNG', quality=95)
    print(f"\nSuccessfully saved surgically updated Figure2.png: {fig2_path}")

    # Confirm file on disk
    fig2_disk = Image.open(fig2_path)
    hashes_disk = {k: compute_region_hash(fig2_disk, box) for k, box in preserved_boxes.items()}
    for k, h in hashes_disk.items():
        assert h == hashes_pre[k], f"Disk check failed for Panel {k}"
    print("Disk verification passed: All preserved panels 2A-2D and 2F are 100% bit-identical.")

    # Confirm Figure3.png was not touched
    fig3_hash_post = compute_file_hash(fig3_path)
    assert fig3_hash_post == fig3_hash_pre, "CRITICAL ERROR: Figure3.png was modified!"
    print(f"Figure3.png integrity verified: {fig3_hash_post} (UNTOUCHED)")

if __name__ == '__main__':
    main()
