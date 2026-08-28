"""
Wave Decomposition Module: Mathematical & Conceptual Dissection of the Three Wave Phenomena.
Compares Wave A (Activity Migration), Wave B (Stance/Swing Shift), and Wave C (Emergent Traveling Wave).
"""

from typing import Dict, Tuple
import numpy as np
from scipy import signal
from model_y import ModelY
from model_ky import ModelKY


class WaveDecomposer:
    """
    Decomposes and compares:
    - Wave A: Center of Motoneuron Activity Migration r_cm(t)
    - Wave B: Phase-Locked Stance-to-Swing Shift
    - Wave C: Continuous Neurogenic Traveling Wave of Interneuronal Spikes
    """

    def __init__(self, model_y: ModelY, model_ky: ModelKY):
        self.model_y = model_y
        self.model_ky = model_ky

        self._analyze_wave_types()

    def _analyze_wave_types(self):
        """Quantifies metrics for all three wave categories."""
        # 1. Wave A Metrics (Model Y: Activity Migration)
        self.wave_a_displacement_mm = float(np.max(self.model_y.r_cm_mm) - np.min(self.model_y.r_cm_mm))
        self.wave_a_peak_velocity = float(np.max(self.model_y.velocity_mm_s))
        self.wave_a_mean_velocity = float(np.mean(self.model_y.velocity_mm_s))

        # 2. Wave B Metrics (Model Y: Stance/Swing Ratio & Jump)
        # Fraction of cycle spent in caudal stance (level > 50) vs rostral swing (level < 50)
        caudal_mask = (self.model_y.r_cm_level > 50.0)
        self.wave_b_caudal_stance_fraction = float(np.mean(caudal_mask))
        self.wave_b_jump_magnitude_levels = float(np.percentile(self.model_y.r_cm_level, 95) - np.percentile(self.model_y.r_cm_level, 5))

        # 3. Wave C Metrics (Model K-Y: Emergent Continuous Neurogenic Traveling Wave)
        self.wave_c_propagation_velocity = float(self.model_ky.wave.velocity_mm_s)
        self.wave_c_bilateral_phase = float(self.model_ky.wave.bilateral_phase_diff_deg)
        self.wave_c_frequency = float(self.model_ky.phase_unfolder.frequency_hz)
        self.wave_c_mexican_hat_index = float(self.model_ky.projectome.mexican_hat_index)

    def get_summary_dict(self) -> Dict[str, Dict[str, float]]:
        return {
            "Wave_A_Activity_Migration": {
                "displacement_mm": self.wave_a_displacement_mm,
                "peak_velocity_mm_s": self.wave_a_peak_velocity,
                "mean_velocity_mm_s": self.wave_a_mean_velocity
            },
            "Wave_B_Stance_Swing_Shift": {
                "caudal_stance_time_fraction": self.wave_b_caudal_stance_fraction,
                "jump_magnitude_levels": self.wave_b_jump_magnitude_levels
            },
            "Wave_C_Emergent_Traveling_Wave": {
                "propagation_velocity_mm_s": self.wave_c_propagation_velocity,
                "bilateral_phase_diff_deg": self.wave_c_bilateral_phase,
                "frequency_hz": self.wave_c_frequency,
                "mexican_hat_index": self.wave_c_mexican_hat_index
            }
        }
