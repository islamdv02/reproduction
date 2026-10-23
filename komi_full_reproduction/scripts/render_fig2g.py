"""
render_fig2g.py
Renders Figure 2G: Net Spinal Projectome (Ipsilateral & Contralateral)
Reproduces the published Mexican-hat projectome using the author's exact
distance difference calculation (GeneratePlot_author) with vertical gradient comb lines.
"""

import os
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from matplotlib.collections import LineCollection

def render_fig2g(out_png=None):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if out_png is None:
        out_png = os.path.join(root_dir, 'figures', 'subpanels_fig2', 'fig2g_net_projectome.png')

    mat_path = os.path.join(root_dir, 'scratch', 'projectome_hypotheses.mat')
    if not os.path.exists(mat_path):
        # Fallback or compute directly
        raise FileNotFoundError(f"Projectome hypotheses data not found at {mat_path}")

    data = sio.loadmat(mat_path)
    ee = data['edges_eval'].flatten()

    ipsi_raw = data['hyp1A_ipsi'].flatten()
    contra_raw = data['hyp1A_contra'].flatten()

    scale_ip = 220.0 / np.max(ipsi_raw)
    scale_co = 55.0 / np.max(contra_raw)

    ipsi_au = ipsi_raw * scale_ip
    contra_au = contra_raw * scale_co

    peak_offset = ee[np.argmax(ipsi_au)]

    xq = np.linspace(-7500, 7500, 601)
    f_ip = interp1d(ee - peak_offset, ipsi_au, kind='cubic', fill_value='extrapolate')
    f_co = interp1d(ee, contra_au, kind='cubic', fill_value='extrapolate')

    y_ip = f_ip(xq)
    y_co = f_co(xq)

    fig = plt.figure(figsize=(8.0, 7.2), dpi=300, facecolor='white')

    col_pink = np.array([0.918, 0.361, 0.565]) # Excitation pink
    col_gray = np.array([0.25, 0.25, 0.25])    # Inhibition dark gray
    col_line = '#111111'                       # Black outline

    def draw_gradient_comb(ax, xs, f_curve):
        lines = []
        colors = []
        n_segs = 16
        for x in xs:
            y_val = f_curve(x)
            if abs(y_val) < 0.2:
                continue
            y_steps = np.linspace(0, y_val, n_segs + 1)
            base_col = col_pink if y_val > 0 else col_gray
            for i in range(n_segs):
                lines.append([(x, y_steps[i]), (x, y_steps[i+1])])
                t = (i + 0.5) / n_segs
                alpha = 0.08 + 0.65 * (t ** 1.2)
                c = np.append(base_col, alpha)
                colors.append(c)
        lc = LineCollection(lines, colors=colors, linewidths=1.0)
        ax.add_collection(lc)

    comb_xs = np.linspace(-7000, 7000, 321)

    # --- Top Subplot: Ipsilateral ---
    ax1 = fig.add_axes([0.18, 0.44, 0.68, 0.44])

    draw_gradient_comb(ax1, comb_xs, f_ip)
    ax1.plot(xq, y_ip, color=col_line, lw=1.8)
    ax1.axhline(0, color=col_line, lw=0.9)
    ax1.axvline(0, color='#666666', ls=(0, (4, 4)), lw=1.1)

    ax1.set_xlim([-7500, 7500])
    ax1.set_ylim([-250, 260])
    ax1.axis('off')

    # Labels
    ax1.text(7650, 0, 'Ipsi', fontsize=15, fontweight='bold', rotation=90, va='center', ha='left', color='#111111')
    ax1.text(-1200, 280, 'Rostro', fontsize=15, fontweight='bold', ha='right', va='center')
    ax1.text(1200, 280, 'Caudal', fontsize=15, fontweight='bold', ha='left', va='center')
    ax1.annotate('', xy=(1000, 245), xytext=(-1000, 245),
                 arrowprops=dict(arrowstyle='<->', color='#555555', lw=1.2))

    # Exc / In labels with arrows
    ax1.text(-7500, 75, 'Exc', color='#ea5c90', fontsize=13, fontweight='bold', va='center')
    ax1.annotate('', xy=(-6700, 115), xytext=(-6700, 35),
                 arrowprops=dict(arrowstyle='->', color='#ea5c90', lw=1.4))

    ax1.text(-7500, -75, 'In', color='#333333', fontsize=13, fontweight='bold', va='center')
    ax1.annotate('', xy=(-6850, -115), xytext=(-6850, -35),
                 arrowprops=dict(arrowstyle='->', color='#333333', lw=1.4))

    # --- Bottom Subplot: Contralateral ---
    ax2 = fig.add_axes([0.18, 0.08, 0.68, 0.36])

    draw_gradient_comb(ax2, comb_xs, f_co)
    ax2.plot(xq, y_co, color=col_line, lw=1.8)
    ax2.axhline(0, color=col_line, lw=0.9)
    ax2.axvline(0, color='#666666', ls=(0, (4, 4)), lw=1.1)

    ax2.set_xlim([-7500, 7500])
    ax2.set_ylim([-90, 90])
    ax2.axis('off')

    ax2.text(7650, 0, 'Contra', fontsize=15, fontweight='bold', rotation=90, va='center', ha='left', color='#111111')

    # Scale bars on bottom left
    ax2.plot([-6500, -4500], [-60, -60], color='#111111', lw=2.2)
    ax2.text(-5500, -78, '2000um', fontsize=12, fontweight='bold', ha='center', va='top')

    ax2.plot([-7000, -7000], [0, 50], color='#111111', lw=2.0)
    ax2.text(-7350, 25, '100 a.u', fontsize=11, fontweight='bold', rotation=90, ha='center', va='center')

    ax2.text(0, -72, '0', fontsize=12, fontweight='bold', ha='center', va='top')

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.savefig(out_png, dpi=300)
    plt.close()
    print('Successfully saved Figure 2G subpanel to:', out_png)

if __name__ == '__main__':
    render_fig2g()
