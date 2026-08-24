# Figure 4 Reproduction Status & Post-Run Diagnostics

## Executive Summary

The Figure 4 reproduction pipeline (`run_figure4_reproduction.py`) was executed to reproduce **Figure 4 (Speed and Gait Control in the Mouse Spinal Projectome Model)** from Komi et al., *Nature Communications*, 2026.

All neural simulation stages (Walk, Trot, Bound, Descending Ramp, and 10-point Parameter Sweep) across the full $N = 5,229$ biological network **completed successfully**. The initial execution stopped during the figure generation phase (Step 5) due to an argument mismatch (`TypeError`) in the synthetic EMG plotting function.

---

## 1. Diagnostics Checklist

### 1.1 What was the last completed operation?
1. **Full Network Instantiation ($N = 5,229$)**: Completed across segments T13–S4 at connection density $D = 0.8$.
2. **Physiological Gait Simulations ($3 \times 10,000\text{ ms}$)**:
   - **Walk** ($I_e = 20\text{ pA}, g_{\text{5HT}} = 1.0\times$): Completed (Detected frequency: $0.98\text{ Hz}$, L-R phase: $115.3^\circ$).
   - **Trot** ($I_e = 30\text{ pA}, g_{\text{5HT}} = 1.0\times$): Completed (Detected frequency: $0.98\text{ Hz}$, L-R phase: $112.9^\circ$).
   - **Bound** ($I_e = 45\text{ pA}, g_{\text{5HT}} = 1.75\times$): Completed (Detected frequency: $1.46\text{ Hz}$, L-R phase: $216.5^\circ$).
3. **Descending Acceleration Ramp ($10,000\text{ ms}$)**: $I_e(t) = 15 \to 50\text{ pA}$ completed.
4. **10-Point Parameter Sweep ($10 \times 4,000\text{ ms}$)**: Completed and successfully saved to [`results/figure4_drive_sweep.csv`](file:///c:/Users/LAB/Documents/GitHub/ibrain/results/figure4_drive_sweep.csv).
5. **Initial Figure Panels**:
   - `plots/06_fig4a_tanh_gain_curves.png` (Panel 4A)
   - `plots/07_fig4b_descending_tract_maps.png` (Panel 4B)
   - `plots/08_fig4c_descending_drive_ramp.png` (Panel 4C)

### 1.2 Which simulation/analysis comes next?
- **Panel 4D** (`plots/09_fig4d_gait_patterns_emg.png`): Multi-muscle synthetic EMG traces across Walk, Trot, and Bound regimes.
- **Panel 4E** (`plots/10_fig4e_polar_phase_transitions.png`): Polar phase transition plots.
- **Panels 4F/G** (`plots/11_fig4fg_frequency_amplitude_quantification.png`): Frequency and amplitude vs drive current curves.
- **Composite Figure 4** (`plots/12_figure4_complete.png`): Unified publication multi-panel figure.
- **Summary Metrics Export**: Saving [`results/figure4_summary.json`](file:///c:/Users/LAB/Documents/GitHub/ibrain/results/figure4_summary.json) and timeseries arrays to [`results/figure4_gait_results.npz`](file:///c:/Users/LAB/Documents/GitHub/ibrain/results/figure4_gait_results.npz).

### 1.3 Why did execution stop?
Execution halted during Step 5 on line 190 of `src/figure4_analysis.py`:
```text
TypeError: generate_synthetic_emg() got an unexpected keyword argument 'muscles'
```
**Root Cause**: `generate_synthetic_emg` in `src/locomotion.py` expects:
```python
generate_synthetic_emg(
    rates: np.ndarray,
    neuron_types: np.ndarray,
    neuron_lat: np.ndarray,
    neuron_z: np.ndarray,
    time_ms: np.ndarray,
    noise_level: float = 0.1,
    window_ms: int = 20,
    rng_seed: int = 42
)
```
while `plot_panel_4d_gait_emg_patterns` called:
```python
generate_synthetic_emg(network, sim_res.rates, muscles=target_muscles, noise_level=0.15)
```

### 1.4 Was there an exception, timeout, or computational bottleneck?
- **Exception**: Python `TypeError` in the plotting layer.
- **No computational bottleneck**: The Euler numerical integration of $80,000$ total time steps across $5,229$ non-linear rate neurons executed with zero divergence, zero NaNs, and completed in $\approx 5.5$ minutes.

### 1.5 Are the Walk/Trot/Bound simulations actually required for Figure 4?
- **Yes**. In Komi et al. (2026), Figure 4 explicitly presents:
  - **Panel 4D**: Waveforms of reciprocal motor output (synthetic EMG) at distinct behavioral gaits (Walk, Trot, Bound).
  - **Panel 4E**: Polar vector coordination proving that high descending drive combined with serotonergic gain modulation transitions left-right coordination from alternation ($\approx 180^\circ$) to synchrony ($\approx 0^\circ$).
  - Therefore, the discrete Walk/Trot/Bound regimes are indispensable components of Figure 4.

### 1.6 Are there intermediate files or variables that were not saved?
- In `run_figure4_reproduction.py`, the in-memory simulation results (`gait_results` containing rates and voltages for Walk, Trot, and Bound) were not dumped to an `.npz` archive prior to invoking the plotting submodule.
- **Saved intermediate**: `results/figure4_drive_sweep.csv` was saved immediately after Step 4.

---

## 2. Component Status Matrix

| Component | Description | Status | File Location |
| :--- | :--- | :---: | :--- |
| **Network Instantiation** | $N=5,229$, T13–S4, Balanced & Rescaled | ✅ Complete | In-memory |
| **Walk Simulation** | $I_e = 20\text{ pA}$, $10\text{ s}$ duration | ✅ Complete | In-memory / NPZ export pending |
| **Trot Simulation** | $I_e = 30\text{ pA}$, $10\text{ s}$ duration | ✅ Complete | In-memory / NPZ export pending |
| **Bound Simulation** | $I_e = 45\text{ pA}, 1.75\times\text{ 5-HT}$, $10\text{ s}$ | ✅ Complete | In-memory / NPZ export pending |
| **Descending Ramp** | $I_e: 15 \to 50\text{ pA}$, $10\text{ s}$ | ✅ Complete | In-memory |
| **Parameter Sweep** | 10 drive levels ($15 - 50\text{ pA}$) | ✅ Complete | [`results/figure4_drive_sweep.csv`](file:///c:/Users/LAB/Documents/GitHub/ibrain/results/figure4_drive_sweep.csv) |
| **Figure 4A** | $\tanh$ Gain Modulation Curves | ✅ Complete | [`plots/06_fig4a_tanh_gain_curves.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/06_fig4a_tanh_gain_curves.png) |
| **Figure 4B** | Descending Brainstem Terminal Maps | ✅ Complete | [`plots/07_fig4b_descending_tract_maps.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/07_fig4b_descending_tract_maps.png) |
| **Figure 4C** | Rhythm Acceleration Raster Under Ramp | ✅ Complete | [`plots/08_fig4c_descending_drive_ramp.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/08_fig4c_descending_drive_ramp.png) |
| **Figure 4D** | Synthetic Multi-Gait EMG Signals | ⚠️ Stopped at plotting call | [`plots/09_fig4d_gait_patterns_emg.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/09_fig4d_gait_patterns_emg.png) |
| **Figure 4E** | Polar Phase Transition Diagrams | ⚠️ Stopped after 4D | [`plots/10_fig4e_polar_phase_transitions.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/10_fig4e_polar_phase_transitions.png) |
| **Figure 4F/G** | Frequency & Amplitude Quantification | ⚠️ Stopped after 4D | [`plots/11_fig4fg_frequency_amplitude_quantification.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/11_fig4fg_frequency_amplitude_quantification.png) |
| **Figure 4 Complete** | Unified Composite Publication Figure | ⚠️ Stopped after 4D | [`plots/12_figure4_complete.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/12_figure4_complete.png) |
| **Summary JSON** | Structured quantitative metrics | ⚠️ Pending final export | [`results/figure4_summary.json`](file:///c:/Users/LAB/Documents/GitHub/ibrain/results/figure4_summary.json) |

---

## 3. Original MATLAB Figure 4 Comparison

In BergLab's MATLAB implementation (`@Network/Simulate.m`, `@Network/PlotEMG.m`, `ComputePhase.m`):
1. **Descending Drive**: Modeled as an additive depolarizing current $I_e$ injected into target excitatory neurons (V2a, V0v, V3, MN).
2. **5-HT Neuromodulation**: Modeled as a slope/gain multiplication $g_{\text{eff}} = \alpha \cdot g$ on the non-linear rate transfer function $R(V) = [T \tanh(g(V-T)/T) + T]^+$.
3. **EMG Synthesis**: `PlotEMG.m` calculates motor pool summed firing rates $\text{prob}(t) = \sum_{i \in \text{pool}} R_i(t)$, draws Bernoulli recruitment events modulated by normal CDF z-scores, and convolves rectified signals with a $20\text{ ms}$ moving average window.
4. **Figure Assembly**: MATLAB generates individual figures for the activation curve, anatomical tracts, speed raster, EMG bursts, polar phases, and current-frequency curves.

---

## 4. Recommended Minimal Fix

1. **Save Simulation State First**: Update `run_figure4_reproduction.py` to persist `results/figure4_gait_results.npz` and `results/figure4_summary.json` immediately after the simulations complete, before calling `generate_figure4_complete`.
2. **Correct `generate_synthetic_emg` Invocation**: Ensure `plot_panel_4d_gait_emg_patterns` and `generate_figure4_complete` pass the exact keyword arguments expected by `src/locomotion.py`:
   ```python
   emg_data = generate_synthetic_emg(
       rates=sim_res.rates,
       neuron_types=network.types,
       neuron_lat=network.latera,
       neuron_z=network.pos_z,
       time_ms=sim_res.time_ms,
       noise_level=0.15,
       window_ms=20,
       rng_seed=42
   )
   ```
3. **Stand-Alone Plotting Script**: Provide an option in `run_figure4_reproduction.py` (e.g. `--plots-only`) that loads saved simulation results from `results/` so figures can be regenerated instantly in seconds without re-simulating the 80-second neural trajectories.
