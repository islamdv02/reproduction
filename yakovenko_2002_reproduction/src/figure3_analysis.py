"""
Figure 3 Analysis: 27-Muscle Hindlimb EMG Chart in the Step Cycle.
Faithfully reproduces Figure 3 from Yakovenko et al. (J Neurophysiol 2002).
"""

import os
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
from emg_profiles import build_all_emg_profiles

# Literature references annotated in Figure 3
EMG_REFERENCES = {
    'AdFM': '2, 8, 18, 22',
    'BFa': '3, 5, 18, 22, 25',
    'CF': '18, 22',
    'FDL_ext': '2, 6, 7, 9, 22',
    'FHL': '1, 2, 22, 24, 25',
    'GlutMax': '2, 4, 22',
    'GlutMed': '2, 4, 22',
    'LG': '1, 2, 3, 4, 8, 9, 12,\n20, 21, 22, 24, 26',
    'MG': '1, 2, 3, 4, 8, 9, 12,\n20, 21, 22, 24, 26',
    'Plantaris': '1, 22, 24, 25',
    'SMa': '6, 7, 18, 24',
    'Soleus': '1, 5, 6, 22, 25',
    'TP': '1',
    'VI': '14, 15, 16, 22',
    'VL': '2, 3, 4, 6, 7, 9, 10, 11, 12,\n14, 15, 22, 23, 24, 26',
    'VM': '14, 15, 16, 21',
    'EDL': '1, 2, 7, 22, 24, 25',
    'Iliacus': '2, 3, 4, 8, 9, 10, 12, 22, 24',
    'Psoas': '2, 3, 4, 8, 9, 10, 12, 22, 24',
    'RF': '8, 14, 15,\n16, 22, 24',
    'SRTa': '2, 4, 9, 10, 12, 13, 14, 15, 16, 22',
    'SRTm': '2, 4, 6, 9, 10, 12,\n13, 14, 15, 16, 22',
    'TA': '1, 2, 3, 5, 6, 7, 9, 10,\n11, 22, 24, 25, 26',
    'BFp': '1, 5, 18, 19, 20, 21, 25',
    'FDL_ret': '1, 17, 24, 25',
    'Gracilis': '18, 22',
    'ST': '6, 8, 18',
    'SMp': '3, 5, 6, 7, 8, 9, 10,\n18, 22, 23, 24, 26'
}


def generate_figure3_complete(output_dir: str = "plots") -> str:
    """Generates the master composite Figure 3 publication layout matching the paper."""
    os.makedirs(output_dir, exist_ok=True)
    profiles_ret = build_all_emg_profiles(fdl_as_retractor=True)
    profiles_ext = build_all_emg_profiles(fdl_as_retractor=False)

    t = np.linspace(0, 100, 100, endpoint=False)

    extensor_list = ['AdFM', 'BFa', 'CF', 'FDL', 'FHL', 'GlutMax', 'GlutMed', 'LG', 'MG', 'Plantaris', 'SMa', 'Soleus', 'TP', 'VI', 'VL', 'VM']
    flexor_list = ['EDL', 'Iliacus', 'Psoas', 'RF', 'SRTa', 'SRTm', 'TA']
    retractor_list = ['BFp', 'FDL', 'Gracilis', 'ST', 'SMp']

    fig = plt.figure(figsize=(12, 16), dpi=300)
    fig.suptitle("Figure 3: EMG Patterns of Hindlimb Muscles During Forward Level Locomotion",
                 fontsize=12, fontweight='bold', y=0.99)

    # We create two main columns: Left = Extensors (16 rows), Right = Flexors (7 rows) + Retractors (5 rows)
    # Left column: Extensors
    n_ext = len(extensor_list)
    for i, m in enumerate(extensor_list):
        ax = fig.add_subplot(n_ext, 2, 2 * i + 1)
        if m == 'FDL':
            ax.plot(t, profiles_ext['FDL'], '--', color='black', linewidth=1.5, label='extensor')
            ref_str = EMG_REFERENCES['FDL_ext']
        else:
            ax.plot(t, profiles_ext[m], '-', color='black', linewidth=1.5)
            ref_str = EMG_REFERENCES.get(m, '')

        ax.set_xlim(0, 100)
        ax.set_ylim(-5, 115)
        ax.axvline(30, color='#888888', linestyle=':', linewidth=0.8) # Swing-stance transition

        # Labels
        ax.set_ylabel(m, fontsize=8.5, fontweight='bold', rotation=0, labelpad=28, va='center')
        ax.text(102, 50, ref_str, fontsize=6, va='center', ha='left', color='#444444')

        if i == 0:
            ax.set_title("EXTENSORS", fontsize=10, fontweight='bold', pad=15)
            # Add swing/stance icons/text at top
            ax.text(15, 125, "swing", ha='center', fontsize=8, style='italic')
            ax.text(65, 125, "stance", ha='center', fontsize=8, style='italic')

        if i < n_ext - 1:
            ax.set_xticks([])
            ax.spines['bottom'].set_visible(False)
        else:
            ax.set_xlabel("step cycle, %", fontsize=9)
            ax.set_xticks([0, 50, 100])

        ax.set_yticks([0, 100])
        ax.tick_params(labelsize=7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Right column: Flexors (rows 0..6) + Retractors (rows 8..12)
    # Flexors
    for i, m in enumerate(flexor_list):
        ax = fig.add_subplot(n_ext, 2, 2 * i + 2)
        ax.plot(t, profiles_ret[m], '-', color='black', linewidth=1.5)
        ref_str = EMG_REFERENCES.get(m, '')

        ax.set_xlim(0, 100)
        ax.set_ylim(-5, 115)
        ax.axvline(30, color='#888888', linestyle=':', linewidth=0.8)

        ax.set_ylabel(m, fontsize=8.5, fontweight='bold', rotation=0, labelpad=28, va='center')
        ax.text(102, 50, ref_str, fontsize=6, va='center', ha='left', color='#444444')

        if i == 0:
            ax.set_title("FLEXORS", fontsize=10, fontweight='bold', pad=15)
            ax.text(15, 125, "swing", ha='center', fontsize=8, style='italic')
            ax.text(65, 125, "stance", ha='center', fontsize=8, style='italic')

        if i < len(flexor_list) - 1:
            ax.set_xticks([])
            ax.spines['bottom'].set_visible(False)
        else:
            ax.set_xticks([0, 50, 100])
            ax.set_xticklabels([])

        ax.set_yticks([0, 100])
        ax.tick_params(labelsize=7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Retractors (rows 10..14)
    start_row = 10
    for i, m in enumerate(retractor_list):
        row_idx = start_row + i
        ax = fig.add_subplot(n_ext, 2, 2 * row_idx + 2)
        if m == 'FDL':
            ax.plot(t, profiles_ret['FDL'], '--', color='black', linewidth=1.5)
            ref_str = EMG_REFERENCES['FDL_ret']
        else:
            ax.plot(t, profiles_ret[m], '-', color='black', linewidth=1.5)
            ref_str = EMG_REFERENCES.get(m, '')

        ax.set_xlim(0, 100)
        ax.set_ylim(-5, 115)
        ax.axvline(30, color='#888888', linestyle=':', linewidth=0.8)

        ax.set_ylabel(m, fontsize=8.5, fontweight='bold', rotation=0, labelpad=28, va='center')
        ax.text(102, 50, ref_str, fontsize=6, va='center', ha='left', color='#444444')

        if i == 0:
            ax.text(50, 130, "RETRACTORS", fontsize=10, fontweight='bold', ha='center')

        if i < len(retractor_list) - 1:
            ax.set_xticks([])
            ax.spines['bottom'].set_visible(False)
        else:
            ax.set_xlabel("step cycle, %", fontsize=9)
            ax.set_xticks([0, 50, 100])

        ax.set_yticks([0, 100])
        ax.tick_params(labelsize=7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.tight_layout(rect=[0, 0.02, 0.95, 0.97])
    out_path = os.path.join(output_dir, "figure3_emg_profiles.png")
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out_path
