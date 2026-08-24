# Figure 5 Reproduction: Cell-Type Perturbation Experiments

This document details the scientific theory, mathematical formulations, parameters, and algorithms used to reproduce **Figure 5: Cell-Type Perturbation Experiments in the Mouse Spinal Projectome Model** from *Komi et al., Nature Communications, 2026*, referencing the original BergLab MATLAB codebase (`@Network/MakeLesion.m`, `@Network/Simulate.m`, `02_HelperFunctions/GenerateSynapticDistrib.m`, `@Network/PlotEMG.m`, `@Network/PlotNeurogram.m`, `@Network/Network.m/ComputePhase`).

---

## 1. Scientific Background & Biological Mechanism

Figure 5 establishes the functional necessity of specific genetically identified spinal interneuron classes in establishing the spatiotemporal traveling wave, cycle period, burst amplitude, and interlimb coordination:

1. **V1 Inhibitory Interneurons (En1+)**:
   - V1 neurons project rostrally ($L = 900\ \mu\text{m}$, bias $ro$, ventrolateral) and provide the rostral inhibitory lobe of the spatial Mexican-hat projectome ($sp_2$).
   - **Perturbation Effect**: Loss of V1 inhibition removes the inhibitory braking on traveling wave propagation, resulting in rhythm deceleration (lower frequency) and increased motor burst amplitude (hyperflexion due to disinhibition), while preserving Left–Right and Flexor–Extensor alternation.

2. **V0 Commissural Interneurons (Evx1+)**:
   - V0 neurons comprise inhibitory V0d (GABA/glycinergic, local $500\ \mu\text{m}$) and excitatory V0v (glutamatergic, ascending $3,400\ \mu\text{m}$) commissural interneurons crossing the ventral midline.
   - **Perturbation Effect**: Loss of V0 commissural coupling eliminates anti-phase bilateral coordination, causing Left–Right phase to switch from alternation ($\sim 180^\circ$) to in-phase synchrony ($\sim 0^\circ$), resulting in a hopping/bounding gait phenotype while preserving intralimb flexor-extensor alternation.

---

## 2. Experimental Regimes & Simulation Parameters

- **Spinal Network**: 11 spinal segments ($T_{13}$–$S_4$), $N = 5,229$ neurons ($D = 0.8$, seed 42).
- **Simulation Duration**: $10,000\text{ ms}$ ($10\text{ s}$) forward Euler integration, $\Delta t = 1.0\text{ ms}$, $\tau_V = 50.0\text{ ms}$.
- **Drive & Neuromodulation**: $I_e = 30.0\text{ pA}$ (trot baseline), $\alpha_{\text{5HT}} = 1.0\times$.
- **Noise & Initial Conditions**: $\sigma_{\text{noise}} = 0.5\text{ pA}$, $V_{\text{init}} \sim \mathcal{N}(-70, 3)\text{ mV}$.

### Perturbation Configurations

| Condition | Target Population | Perturbation Method | Mathematical Representation |
| :--- | :--- | :--- | :--- |
| **Control** | None | Intact network | $W$ unmodified, $I_e = 30\text{ pA}$ |
| **V1 Perturbation** | V1 (En1+) | Genetic ablation | $W_{:, \text{V1}} = 0, W_{\text{V1}, :} = 0$ |
| **V0 Perturbation** | V0v + V0d (Evx1+) | Genetic ablation | $W_{:, \text{V0}} = 0, W_{\text{V0}, :} = 0$ |

---

## 3. Panel-by-Panel Specifications

### Panel 5A: V1 Projectome Deletion
- **Biological Question**: How does V1 deletion alter the spatial projectome profile?
- **Analysis**: 1D spatial projection profile along rostrocaudal distance ($\Delta Z = Z_{\text{post}} - Z_{\text{pre}}$).
- **MATLAB Source**: `02_HelperFunctions/GenerateSynapticDistrib.m`.
- **Python Source**: `src/figure5_analysis.py:plot_panel_5a_v1_projectome()`.
- **Output**: [`plots/13_fig5a_v1_projectome.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/13_fig5a_v1_projectome.png).

### Panel 5B: V1 Spatiotemporal Activity & Synthetic EMG
- **Biological Question**: What are the physiological consequences of V1 deletion on motor burst patterns?
- **Analysis**: Population firing rates and synthetic EMG (Tibialis Anterior / Gastrocnemius) over a $2\text{ s}$ steady-state window.
- **MATLAB Source**: `@Network/PlotEMG.m`, `@Network/PlotNeurogram.m`.
- **Python Source**: `src/figure5_analysis.py:plot_panel_5b_v1_activity_emg()`.
- **Output**: [`plots/14_fig5b_v1_activity_emg.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/14_fig5b_v1_activity_emg.png).

### Panel 5C: V1 Quantification
- **Biological Question**: Does V1 deletion preserve bilateral and intralimb phase coordination?
- **Metrics**: Locomotor frequency (Hz), RMS amplitude (Hz), circular Left–Right and Flexor–Extensor phase angles.
- **MATLAB Source**: `@Network/Network.m:ComputePhase`.
- **Python Source**: `src/figure5_analysis.py:plot_panel_5c_v1_quantification()`.
- **Output**: [`plots/15_fig5c_v1_quantification.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/15_fig5c_v1_quantification.png).

### Panel 5D: V0 Contralateral Projectome Deletion
- **Biological Question**: How does V0 deletion eliminate cross-cord commissural connectivity?
- **Analysis**: 1D contralateral projectome profile before vs. after V0 ablation.
- **MATLAB Source**: `02_HelperFunctions/GenerateSynapticDistrib.m`.
- **Python Source**: `src/figure5_analysis.py:plot_panel_5d_v0_projectome()`.
- **Output**: [`plots/16_fig5d_v0_projectome.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/16_fig5d_v0_projectome.png).

### Panel 5E: V0 Spatiotemporal Activity & Synthetic EMG
- **Biological Question**: Does V0 deletion convert alternating locomotion into bilateral synchrony (hopping)?
- **Analysis**: Firing rate rasters and bilateral synthetic EMG envelopes under V0 deletion.
- **MATLAB Source**: `@Network/PlotEMG.m`, `@Network/PlotRaster.m`.
- **Python Source**: `src/figure5_analysis.py:plot_panel_5e_v0_activity_emg()`.
- **Output**: [`plots/17_fig5e_v0_activity_emg.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/17_fig5e_v0_activity_emg.png).

### Panel 5F: V0 Quantification
- **Biological Question**: What is the quantitative phase shift under V0 ablation?
- **Metrics**: Frequency (Hz), Left–Right polar phase ($\Delta \phi_{\text{L-R}} \to 0^\circ$), Flexor–Extensor polar phase ($\Delta \phi_{\text{F-E}}$).
- **MATLAB Source**: `@Network/Network.m:ComputePhase`.
- **Python Source**: `src/figure5_analysis.py:plot_panel_5f_v0_quantification()`.
- **Output**: [`plots/18_fig5f_v0_quantification.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/18_fig5f_v0_quantification.png).

### Composite Figure 5
- **Output**: [`plots/19_figure5_complete.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/plots/19_figure5_complete.png).
