"""
Mechanistic Comparator Module: Multi-Seed Monte Carlo Comparison Between Model Y and Model K-Y.
Runs N >= 5 independent random seeds and computes correlation, RMSE, NRMSE, phase lag, and velocity.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import signal
from model_y import ModelY
from model_ky import ModelKY


class MechanisticComparator:
    """
    Executes rigorous multi-seed comparative benchmarking between Model Y and Model K-Y.
    """

    def __init__(self, seeds: List[int] = [42, 101, 2024, 7, 99]):
        self.seeds = list(seeds)

    def run_multi_seed_comparison(self) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
        """Runs simulations across all seeds and compiles quantitative comparative statistics."""
        records = []

        # Model Y reference (deterministic empirical baseline)
        model_y = ModelY(recruitment_mode='graded', n_cycles=2)
        y_traj_100 = model_y.r_cm_level[:100]

        for s_idx, seed in enumerate(self.seeds):
            m_ky = ModelKY(n_neurons=800, rng_seed=seed, duration_ms=2500.0, warmup_ms=500.0)

            # Resample Model K-Y trajectory to 100 step cycle points
            # Identify dominant period
            T_period = m_ky.phase_unfolder.cycle_period_ms
            dt = m_ky.dynamics.dt_ms
            steps_per_cycle = int(np.round(T_period / dt))

            if steps_per_cycle > 20 and steps_per_cycle < len(m_ky.r_cm_level):
                ky_cycle = m_ky.r_cm_level[:steps_per_cycle]
                ky_resampled = signal.resample(ky_cycle, 100)
            else:
                ky_resampled = signal.resample(m_ky.r_cm_level[:400], 100)

            # Alignment / Cross-correlation to find best phase alignment
            xcorr = signal.correlate(y_traj_100 - np.mean(y_traj_100),
                                     ky_resampled - np.mean(ky_resampled), mode='full')
            lags = signal.correlation_lags(100, 100)
            best_lag = lags[np.argmax(xcorr)]

            ky_aligned = np.roll(ky_resampled, best_lag)

            # Metrics
            corr = float(np.corrcoef(y_traj_100, ky_aligned)[0, 1])
            rmse = float(np.sqrt(np.mean((y_traj_100 - ky_aligned) ** 2)))
            nrmse = float(rmse / (np.max(y_traj_100) - np.min(y_traj_100)))

            rec = {
                'seed': seed,
                'correlation_r': corr,
                'rmse_levels': rmse,
                'nrmse': nrmse,
                'phase_lag_pct': abs(best_lag),
                'wave_velocity_mm_s': m_ky.wave.velocity_mm_s,
                'mexican_hat_index': m_ky.projectome.mexican_hat_index,
                'projectome_asymmetry': m_ky.projectome.asymmetry_index,
                'planar_variance_pct': m_ky.phase_unfolder.planar_variance * 100.0,
                'dominant_freq_hz': m_ky.phase_unfolder.frequency_hz,
                'bilateral_phase_deg': m_ky.wave.bilateral_phase_diff_deg
            }
            records.append(rec)

        df = pd.DataFrame(records)

        # Summary statistics (mean +- SD)
        stats = {}
        for col in df.columns:
            if col != 'seed':
                stats[col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }

        return df, stats
