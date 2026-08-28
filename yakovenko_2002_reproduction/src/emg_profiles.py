"""
Standardized 27-Muscle Hindlimb Electromyographic (EMG) Step Cycle Profiles.
Faithfully reproduces Figure 3 from Yakovenko et al. (J Neurophysiol 2002).
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


def generate_piecewise_linear_emg(keypoints: List[Tuple[float, float]], n_points: int = 100) -> np.ndarray:
    """
    Generates a 100-point normalized EMG profile from a list of (cycle_percent, emg_level_percent) keypoints.
    Automatically handles circular wrapping across the 0-100% step cycle.
    """
    keypoints = sorted(keypoints, key=lambda k: k[0])
    x_k = [k[0] for k in keypoints]
    y_k = [k[1] for k in keypoints]

    # Ensure boundaries wrap cleanly
    if x_k[0] > 0.0:
        x_k.insert(0, 0.0)
        y_k.insert(0, y_k[-1] if x_k[-1] == 100.0 else y_k[0])
    if x_k[-1] < 100.0:
        x_k.append(100.0)
        y_k.append(y_k[0])

    t = np.linspace(0.0, 100.0, n_points, endpoint=False)
    emg = np.interp(t, x_k, y_k)
    return np.clip(emg, 0.0, 100.0)


def build_all_emg_profiles(fdl_as_retractor: bool = True) -> Dict[str, np.ndarray]:
    """
    Constructs normalized 100-point EMG profiles for all 27 hindlimb muscles
    matching the piecewise linear profiles in Figure 3.
    """
    profiles = {}

    # --- EXTENSORS ---
    # AdFM (Adductor femoris magnus)
    profiles['AdFM'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (25.0, 0.0), (30.0, 30.0), (55.0, 100.0), (75.0, 80.0), (95.0, 15.0), (98.0, 0.0), (100.0, 0.0)
    ])

    # BFa (Biceps femoris anterior)
    profiles['BFa'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (25.0, 0.0), (30.0, 40.0), (50.0, 100.0), (75.0, 70.0), (90.0, 10.0), (95.0, 0.0), (100.0, 0.0)
    ])

    # CF (Caudofemoralis)
    profiles['CF'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (30.0, 0.0), (35.0, 20.0), (60.0, 100.0), (80.0, 60.0), (92.0, 0.0), (100.0, 0.0)
    ])

    # FHL (Flexor hallucis longus)
    profiles['FHL'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (22.0, 0.0), (30.0, 45.0), (55.0, 100.0), (75.0, 60.0), (88.0, 10.0), (92.0, 0.0), (100.0, 0.0)
    ])

    # GlutMax (Gluteus maximus)
    profiles['GlutMax'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (28.0, 0.0), (35.0, 40.0), (52.0, 100.0), (70.0, 60.0), (85.0, 0.0), (100.0, 0.0)
    ])

    # GlutMed (Gluteus medius)
    profiles['GlutMed'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (26.0, 0.0), (32.0, 35.0), (55.0, 100.0), (75.0, 65.0), (90.0, 0.0), (100.0, 0.0)
    ])

    # LG (Gastrocnemius lateralis)
    profiles['LG'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (21.0, 0.0), (30.0, 50.0), (50.0, 100.0), (72.0, 60.0), (85.0, 0.0), (100.0, 0.0)
    ])

    # MG (Gastrocnemius medialis)
    profiles['MG'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (21.0, 0.0), (30.0, 50.0), (50.0, 100.0), (72.0, 60.0), (85.0, 0.0), (100.0, 0.0)
    ])

    # Plantaris
    profiles['Plantaris'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (22.0, 0.0), (30.0, 45.0), (55.0, 100.0), (72.0, 55.0), (85.0, 0.0), (100.0, 0.0)
    ])

    # SMa (Semimembranosus anterior)
    profiles['SMa'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (28.0, 0.0), (32.0, 30.0), (55.0, 100.0), (75.0, 65.0), (90.0, 0.0), (100.0, 0.0)
    ])

    # Soleus
    profiles['Soleus'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (20.0, 0.0), (30.0, 55.0), (55.0, 100.0), (80.0, 75.0), (92.0, 15.0), (96.0, 0.0), (100.0, 0.0)
    ])

    # TP (Tibialis posterior)
    profiles['TP'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (25.0, 0.0), (30.0, 35.0), (55.0, 100.0), (75.0, 50.0), (88.0, 0.0), (100.0, 0.0)
    ])

    # VI (Vastus intermedius)
    profiles['VI'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (24.0, 0.0), (30.0, 50.0), (45.0, 100.0), (62.0, 40.0), (75.0, 0.0), (100.0, 0.0)
    ])

    # VL (Vastus lateralis)
    profiles['VL'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (23.0, 0.0), (30.0, 65.0), (40.0, 100.0), (58.0, 35.0), (68.0, 45.0), (78.0, 0.0), (100.0, 0.0)
    ])

    # VM (Vastus medialis)
    profiles['VM'] = generate_piecewise_linear_emg([
        (0.0, 0.0), (23.0, 0.0), (30.0, 60.0), (42.0, 100.0), (60.0, 35.0), (75.0, 0.0), (100.0, 0.0)
    ])

    # --- FLEXORS ---
    # EDL (Extensor digitorum longus)
    profiles['EDL'] = generate_piecewise_linear_emg([
        (0.0, 60.0), (8.0, 100.0), (18.0, 50.0), (26.0, 0.0), (100.0, 0.0)
    ])

    # Iliacus
    profiles['Iliacus'] = generate_piecewise_linear_emg([
        (0.0, 50.0), (10.0, 100.0), (20.0, 60.0), (28.0, 0.0), (100.0, 0.0)
    ])

    # Psoas
    profiles['Psoas'] = generate_piecewise_linear_emg([
        (0.0, 55.0), (8.0, 100.0), (18.0, 55.0), (28.0, 0.0), (100.0, 0.0)
    ])

    # RF (Rectus femoris)
    profiles['RF'] = generate_piecewise_linear_emg([
        (0.0, 60.0), (8.0, 100.0), (18.0, 40.0), (24.0, 0.0), (62.0, 0.0), (72.0, 55.0), (84.0, 0.0), (100.0, 0.0)
    ])

    # SRTa (Sartorius anterior)
    profiles['SRTa'] = generate_piecewise_linear_emg([
        (0.0, 45.0), (12.0, 100.0), (22.0, 50.0), (29.0, 0.0), (100.0, 0.0)
    ])

    # SRTm (Sartorius medialis)
    profiles['SRTm'] = generate_piecewise_linear_emg([
        (0.0, 45.0), (12.0, 100.0), (22.0, 50.0), (29.0, 0.0), (100.0, 0.0)
    ])

    # TA (Tibialis anterior)
    profiles['TA'] = generate_piecewise_linear_emg([
        (0.0, 65.0), (8.0, 100.0), (18.0, 55.0), (28.0, 0.0), (100.0, 0.0)
    ])

    # --- RETRACTORS ---
    # BFp (Biceps femoris posterior)
    profiles['BFp'] = generate_piecewise_linear_emg([
        (0.0, 60.0), (8.0, 15.0), (15.0, 0.0), (20.0, 15.0), (26.0, 40.0), (32.0, 0.0),
        (82.0, 0.0), (90.0, 45.0), (96.0, 100.0), (100.0, 60.0)
    ])

    # Gracilis
    profiles['Gracilis'] = generate_piecewise_linear_emg([
        (0.0, 50.0), (8.0, 15.0), (16.0, 0.0), (20.0, 10.0), (26.0, 35.0), (32.0, 0.0),
        (82.0, 0.0), (90.0, 45.0), (96.0, 100.0), (100.0, 50.0)
    ])

    # ST (Semitendinosus)
    profiles['ST'] = generate_piecewise_linear_emg([
        (0.0, 65.0), (8.0, 15.0), (15.0, 0.0), (20.0, 20.0), (26.0, 50.0), (32.0, 0.0),
        (80.0, 0.0), (88.0, 40.0), (96.0, 100.0), (100.0, 65.0)
    ])

    # SMp (Semimembranosus posterior)
    profiles['SMp'] = generate_piecewise_linear_emg([
        (0.0, 40.0), (8.0, 10.0), (16.0, 0.0), (82.0, 0.0), (90.0, 40.0), (96.0, 100.0), (100.0, 40.0)
    ])

    # FDL (Flexor digitorum longus) - Retractor mode vs Extensor mode
    if fdl_as_retractor:
        profiles['FDL'] = generate_piecewise_linear_emg([
            (0.0, 60.0), (8.0, 10.0), (15.0, 0.0), (80.0, 0.0), (88.0, 35.0), (96.0, 100.0), (100.0, 60.0)
        ])
    else:
        profiles['FDL'] = generate_piecewise_linear_emg([
            (0.0, 0.0), (22.0, 0.0), (30.0, 40.0), (55.0, 100.0), (75.0, 55.0), (88.0, 0.0), (100.0, 0.0)
        ])

    return profiles


class CatHindlimbEMG:
    """
    Manages the 27 muscle EMG profiles across the 100-step cycle.
    Provides matrix format and interpolation for simulation time steps.
    """

    def __init__(self, fdl_as_retractor: bool = True):
        self.fdl_as_retractor = bool(fdl_as_retractor)
        self.profiles = build_all_emg_profiles(fdl_as_retractor=self.fdl_as_retractor)
        self.muscle_names = list(self.profiles.keys())
        self.n_points = 100

        # Matrix format (27 muscles x 100 time points)
        self.emg_matrix = np.zeros((len(self.muscle_names), self.n_points), dtype=np.float64)
        for i, m in enumerate(self.muscle_names):
            self.emg_matrix[i, :] = self.profiles[m]

        self.df_emg = pd.DataFrame(
            self.emg_matrix,
            index=self.muscle_names,
            columns=[f"Step_{t}" for t in range(self.n_points)]
        )

    def get_emg(self, muscle: str, step_pct: float) -> float:
        """Returns the normalized EMG level (0-100%) for a muscle at step cycle percent [0, 100)."""
        idx = int(np.clip(np.floor(step_pct), 0, 99))
        return float(self.profiles[muscle][idx])
