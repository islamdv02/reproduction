# Figure 4 Reproduction: Speed and Gait Control

This document details the scientific theory, mathematical formulations, parameters, and algorithms used to reproduce **Figure 4: Speed and Gait Control in the Mouse Spinal Projectome Model** from *Komi et al., Nature Communications, 2026*, referencing the original BergLab MATLAB codebase (`@Network`, `@SpinalCordGeometry`, `@NetworkParameters`, `Simulate.m`, `ComputePhase.m`).

---

## 1. Scientific Background & Biological Mechanism

Locomotion in vertebrates requires flexible adaptation of speed and coordination pattern (gait) in response to environmental demands and descending commands from the brainstem:

1. **Glutamatergic Drive from the Lateral Paragigantocellular Nucleus (LPGi)**:
   - LPGi neurons located in the caudal ventrolateral medulla project bilaterally along the ventral spinal cord to provide monotonic excitatory current drive $I_{\text{LPGi}}$ to premotor spinal interneurons ($V2a, V0v, V3$) and motoneurons.
   - Increases overall network depolarization, accelerating the propagation speed of intrinsic traveling activity waves along the rostrocaudal axis ($T_{13} \to S_4$), driving locomotor frequency from $\approx 1.5\text{ Hz}$ up to $\approx 8.5\text{ Hz}$.

2. **Serotonergic Neuromodulation (5-HT) from Raphe Nuclei (Mg, Ob)**:
   - Raphe Magnus ($Mg$) and Raphe Obscurus ($Ob$) provide diffuse serotonergic innervation to the ventral and intermediate spinal cord.
   - 5-HT acts on high-affinity $5\text{-HT}_7$ and $5\text{-HT}_{2\text{A}}$ receptors on excitatory ($V2a, V3$) and inhibitory interneurons, increasing intrinsic activation gain $g \to g \cdot (1 + \alpha_{\text{5HT}})$ and lowering threshold $T$.
   - The synergistic combination of elevated LPGi drive and 5-HT gain engages higher-order network modes, causing a phase transition from left-right alternating gaits (**Walk**, **Trot**) to left-right synchronous gaits (**Bound**, **Gallop**).

---

## 2. Experimental Regimes & Simulation Parameters

- **Spinal Network**: 11 spinal segments ($T_{13}, L_1, L_2, L_3, L_4, L_5, L_6, S_1, S_2, S_3, S_4$) with $N = 5,229$ neurons ($D = 0.8$, $Sym = 1$, $Balance = 1$, $\sigma_{\text{spatial}} = 500\ \mu\text{m}$).
- **Integration**: Forward Euler, $\Delta t = 1.0\ \text{ms}$, $\tau_V = 50.0\ \text{ms}$, $\sigma_{\text{noise}} = 0.5$, $V_{\text{init}} \sim \mathcal{N}(-70, 3)\ \text{mV}$.

### Multi-Gait Parameter Configurations

| Gait State | Descending Current $I_e$ | 5-HT Gain Multiplier | Target Frequency $f$ | Left-Right Phase $\Delta \phi_{\text{L-R}}$ | Flexor-Extensor Phase $\Delta \phi_{\text{F-E}}$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Walk** | $20.0\text{ pA}$ | $1.0\times$ ($g = 0.7 - 1.0$) | $1.5 - 2.5\text{ Hz}$ | $\approx 180^\circ$ ($\pi$, Alternation) | $\approx 180^\circ$ ($\pi$, Alternation) |
| **Trot** | $30.0\text{ pA}$ | $1.0\times$ ($g = 1.0$) | $3.5 - 5.0\text{ Hz}$ | $\approx 180^\circ$ ($\pi$, Alternation) | $\approx 180^\circ$ ($\pi$, Alternation) |
| **Bound** | $45.0\text{ pA}$ | $1.5 - 2.0\times$ ($g = 1.5 - 2.0$) | $6.0 - 8.5\text{ Hz}$ | $\approx 0^\circ$ ($0$, Synchrony) | $\approx 180^\circ$ ($\pi$, Alternation) |

---

## 3. Panel-by-Panel Specifications

### Panel 4A: Compound Hyperbolic Tangent Gain Modulation Curves
- **Scientific Question**: How does neuromodulatory gain ($g$) and external input shift the neuronal input-output activation curve?
- **Equations**:
  $$f(V) = \begin{cases} T \tanh\left(\frac{g(V - T)}{T}\right) & \text{if } V \le T \\ f_{\max} \tanh\left(\frac{g(V - T)}{f_{\max}}\right) & \text{if } V > T \end{cases}$$
  $$R(V) = [f(V) + T]^+$$
  where $T = 5 - 40\text{ mV}$, $f_{\max} = 50 - 60\text{ Hz}$, $g \in \{0.5, 0.7, 1.0, 1.5, 2.0, 3.0\}$.
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/Simulate.m:77–84`, `@Celltype/Celltype.m:75–78`.
- **Python Implementation**: `src/figure4_analysis.py:plot_panel_4a_tanh_gain_curves()`.

---

### Panel 4B: Descending Brainstem Terminal Projections
- **Scientific Question**: How are descending tract terminals anatomically distributed across spinal cord laminae and motor columns?
- **Tracts Mapped**:
  - `LPGIVglutL` / `LPGIVglutR`: Bilateral intermediate laminae targeting V2a, V0v, and V3.
  - `LPGIVglyL` / `LPGIVglyR`: Ventral inhibitory descending terminals.
  - `RapheObsL` / `RapheObsR`: Ventrolateral serotonergic terminals.
- **MATLAB Source**: `00_SpinalNetworkModel/@SpinalCordGeometry/SpinalCordGeometry.m:243–260`, `matDescending.mat`.
- **Python Implementation**: `src/figure4_analysis.py:plot_panel_4b_descending_tract_maps()`.

---

### Panel 4C: Speed Control via Descending Drive Acceleration Ramp
- **Scientific Question**: Does continuous increase in descending drive smoothly accelerate locomotor rhythm without disrupting traveling wave continuity?
- **Experimental Paradigm**: Linearly ramped descending current $I_e(t) = 15.0 + 35.0 \cdot \frac{t}{T_{\text{sim}}}\text{ pA}$ over $10\text{ s}$ ($10,000\text{ ms}$).
- **Observable**: Instantaneous frequency increases monotonically across the simulation.
- **MATLAB Source**: `Simulate.m` with 2D input matrix $I_e \in \mathbb{R}^{N \times t_{\text{steps}}}$.
- **Python Implementation**: `src/gait_control.py:simulate_descending_ramp()`, `src/figure4_analysis.py:plot_panel_4c_descending_ramp()`.

---

### Panel 4D: Multi-Gait Locomotor Patterns (Walking, Trotting, Bounding)
- **Scientific Question**: What are the distinct multi-muscle EMG signatures of walking, trotting, and bounding?
- **Synthetic EMG Generation**:
  $$\text{sig}_m(t) = \left( A_m(t) \cdot \frac{\xi_1(t)}{5} \cdot \text{Bernoulli}\left(\Phi\left(\text{zscore}(A_m(t))\right)\right) \right) + \xi_2(t) \cdot \sigma_{\text{noise}}$$
  $$\text{EMG}_m(t) = \text{movmean}(|\text{sig}_m(t)|, 20\text{ ms})$$
- **Muscles Displayed**:
  - Left & Right Tibialis Anterior (Ankle Flexor, Berg Blue `#377eb8`)
  - Left & Right Gastrocnemius (Ankle Extensor, Berg Orange `#ff7f00`)
  - Left & Right Vastus Medialis (Knee Extensor)
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/PlotEMG.m:21–76`.
- **Python Implementation**: `src/figure4_analysis.py:plot_panel_4d_gait_emg_patterns()`.

---

### Panel 4E: Polar Phase Transitions ($\pi \to 0$)
- **Scientific Question**: How does left-right and flexor-extensor coordination transition across gaits?
- **Equations**:
  $$\Delta \phi_{\text{L-R}} = \frac{t_{\text{peak, Right L2}} - t_{\text{peak, Left L2}}}{T_{\text{cycle}}} \times 2\pi \pmod{2\pi}$$
  $$\Delta \phi_{\text{F-E}} = \frac{t_{\text{peak, L5}} - t_{\text{peak, L2}}}{T_{\text{cycle}}} \times 2\pi \pmod{2\pi}$$
- **Key Result**:
  - Walking & Trotting: $\Delta \phi_{\text{L-R}} \approx 180^\circ$ ($\pi$).
  - Bounding: $\Delta \phi_{\text{L-R}} \approx 0^\circ$ ($0$).
  - Intralimb flexor-extensor phase $\Delta \phi_{\text{F-E}} \approx 180^\circ$ remains invariant across all gaits.
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/Network.m:80–95` (`ComputePhase`).
- **Python Implementation**: `src/figure4_analysis.py:plot_panel_4e_polar_phase_transitions()`.

---

### Panel 4F & 4G: Quantification of Frequency & Output Amplitude
- **Scientific Question**: What is the quantitative relationship between descending drive $I_e$, neuromodulatory gain $g$, locomotor frequency $f$, and muscle burst amplitude?
- **Parameter Sweep**: 10 descending drive points $I_e \in [15.0, 50.0]\text{ pA}$ across standard and 5-HT enhanced conditions.
- **Metrics**:
  - Frequency $f = \frac{1}{\text{mean}(\text{IPI})}$ (Hz).
  - RMS Amplitude: $\text{RMS} = \frac{1}{N}\sum_{i=1}^N \sqrt{\frac{1}{T}\sum_{t=1}^T (R_i(t) - \bar{R}_i)^2}$.
- **MATLAB Source**: Methods p. 12–13.
- **Python Implementation**: `src/gait_control.py:run_descending_drive_sweep()`, `src/figure4_analysis.py:plot_panel_4fg_frequency_amplitude()`.
