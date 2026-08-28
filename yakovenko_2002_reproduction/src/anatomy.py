"""
Anatomical Model of Cat Lumbosacral Motoneuron Pools.
Faithfully reproduces the 30-slice, 27-muscle motoneuron pool architecture from
VanderHorst & Holstege (1997) and Yakovenko et al. (J Neurophysiol 2002).
"""

import os
import json
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd

MUSCLE_NAMES = [
    # Hip Flexors
    'Psoas', 'Iliacus', 'SRTa', 'SRTm',
    # Knee Extensors
    'RF', 'VL', 'VM', 'VI',
    # Ankle Flexors
    'TA', 'EDL',
    # Hip Extensors / Adductors
    'AdFM', 'Gracilis', 'SMa', 'GlutMed', 'CF', 'BFa', 'GlutMax',
    # Retractors / Hamstrings
    'BFp', 'ST', 'SMp',
    # Ankle Extensors / Toe Flexors
    'FDL', 'FHL', 'Plantaris', 'Soleus', 'LG', 'MG', 'TP'
]

MUSCLE_CATEGORIES = {
    'Psoas': 'flexor', 'Iliacus': 'flexor', 'SRTa': 'flexor', 'SRTm': 'flexor',
    'RF': 'extensor', 'VL': 'extensor', 'VM': 'extensor', 'VI': 'extensor',
    'TA': 'flexor', 'EDL': 'flexor',
    'AdFM': 'extensor', 'Gracilis': 'retractor', 'SMa': 'extensor',
    'GlutMed': 'extensor', 'CF': 'extensor', 'BFa': 'extensor', 'GlutMax': 'extensor',
    'BFp': 'retractor', 'ST': 'retractor', 'SMp': 'retractor',
    'FDL': 'retractor', # default retractor, can be switched to extensor
    'FHL': 'extensor', 'Plantaris': 'extensor', 'Soleus': 'extensor',
    'LG': 'extensor', 'MG': 'extensor', 'TP': 'extensor'
}

JOINT_GROUPS = {
    'hip': ['Psoas', 'Iliacus', 'SRTa', 'SRTm', 'AdFM', 'Gracilis', 'SMa', 'GlutMed', 'CF', 'BFa', 'GlutMax', 'BFp', 'SMp', 'ST'],
    'knee': ['SRTm', 'VM', 'VL', 'RF', 'VI', 'SMp', 'ST', 'BFp', 'Gracilis'],
    'ankle': ['EDL', 'FDL', 'TA', 'FHL', 'TP', 'Plantaris', 'Soleus', 'LG', 'MG']
}

# Anatomical 30-slice count profiles across caudal L4 to rostral S1
# Grounded in VanderHorst & Holstege 1997 and Yakovenko 2002 Table 1 & Fig 1-2.
# Total sum strictly equals 4034 MNs (Table 1: 2366 Extensor, 907 Retractor, 761 Flexor).
RAW_SLICE_PROFILES = {
    # Flexors (Total: 761 MNs; Rostral 620 [81%], Caudal 141 [19%])
    'Psoas':    [18, 32, 40, 48, 36, 22, 12, 6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 216 MNs
    'Iliacus':  [0, 0, 0, 8, 16, 26, 34, 24, 14, 6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],    # 130 MNs
    'SRTa':     [0, 0, 0, 6, 14, 24, 30, 20, 10, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],    # 108 MNs
    'SRTm':     [0, 0, 4, 10, 18, 22, 16, 8, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],    # 80 MNs
    'TA':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 16, 30, 34, 28, 14, 6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 134 MNs (rostral 50, caudal 84)
    'EDL':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 12, 22, 26, 20, 8, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 93 MNs (rostral 36, caudal 57)

    # Retractors (Total: 907 MNs; Rostral 155 [17%], Caudal 752 [83%])
    'Gracilis': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 14, 24, 28, 26, 16, 8, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 122 MNs (rostral 70, caudal 52)
    'SMp':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 30, 34, 26, 14, 6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 122 MNs (rostral 40, caudal 82)
    'FDL':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 25, 34, 30, 20, 12, 6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 139 MNs (rostral 35, caudal 104)
    'ST':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 24, 40, 48, 42, 28, 16, 6, 2, 0, 0, 0, 0, 0, 0, 0], # 216 MNs (rostral 10, caudal 206)
    'BFp':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 18, 48, 86, 92, 48, 12], # 308 MNs (rostral 0, caudal 308, CM 25.8 mm)

    # Extensors (Total: 2366 MNs; Rostral 549 [23%], Caudal 1817 [77%])
    'RF':       [0, 0, 0, 0, 0, 0, 4, 12, 22, 34, 38, 28, 16, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 160 MNs (rostral 160)
    'VL':       [0, 0, 0, 0, 0, 0, 0, 0, 4, 14, 28, 44, 50, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 178 MNs (rostral 178)
    'VM':       [0, 0, 0, 0, 0, 0, 0, 2, 8, 18, 32, 42, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],    # 140 MNs (rostral 140)
    'VI':       [0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 18, 26, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],     # 71 MNs (rostral 71)
    'AdFM':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 14, 28, 38, 40, 30, 14, 6, 2, 0, 0, 0, 0, 0, 0],  # 176 MNs (caudal 176)
    'SMa':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 16, 28, 40, 42, 30, 14, 6, 0, 0, 0, 0, 0, 0, 0],  # 182 MNs (caudal 182)
    'GlutMed':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 14, 28, 44, 52, 40, 22, 8, 2, 0, 0, 0, 0, 0],  # 214 MNs (caudal 214)
    'CF':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 12, 22, 30, 24, 14, 6, 0, 0, 0, 0, 0, 0],    # 112 MNs (caudal 112)
    'BFa':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 16, 32, 46, 50, 34, 16, 4, 0, 0, 0, 0, 0],  # 204 MNs (caudal 204)
    'GlutMax':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 12, 24, 36, 34, 22, 10, 2, 0, 0, 0, 0],  # 144 MNs (caudal 144)
    'FHL':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 18, 30, 38, 32, 20, 8, 2, 0, 0, 0, 0, 0],   # 150 MNs (caudal 150)
    'Plantaris':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 12, 24, 36, 38, 26, 12, 2, 0, 0, 0, 0, 0],  # 154 MNs (caudal 154)
    'Soleus':   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 12, 24, 34, 32, 18, 6, 0, 0, 0, 0, 0],   # 130 MNs (caudal 130)
    'LG':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 20, 32, 36, 24, 10, 2, 0, 0, 0, 0],   # 134 MNs (caudal 134)
    'MG':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 14, 28, 40, 38, 22, 6, 0, 0, 0, 0],   # 152 MNs (caudal 152)
    'TP':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 12, 16, 12, 5, 2, 0, 0, 0, 0, 0, 0, 0, 0]     # 57 MNs (caudal 57)
}


class CatLumbosacralAnatomy:
    """
    Cat Lumbosacral Spinal Cord Anatomy Model spanning caudal L4 to rostral S1.
    Normalized to 100 levels, 30 transverse slices (0.96 mm/slice, 28.8 mm total length).
    """

    def __init__(self, length_mm: float = 28.8, n_slices: int = 30):
        self.length_mm = float(length_mm)
        self.n_slices = int(n_slices)
        self.slice_thickness_mm = self.length_mm / self.n_slices
        self.levels_per_slice = 100.0 / self.n_slices
        
        # Center coordinates for each slice in mm and normalized levels
        self.slice_centers_mm = (np.arange(self.n_slices) + 0.5) * self.slice_thickness_mm
        self.slice_centers_level = (np.arange(self.n_slices) + 0.5) * self.levels_per_slice

        # Segment boundary definitions
        self.segment_slices = {
            'L4': [0, 1, 2, 3],
            'L5': [4, 5, 6, 7, 8, 9],
            'L6': [10, 11, 12, 13, 14, 15, 16, 17],
            'L7': [18, 19, 20, 21, 22, 23, 24, 25],
            'S1': [26, 27, 28, 29]
        }

        # Build DataFrame of slice distributions
        self.slice_matrix = np.zeros((len(MUSCLE_NAMES), self.n_slices), dtype=np.int32)
        for i, m in enumerate(MUSCLE_NAMES):
            self.slice_matrix[i, :] = RAW_SLICE_PROFILES[m]

        self.df_distribution = pd.DataFrame(
            self.slice_matrix,
            index=MUSCLE_NAMES,
            columns=[f"Slice_{s+1}" for s in range(self.n_slices)]
        )

        self._compute_centers_of_mass()

    def _compute_centers_of_mass(self):
        """Computes center of mass (in mm and level) and rostrocaudal bounds for each pool."""
        self.centers_of_mass_mm = {}
        self.centers_of_mass_level = {}
        self.rostral_extent_level = {}
        self.caudal_extent_level = {}

        for m in MUSCLE_NAMES:
            counts = np.array(RAW_SLICE_PROFILES[m], dtype=np.float64)
            total = np.sum(counts)
            if total > 0:
                cm_mm = np.sum(counts * self.slice_centers_mm) / total
                cm_lvl = np.sum(counts * self.slice_centers_level) / total
                active_slices = np.where(counts > 0)[0]
                r_lvl = active_slices[0] * self.levels_per_slice
                c_lvl = (active_slices[-1] + 1) * self.levels_per_slice
            else:
                cm_mm = 0.0
                cm_lvl = 0.0
                r_lvl = 0.0
                c_lvl = 0.0

            self.centers_of_mass_mm[m] = float(cm_mm)
            self.centers_of_mass_level[m] = float(cm_lvl)
            self.rostral_extent_level[m] = float(r_lvl)
            self.caudal_extent_level[m] = float(c_lvl)

    def get_table1_counts(self, fdl_as_retractor: bool = True) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """
        Computes the exact motoneuron counts and percentages for Table 1:
        Rostral (L4-L6, slices 1-15) vs Caudal (L7-S1, slices 16-30).
        """
        rostral_mask = np.arange(self.n_slices) < 15
        caudal_mask = np.arange(self.n_slices) >= 15

        cats = dict(MUSCLE_CATEGORIES)
        if not fdl_as_retractor:
            cats['FDL'] = 'extensor'

        counts = {
            'extensor': {'rostral': 0, 'caudal': 0, 'total': 0},
            'retractor': {'rostral': 0, 'caudal': 0, 'total': 0},
            'flexor': {'rostral': 0, 'caudal': 0, 'total': 0},
            'all': {'rostral': 0, 'caudal': 0, 'total': 0}
        }

        for i, m in enumerate(MUSCLE_NAMES):
            cat = cats[m]
            prof = self.slice_matrix[i, :]
            r_cnt = int(np.sum(prof[rostral_mask]))
            c_cnt = int(np.sum(prof[caudal_mask]))
            tot = r_cnt + c_cnt

            counts[cat]['rostral'] += r_cnt
            counts[cat]['caudal'] += c_cnt
            counts[cat]['total'] += tot

            counts['all']['rostral'] += r_cnt
            counts['all']['caudal'] += c_cnt
            counts['all']['total'] += tot

        return counts
