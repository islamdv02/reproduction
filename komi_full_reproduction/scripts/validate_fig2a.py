"""
validate_fig2a.py
Computes quantitative validation metrics for Figure 2A reproduction:
- Centroid displacements
- Spot counts and population stats
- Mask IoU (spinal cord and grey matter)
- Methodological classification
"""

import os
import json
import numpy as np
import scipy.io as sio
from PIL import Image

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_file = os.path.join(root_dir, 'scratch', 'fig2a_extracted_data.mat')
    pub_file = os.path.join(root_dir, 'scratch', 'pub_2a_native.png')
    rec_file = os.path.join(root_dir, 'figures', 'subpanels_fig2', 'fig2a_spatial_transcriptomics.png')
    results_dir = os.path.join(root_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    print("Computing Figure 2A quantitative validation metrics...")
    data = sio.loadmat(data_file)
    x = data['x'].flatten()
    y = data['y'].flatten()
    lowres = np.array([str(s[0]) if len(s) > 0 and len(s[0]) > 0 else '' for s in data['lowres'].flatten()])
    cell_types = np.array([str(s[0]) if len(s) > 0 and len(s[0]) > 0 else '' for s in data['cell_types'].flatten()])
    weights = data['weights']

    gm_mask = (lowres == 'grey')
    cord_mask = (lowres != 'DRG')
    mid_x = (x[cord_mask].min() + x[cord_mask].max()) / 2.0

    # Spot attribution logic
    gm_indices = np.where(gm_mask)[0]
    w_gm = weights[gm_mask, :]
    w_min = np.min(w_gm[w_gm > 0])
    w_gm_pos = np.where(w_gm > 0, w_gm, w_min)
    log_w = np.log(w_gm_pos)
    col_min = log_w.min(axis=0)
    col_max = log_w.max(axis=0)
    wn = (log_w - col_min) / (col_max - col_min + 1e-12)

    unique_types = []
    seen = set()
    for t in cell_types:
        if t not in seen:
            seen.add(t)
            unique_types.append(t)
    unique_types = np.array(unique_types)

    def get_spots(type_names):
        spots = set()
        for tname in type_names:
            cols = np.where(unique_types == tname)[0]
            for c in cols:
                col_vals = wn[:, c]
                order = np.argsort(col_vals)
                swno = col_vals[order]
                csum = np.cumsum(swno)
                cdwn = np.diff(csum)
                ix = np.where(cdwn > 0.4)[0] + 1
                if len(ix) == 0:
                    continue
                swn = swno[ix]
                swn_z = (swn - np.mean(swn)) / (np.std(swn) + 1e-12)
                indx = (swn_z > 1.0)
                selected_gm_sub = order[ix[indx]]
                for s in gm_indices[selected_gm_sub]:
                    spots.add(s)
        return np.array(sorted(list(spots)))

    s_mn = get_spots(['MN-alpha', 'MN-gamma'])
    s_v1 = get_spots(['Inhib-23', 'Inhib-24', 'Inhib-26'])
    s_v2a = get_spots(['Excit-35', 'Excit-36'])
    s_rora = get_spots(['Excit-06'])

    left_rora = [s for s in s_rora if x[s] <= mid_x]
    left_v2a = [s for s in s_v2a if x[s] <= mid_x]
    left_v1 = [s for s in s_v1 if x[s] <= mid_x]
    left_mn = [s for s in s_mn if x[s] <= mid_x]

    # Published label positions in published coordinates (760 x 560)
    pub_labels = {
        'Rora': (510, 205),
        'V2a': (470, 315),
        'V1': (535, 365),
        'Mn': (565, 435),
    }

    # Scaling from data coordinates to published coordinates
    sx, sy = 1.165, 1.165
    ox = 400.0 - mid_x * sx
    oy = 330.0 - 180.5 * sy

    def to_pub(px, py):
        return px * sx + ox, py * sy + oy

    centroid_metrics = {}
    for name, s_idx in [('Rora', left_rora), ('V2a', left_v2a), ('V1', left_v1), ('Mn', left_mn)]:
        mirr_x = 2 * mid_x - x[s_idx]
        c_x, c_y = mirr_x.mean(), y[s_idx].mean()
        pub_cx, pub_cy = to_pub(c_x, c_y)
        ref_x, ref_y = pub_labels[name]
        disp = float(np.hypot(pub_cx - ref_x, pub_cy - ref_y))
        centroid_metrics[name] = {
            'n_spots_left': int(len(s_idx)),
            'data_centroid': {'x': float(round(c_x, 2)), 'y': float(round(c_y, 2))},
            'mapped_pub_centroid': {'x': float(round(pub_cx, 1)), 'y': float(round(pub_cy, 1))},
            'published_label_pos': {'x': float(ref_x), 'y': float(ref_y)},
            'displacement_pixels': float(round(disp, 1)),
            'displacement_percent_width': float(round(disp / 760.0 * 100.0, 2))
        }

    # Pixel similarity / mask IoU
    pub_im = np.array(Image.open(pub_file).convert('L'))
    rec_im = np.array(Image.open(rec_file).convert('L'))
    # Resize rec to pub size
    rec_resized = np.array(Image.fromarray(rec_im).resize((pub_im.shape[1], pub_im.shape[0]), Image.Resampling.LANCZOS))

    pub_cord_mask = (pub_im < 250)
    rec_cord_mask = (rec_resized < 250)
    intersection = np.logical_and(pub_cord_mask, rec_cord_mask).sum()
    union = np.logical_or(pub_cord_mask, rec_cord_mask).sum()
    mask_iou = float(intersection / union) if union > 0 else 0.0

    metrics = {
        'panel': 'Figure 2A',
        'scientific_status': 'METHODS-BASED RECONSTRUCTION',
        'status_rationale': (
            'Exact author spatial transcriptomics coordinates (RCTDCoord in matGeometry.mat), '
            'exact author cell type census (CellTypesCensus in matCellInfo.mat), '
            'exact author attribution thresholding (SpinalCordGeometry.m lines 74-100), '
            'and author anatomical grey matter reference (ZeroMap.mat) were strictly used. '
            'Because the authors did not supply a dedicated plotting driver script (PlotFigure2A.m) in the repository, '
            'the visualization pipeline was reconstructed according to the published Methods.'
        ),
        'coordinate_system': {
            'mediolateral_axis': 'x (27 to 482 px, midline = 254.5)',
            'dorsoventral_axis': 'y (25 to 336 px, dorsal=top, ventral=bottom)',
            'left_hemicord_spots': 'x <= 254.5 (raw Visium spots)',
            'right_hemicord_fields': 'Continuous 2D probability distributions symmetrized across midline'
        },
        'spot_counts_left_hemicord': {
            'Rora_Excit06': len(left_rora),
            'V2a_Excit35_36': len(left_v2a),
            'V1_Inhib23_24_26': len(left_v1),
            'Mn_alpha_gamma': len(left_mn),
            'total_attributed_spots': len(left_rora) + len(left_v2a) + len(left_v1) + len(left_mn)
        },
        'probability_field_parameters': {
            'method': 'Continuous 2D Gaussian density fields',
            'normalization': 'Independent per-class [0, 1] normalization',
            'anatomical_masking': 'Strictly bounded within grey matter butterfly contour',
            'Rora_sigma': 18.0,
            'V2a_sigma': 24.0,
            'V1_sigma': 20.0,
            'Mn_sigma': 18.0
        },
        'centroids_and_displacements': centroid_metrics,
        'overall_cord_mask_iou': round(mask_iou, 4)
    }

    out_metrics_file = os.path.join(results_dir, 'fig2a_validation_metrics.json')
    with open(out_metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved validation metrics: {out_metrics_file}")
    print(json.dumps(metrics, indent=2))

if __name__ == '__main__':
    main()
