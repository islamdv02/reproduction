# Figure 3 Reproduction: Normal Locomotor Dynamics

This document details the exact mathematical formulation, parameters, and algorithms used to reproduce **Figure 3: Normal Locomotion Generation in the Mouse Spinal Projectome Model** from *Komi et al., Nature Communications, 2026*, referencing the original BergLab MATLAB codebase (`@Network`, `@SpinalCordGeometry`, `02_HelperFunctions`).

---

## 1. Simulation Configuration & Experimental Paradigm

- **Spinal Cord Segments**: 11 spinal segments ($T_{13}, L_1, L_2, L_3, L_4, L_5, L_6, S_1, S_2, S_3, S_4$)
- **Network Size**: $N = 5,229$ neurons (configured at relative density $D = 0.8$)
- **Synaptic Connectivity**: Symmetric ($Sym = 1$), row-wise balanced ($Balance = 1$), spatial Gaussian projection ($\sigma = 500\ \mu\text{m}$)
- **External Drive**: Tonic excitation $I_e(t) = 30.0\ \text{pA}$ across all neurons
- **Noise Drive**: Additive Gaussian white noise $\mathbf{I}_{\text{noise}}(t) \sim \mathcal{N}(0, \sigma_{\text{noise}}^2)$ with $\sigma_{\text{noise}} = 0.5$
- **Integration**: Forward Euler, $\Delta t = 1.0\ \text{ms}$, $\tau_V = 50.0\ \text{ms}$, $t_{\text{steps}} = 10,000\ \text{ms}$ (10 s)
- **Analysis Time Window**: Steady-state locomotion $t \in [1000, 10000]\ \text{ms}$ (1000 ms initial transient discarded)

---

## 2. Detailed Panel-by-Panel Specifications

### Panel 3a: 3D Anatomical Organization & Neural Network Layout
- **Description**: 3D spatial layout of the reconstructed spinal cord projectome ($T_{13}$ to $S_4$), showing individual neurons colored by cell type ($V1, V2a_1, V2a_2, V2b, V0d, V0v, dI6, V3, \text{MN}$).
- **Input Data**: 3D neuron coordinates $(X, Y, Z)$ from `SpinalDataLoader` and cell-type identities.
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/PlotDynamicsConnection3D.m`, lines 1–60.
- **Python Implementation**: `src/figure3_analysis.py:plot_panel_3a_network_3d()`

---

### Panel 3b & 3c: Population-Specific Firing Rates
- **Description**: Mean firing rate trajectories $R_{\text{pop}}(t)$ for the 9 ventral cell populations across time.
- **Equations**:
  $$R_{\text{pop}}(t) = \frac{1}{N_{\text{pop}}} \sum_{i \in \text{pop}} R_i(t)$$
- **Color Mapping**:
  - $V1$: `#377eb8` (Blue)
  - $V2a_1$: `#e41a1c` (Red)
  - $V2a_2$: `#ff7f00` (Orange)
  - $V2b$: `#984ea3` (Purple)
  - $V0d$: `#4daf4a` (Green)
  - $V0v$: `#a65628` (Brown)
  - $dI6$: `#f781bf` (Pink)
  - $V3$: `#666666` (Grey)
  - $\text{MN}$: `#1b9e77` (Teal)
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/PlotRates.m`, lines 1–44.
- **Python Implementation**: `src/figure3_analysis.py:plot_panel_3bc_population_rates()`

---

### Panel 3d: Motoneuron Pool Activity & Synthetic EMG Generation
- **Description**: Hindlimb muscle motoneuron pool firing rates and synthetic electromyographic (EMG) signals showing flexor-extensor and left-right reciprocal alternation with stance/swing phase shading.
- **Muscles Analyzed**:
  - **Flexors**: Iliopsoas (Hip Flexor), Tibialis Anterior (Ankle Flexor), Biceps Femoris (Knee Flexor)
  - **Extensors**: Quadriceps / Vastus Lateralis / Vastus Medialis (Knee Extensor), Gastrocnemius (Ankle Extensor)
- **Mathematical EMG Equation**:
  $$\text{prob}_m(t) = \sum_{i \in \text{MN}_m} R_i(t)$$
  $$\text{sig}_m(t) = \eta_1(t) \cdot \sigma_{\text{noise}} \cdot \text{Bernoulli}\left(\Phi\left(z(\text{prob}_m(t))\right)\right) \cdot \text{prob}_m(t) + \eta_2(t) \cdot \sigma_{\text{noise}}$$
  $$\text{Envelope}_m(t) = \text{movmean}(|\text{sig}_m(t)|, \text{window}=20\ \text{ms})$$
  where $\Phi(x) = \frac{1}{2}\left[1 + \text{erf}\left(\frac{x}{\sqrt{2}}\right)\right]$ is the Gaussian CDF, $z(x) = \frac{x - \mu_x}{\sigma_x}$, and $\eta_1, \eta_2 \sim \mathcal{N}(0, 1)$.
- **Stance/Swing Shading**: Determined by zero-crossings / derivative peaks of the reference extensor muscle *Vastus Medialis*.
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/PlotEMG.m`, lines 21–76.
- **Python Implementation**: `src/locomotion.py:generate_synthetic_emg()`, `src/figure3_analysis.py:plot_panel_3d_emg()`

---

### Panel 3e: Rostrocaudal Spatiotemporal Traveling Wave
- **Description**: Space-time raster and continuous heatmap of neural activity sorted along the rostrocaudal spinal cord axis ($Z$-coordinate from rostral $T_{13}$ to caudal $S_4$), demonstrating caudally directed traveling wave propagation.
- **Wave Propagation Velocity**:
  $$v_{\text{wave}} = \frac{\Delta Z}{\Delta t_{\text{lag}}} \approx 0.5\text{--}1.5\ \text{mm/s}$$
- **Phase Gradient**:
  $$\phi(Z) = \text{Phase}(R(t, Z)) = \text{mod}\left(\frac{2\pi \cdot \text{lag}(Z)}{T_{\text{cycle}}}, 2\pi\right)$$
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/PlotRaster.m`, lines 19–34; `02_HelperFunctions/ComputeFiringPhaseSorting.m`.
- **Python Implementation**: `src/locomotion.py:compute_traveling_wave()`, `src/figure3_analysis.py:plot_panel_3e_traveling_wave()`

---

### Panel 3f & 3g: Low-Dimensional Neural Manifold / PCA Rotational Dynamics
- **Description**: Dimensionality reduction via Principal Component Analysis (PCA) on population firing rates showing circular/elliptical rotational trajectories (limit cycles) in the PC1–PC2 and PC1–PC2–PC3 subspaces, with cumulative variance explained.
- **Equations**:
  $$\bar{\mathbf{R}} = \frac{1}{T} \sum_{t=1}^T \mathbf{R}(t)$$
  $$\tilde{\mathbf{R}} = \mathbf{R} - \bar{\mathbf{R}}$$
  $$\mathbf{C} = \frac{1}{T} \tilde{\mathbf{R}}^T \tilde{\mathbf{R}} = \mathbf{V} \mathbf{\Lambda} \mathbf{V}^T$$
  $$\mathbf{PC}(t) = \tilde{\mathbf{R}}(t) \mathbf{V}_{:, 1:3}$$
- **Variance Explained**: $V_{\text{exp}}(k) = \frac{\lambda_k}{\sum_j \lambda_j}$ (Typically $>70\%$ in top 3 PCs).
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/Network.m`, lines 96–118 (`ComputePC`); `02_HelperFunctions/PlotAnimatedNetworkEmgandPC.m`, lines 168–180.
- **Python Implementation**: `src/locomotion.py:compute_pca_dynamics()`, `src/figure3_analysis.py:plot_panel_3fg_pca_dynamics()`

---

### Panel 3h: Inter-Population Phase Relationships
- **Description**: Polar distribution and circular phase histograms of cell populations and left-right hemichords, validating antiphase left-right coordination ($\Delta \phi_{\text{L-R}} \approx \pi$) and flexor-extensor alternation ($\Delta \phi_{\text{F-E}} \approx \pi$).
- **MATLAB Source**: `00_SpinalNetworkModel/@Network/Network.m`, lines 80–95 (`ComputePhase`).
- **Python Implementation**: `src/locomotion.py:compute_population_phases()`, `src/figure3_analysis.py:plot_panel_3h_phase_relationships()`
