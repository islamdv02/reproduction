"""
Critical Monte Carlo Evaluator: 10 Independent Random Seeds with Full Distribution Statistics.
Computes Mean, SD, Median, Min, Max, and 95% Confidence Intervals across 10 independent runs,
benchmarked against a >= 400 surrogate random-walk null baseline.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import signal
from scipy import stats

from model_y import ModelY
from model_ky import ModelKY


def compute_random_walk_null(y_ref: np.ndarray, n_surrogates: int = 400, seed: int = 42) -> Tuple[float, float, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_pts = len(y_ref)
    null_corrs = np.zeros(n_surrogates)
    y_ref_centered = y_ref - np.mean(y_ref)

    for s in range(n_surrogates):
        steps = rng.normal(0.0, 1.0, size=n_pts * 4)
        rw_raw = np.cumsum(steps)
        rw_segment = rw_raw[:n_pts * 2]
        rw_resampled = signal.resample(rw_segment, n_pts)

        rw_centered = rw_resampled - np.mean(rw_resampled)
        if np.std(rw_centered) > 1e-9:
            xcorr = signal.correlate(y_ref_centered, rw_centered, mode='full')
            lags = signal.correlation_lags(n_pts, n_pts)
            best_lag = lags[np.argmax(xcorr)]
            rw_aligned = np.roll(rw_resampled, best_lag)
            r_val = float(np.corrcoef(y_ref, rw_aligned)[0, 1])
        else:
            r_val = 0.0
        null_corrs[s] = r_val

    null_med = float(np.median(null_corrs))
    null_95 = float(np.percentile(null_corrs, 95))
    return null_med, null_95, null_corrs


class CriticalMonteCarloEvaluator:
    """
    Evaluates model robustness across 10 random seeds with empirical null benchmarks.
    """

    def __init__(self, seeds: List[int] = [42, 101, 2024, 7, 99, 1234, 555, 888, 314, 777]):
        self.seeds = list(seeds)

    def run_10_seed_evaluation(self, n_surrogates: int = 400) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
        records = []
        model_y = ModelY(recruitment_mode='graded', n_cycles=2)
        y_ref = model_y.r_cm_level[:100]

        null_med, null_95, null_corrs = compute_random_walk_null(y_ref, n_surrogates=n_surrogates, seed=42)

        for seed in self.seeds:
            m_ky = ModelKY(n_neurons=500, rng_seed=seed, duration_ms=2500.0, warmup_ms=500.0)

            # Cycle resample
            period_ms = m_ky.phase_unfolder.cycle_period_ms
            dt = m_ky.dynamics.dt_ms
            steps = int(np.round(period_ms / dt))
            if 20 < steps < len(m_ky.r_cm_level):
                ky_cycle = m_ky.r_cm_level[:steps]
                ky_100 = signal.resample(ky_cycle, 100)
            else:
                ky_100 = signal.resample(m_ky.r_cm_level[:400], 100)

            # Align
            xcorr = signal.correlate(y_ref - np.mean(y_ref), ky_100 - np.mean(ky_100), mode='full')
            lags = signal.correlation_lags(100, 100)
            best_lag = lags[np.argmax(xcorr)]
            ky_aligned = np.roll(ky_100, best_lag)

            corr = float(np.corrcoef(y_ref, ky_aligned)[0, 1])
            rmse = float(np.sqrt(np.mean((y_ref - ky_aligned)**2)))
            nrmse = float(rmse / (np.max(y_ref) - np.min(y_ref)))
            p_val = float(np.mean(null_corrs >= corr))

            rec = {
                'seed': seed,
                'trajectory_correlation_r': corr,
                'null_median_r': null_med,
                'null_95th_pct_r': null_95,
                'p_value_vs_null': p_val,
                'rmse_levels': rmse,
                'normalized_rmse': nrmse,
                'phase_error_pct': abs(int(best_lag)),
                'bilateral_phase_diff_deg': float(m_ky.wave.bilateral_phase_diff_deg),
                'wave_velocity_mm_s': float(m_ky.wave.velocity_mm_s),
                'dominant_frequency_hz': float(m_ky.phase_unfolder.frequency_hz),
                'pca_planar_variance_pct': float(m_ky.phase_unfolder.planar_variance * 100.0),
                'mexican_hat_index': float(m_ky.projectome.mexican_hat_index),
                'projectome_asymmetry': float(m_ky.projectome.asymmetry_index)
            }
            records.append(rec)

        df = pd.DataFrame(records)

        # Full statistics
        stats_dict = {}
        N = len(self.seeds)
        for col in df.columns:
            if col != 'seed':
                vals = df[col].values
                mean = float(np.mean(vals))
                std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
                median = float(np.median(vals))
                val_min = float(np.min(vals))
                val_max = float(np.max(vals))
                # 95% Confidence Interval
                sem = std / np.sqrt(N)
                ci95_low = mean - 1.96 * sem
                ci95_high = mean + 1.96 * sem

                stats_dict[col] = {
                    'mean': mean,
                    'std': std,
                    'median': median,
                    'min': val_min,
                    'max': val_max,
                    'ci95_low': float(ci95_low),
                    'ci95_high': float(ci95_high)
                }

        return df, stats_dict
