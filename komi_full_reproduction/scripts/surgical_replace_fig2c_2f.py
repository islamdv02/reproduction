"""
surgical_replace_fig2c_2f.py
Surgically replaces ONLY Panels 2C and 2F in figures/main_figures/Figure2.png.
Verifies via SHA-256 hashes that Panels 2A, 2B, 2D, 2E, and 2G are 100% bit-identical.
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

    # Confirm initial Figure 3 hash
    fig3_hash_pre = compute_file_hash(fig3_path)
    print(f"Figure3.png pre-hash: {fig3_hash_pre}")

    fig2_orig = Image.open(fig2_path)
    W, H = fig2_orig.size
    print(f"Figure2.png dimensions: {W} x {H}")

    # Preserved panel boxes (strictly non-overlapping with 2C and 2F):
    # 2A: (40, 40, 1250, 1100)
    # 2B: (1240, 40, 4100, 1100)
    # 2D: (2840, 1120, 4100, 2200)
    # 2E: (40, 2220, 1340, 3580)
    # 2G: (2640, 2220, 4100, 3580)
    preserved_boxes = {
        '2A': (40, 40, 1250, 1100),
        '2B': (1240, 40, 4100, 1100),
        '2D': (2840, 1120, 4100, 2200),
        '2E': (40, 2220, 1340, 3580),
        '2G': (2640, 2220, 4100, 3580),
    }

    hashes_pre = {k: compute_region_hash(fig2_orig, box) for k, box in preserved_boxes.items()}
    print("\nPre-replacement SHA-256 hashes of preserved panels:")
    for k, h in hashes_pre.items():
        print(f"  Panel {k}: {h}")

    # Prepare corrected subpanels
    # 2C: target box (2740, 1060) placed at (100, 1140) -> ends at x=2840 (before 2D at 2840), y=2200
    # 2F: target box (1260, 1340) placed at (1380, 2240) -> ends at x=2640 (before 2G at 2640), y=3580
    im_2c = load_and_fit(os.path.join(sub_dir, 'fig2c_directional_kernels.png'), 2740, 1060)
    im_2f = load_and_fit(os.path.join(sub_dir, 'fig2f_celltype_matrix.png'), 1260, 1340)

    # Perform surgical replacement on a copy of Figure2
    fig2_updated = fig2_orig.copy()
    fig2_updated.paste(im_2c, (100, 1140))
    fig2_updated.paste(im_2f, (1380, 2240))

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
    print("Disk verification passed: All preserved panels 2A, 2B, 2D, 2E, and 2G are 100% bit-identical.")

    # Confirm Figure 3 hash
    fig3_hash_post = compute_file_hash(fig3_path)
    assert fig3_hash_post == fig3_hash_pre, "Figure3.png was modified!"
    print(f"Figure3.png post-hash: {fig3_hash_post} (100% byte-identical)")

if __name__ == '__main__':
    main()
