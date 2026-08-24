# Scientific Reproduction Plan: Komi et al. (Nature Communications, 2026)
## "Spatial and network principles behind neural generation of locomotion"

**Paper:** [https://doi.org/10.1038/s41467-026-74228-0](https://doi.org/10.1038/s41467-026-74228-0)  
**Original Code:** [https://github.com/BergLab/SpinalProjectome](https://github.com/BergLab/SpinalProjectome)  
**Authors:** Salif Komi, August Winther, Grace A. Houser, Thomas Topilko, R.J.F. Sørensen, Silas Dalum Larsen, Madelaine C. Adamsson Bonfils, Guanghui Li, Rune W. Berg (2026)

---

## Document Overview & Strict Grounding Rules
This reproduction plan documents every computational model, mathematical equation, parameter, algorithmic step, and analysis pipeline from Komi et al. (2026).
- Every item lists its exact source: **Paper Main Text**, **Methods**, **Supplementary Material**, or **Original Source Code**.
- Parameters explicitly reported in the text/methods are verified against the original MATLAB code.
- Parameters not explicitly stated in the paper text but present in the codebase are documented with their exact code location.
- No parameter has been invented or simplified.

---

## Table of Contents
1. [Computational Models Used in the Paper](#1-every-computational-model-used-in-the-paper)
2. [Important Mathematical Equations](#2-every-important-equation)
3. [Model Parameters Explicitly Reported & Code-Verified](#3-every-model-parameter-explicitly-reported)
4. [Network Sizes](#4-network-sizes)
5. [Excitatory / Inhibitory Proportions](#5-excitatory--inhibitory-proportions)
6. [Connection Probabilities](#6-connection-probabilities)
7. [Weight Distributions](#7-weight-distributions)
8. [Neuron Dynamics & Rate Equations](#8-neuron-dynamics--rate-equations)
9. [Spatial Organization Rules](#9-spatial-organization-rules)
10. [Mexican-Hat Connectivity Rules & Theory](#10-mexican-hat-connectivity-rules)
11. [Random-Network Construction & Spatial Unfolding](#11-random-network-construction)
12. [Mouse Spinal-Cord Network Construction (3D Lumbar/Sacral)](#12-mouse-spinal-cord-network-construction)
13. [Cell-Type Spatial Distributions](#13-cell-type-spatial-distributions)
14. [Projection Probabilities & Directional Kernels](#14-projection-probabilities)
15. [Descending Control Mechanisms](#15-descending-control-mechanisms)
16. [V0 Manipulation (Silencing & Ablation)](#16-v0-manipulation)
17. [Ablation Experiments (V1, V0, V2b, Lesion, Regrowth)](#17-ablation-experiments)
18. [PCA Analysis & Rotational Dynamics](#18-pca-analysis)
19. [Frequency Measurement](#19-frequency-measurement)
20. [Amplitude Measurement](#20-amplitude-measurement)
21. [Left-Right Phase Analysis](#21-left-right-phase-analysis)
22. [Ipsilateral L2–L5 Phase Analysis](#22-ipsilateral-l2l5-phase-analysis)
23. [All Figures and Quantitative Results to Reproduce](#23-all-figuresresults-that-we-should-reproduce)
24. [Implementation Architecture & Python Translation Roadmap](#24-implementation-architecture--python-translation-roadmap)

---

### 1. Every Computational Model Used in the Paper

1. **Model 1: Balanced Sequence Generator (BSG) / Random Recurrent Network**
   - **Description:** A non-spatial recurrent network of randomly connected excitatory and inhibitory units under local E/I balance ($\sum_j w_{ij} = 0$). Rhythms emerge as small-size finite-network effects when dominant eigenvalues exceed stability with non-zero imaginary component. Unfolded onto 1D space via phase-space coherence.
   - **Sources:**
     - Paper Main Text: Page 2, 8
     - Methods: Page 10 ("Random networks", "Spatial unfolding")
     - Supplementary Information: Supplementary Fig. 2A–G
     - Code: `00_SpinalNetworkModel/@Network/ComputeEigenModesandNullSpace.m`, `02_HelperFunctions/BalanceConnectivity.m`, `02_HelperFunctions/ComputeFiringPhaseSorting.m`

2. **Model 2: 1D Continuum Neural Field Model (Amari Formulation)**
   - **Description:** A theoretical 1D integro-differential neural field on periodic domain $\Omega = [0, 2\pi]$ with symmetric vs. asymmetric Mexican-hat interaction kernel $w(x - y)$ analyzing pattern formation, Turing instabilities, and traveling wave velocity.
   - **Sources:**
     - Paper Main Text: Page 2
     - Methods: Page 11 ("Wave propagation mechanism", Equations 1–3)
     - Supplementary Information: Supplementary Fig. 3

3. **Model 3: 1D Scaled 5-Subpopulation Mexican-Hat Network**
   - **Description:** A 1D spatially linear network discretized into 5 subpopulations (`sp1`, `sp2`, `sp3`, `sp4`, `sp5`), each assigned distinct projection length means ($\mu^p$) and widths ($\sigma^p$) forming an asymmetric Mexican-hat projectome. Tested across network sizes from $N=200$ to $N=10,000$.
   - **Sources:**
     - Paper Main Text: Page 2, Fig. 1E–H
     - Methods: Page 10–11 ("Scaling of networks")
     - Supplementary Information: Supplementary Fig. 2H–J, Supplementary Fig. 3
     - Code: `00_SpinalNetworkModel/@NetworkParameters/NetworkParameters.m`, `02_HelperFunctions/RescaleConnectivity.m`

4. **Model 4: Full 3D Mouse Spinal Cord Network Model (T13–S4 Lumbo-Sacral Cord)**
   - **Description:** A biologically grounded 3D network with realistic geometry (DV, ML, RC axes) incorporating 9 ventral cell types (excitatory: V2a-1, V2a-2, V0v, V3; inhibitory: V1, V2b, V0d, dI6; motoneurons: MN partitioned into flexor/extensor hindlimb motor pools). Synaptic connectivity is sampled from 3D anisotropic Gaussian probability clouds constrained by transcriptomic cell locations, layer constraints, and projection biases.
   - **Sources:**
     - Paper Main Text: Pages 2–7, Figs. 2, 3, 4, 5
     - Methods: Pages 11–14
     - Supplementary Information: Supplementary Figs. 4–12, Supplementary Table 1
     - Code: `InstantiateModel.m`, `00_SpinalNetworkModel/@Network/InstantiateNetwork.m`, `00_SpinalNetworkModel/@Network/Simulate.m`, `00_SpinalNetworkModel/@SpinalCordGeometry/SpinalCordGeometry.m`, `00_SpinalNetworkModel/@SpinalCordGenetics/SpinalCordGenetics.m`

---

### 2. Every Important Equation

#### A. Rate-Based Membrane Potential Dynamics
$$\tau_i \frac{d x_i(t)}{dt} = -x_i(t) + \sum_{j=1}^N w_{ij} F(x_j(t)) + I_i(t) + \epsilon_i(t)$$
- $x_i(t)$: Membrane input potential of neuron $i$ (mV).
- $\tau_i$: Membrane integration time constant ($\tau = 50\text{ ms}$; in BSG model: $\tau_I = 20\text{ ms}, \tau_E = 50\text{ ms}$).
- $w_{ij}$: Synaptic weight from presynaptic neuron $j$ to postsynaptic neuron $i$.
- $I_i(t)$: External tonic or descending input.
- $\epsilon_i(t) \sim \mathcal{N}(0, \sigma_{\text{noise}}^2)$: Zero-mean Gaussian noise term.
- Numerical integration: Forward Euler with time step $\Delta t = 1\text{ ms}$.
- **Sources:** Methods p. 10; Code: `00_SpinalNetworkModel/@Network/Simulate.m` (lines 59–69).

#### B. Compound Hyperbolic Tangent Activation Function $F(x)$
$$F(x) = \begin{cases} T \cdot \tanh\left( \frac{g(x - T)}{T} \right) + T, & \text{for } x \le T \\ f_{\max} \cdot \tanh\left( \frac{g(x - T)}{f_{\max}} \right) + T, & \text{for } x > T \end{cases}$$
- $T$: Firing threshold parameter (mV).
- $g$: Intrinsic neuronal gain (dimensionless slope).
- $f_{\max}$: Maximum saturation firing rate (Hz).
- $F(x) \ge 0$ strictly guarantees non-negative firing rates for all $x$.
- **Sources:** Methods p. 10; Supplementary Fig. 2B; Code: `Simulate.m` (lines 77–84).

#### C. Optional Spike Rate Adaptation Dynamics
When adaptation is enabled:
$$\tau_{a, i} \frac{d a_i(t)}{dt} = C_a R_i(t) - a_i(t)$$
$$R_i(t) = F(V_i(t) - a_i(t))$$
- $a_i(t)$: Adaptation variable.
- $C_a = 1.25$: Calcium/adaptation coupling factor.
- $\tau_a$: Adaptation time constant ($\tau_a = 3000\text{ ms}$ for Kcnn/SK-expressing neurons, $\tau_a = 10000\text{ ms}$ for non-expressing).
- **Sources:** Code: `Simulate.m` (lines 7–9, 18, 65–68).

#### D. Amari 1D Neural Field Model & Linear Stability Analysis
$$\frac{\partial u(x,t)}{\partial t} = -u(x,t) + \int_\Omega w(x - y) F(u(y,t))\, dy$$
Linearized perturbation $v(x,t) = u(x,t) - u_0$:
$$(\lambda + 1) v(x) = F'(u_0) \int_\Omega w(x - y) v(y)\, dy$$
Eigenfunction spectrum for spatial frequency $k$ ($v(x) = e^{ikx}$):
$$\lambda(k) = -1 + F'(u_0) \hat{w}(k)$$
- Symmetric $w(x) = w(-x) \implies \hat{w}(k) \in \mathbb{R} \implies$ stationary pattern/bump formation.
- Asymmetric $w(x) \ne w(-x) \implies \text{Im}(\hat{w}(k)) \ne 0 \implies$ traveling wave / oscillatory dynamics.
- **Sources:** Methods p. 11 (Equations 1–3).

#### E. 1D 5-Subpopulation Mexican-Hat Connection Probability
$$P_{\text{syn}}(i, j) = G_p \cdot \mathcal{N}\left( d_{ij} \mid \mu^{p(j)}, \sigma^{p(j)} \right), \quad d_{ij} = x_i - x_j \in [-L_N, L_N]$$
$$A(i, j) \sim \text{Binomial}\left( 1, P_{\text{syn}}(i, j) \right)$$
$$W = G \odot A, \quad G(i, j) \sim \mathcal{N}(1, 0.1)$$
$$\sum_{j=1}^N w_{ij} = 0 \quad \forall i$$
- **Sources:** Methods p. 11.

#### F. 3D Anisotropic Spatial Synaptic Probability
$$P_X^p(d_{X,ij}) \sim \mathcal{N}(\mu_X^p, \sigma_X^p), \quad P_Y^p(d_{Y,ij}) \sim \mathcal{N}(\mu_Y^p, \sigma_Y^p), \quad P_Z^p(d_{Z,ij}) \sim \mathcal{N}(\mu_Z^p, \sigma_Z^p)$$
$$P_{\text{syn}}(i, j) = \left( P_X^p(d_{X,ij}) \cdot P_Y^p(d_{Y,ij}) \cdot P_Z^p(d_{Z,ij}) \right)^{1/3}$$
Full combined probability in code:
$$\text{Prob}(i, j) = \left( \prod_{d \in \{ML, DV, RC\}} \frac{\mathcal{N}(\text{Bias}_d(i,j), 0, 1)}{\mathcal{N}(0, 0, 1)} \right)^{1/3} \cdot \text{BiasCI}_{ij} \cdot \text{BiasPop}_{ij} \cdot \text{BiasLay}_{ij} \cdot \text{BiasSeg}_{ij} \cdot \text{BiasMn}_{ij}$$
- **Sources:** Methods p. 12; Code: `00_SpinalNetworkModel/@Network/InstantiateNetwork.m` (line 189).

#### G. Hemicord-Specific Synaptic Balancing Rule
For each target neuron row $i$ in hemicord $H \in \{ \text{Left}, \text{Right} \}$:
$$S_i = \sum_{j \in H} w_{ij}, \quad S_i^+ = \sum_{j \in H, w_{ij} > 0} w_{ij}, \quad S_i^- = \sum_{j \in H, w_{ij} < 0} w_{ij}$$
$$f_i^+ = \frac{S_i^+ - S_i / 2}{S_i^+}, \quad f_i^- = \frac{S_i^- - S_i / 2}{S_i^-}$$
$$w_{ij} \leftarrow w_{ij} \cdot f_i^+ \quad (\text{if } w_{ij} > 0), \quad w_{ij} \leftarrow w_{ij} \cdot f_i^- \quad (\text{if } w_{ij} < 0)$$
Result: $\sum_{j \in H} w_{ij} = 0$ exactly.
- **Sources:** Methods p. 10; Code: `02_HelperFunctions/BalanceConnectivity.m` (lines 1–17).

#### H. Connectivity Matrix Rescaling
$$r = \frac{N_{\text{pos}}}{N_{\text{neg}}}, \quad S = \frac{N_{\text{zeros}}}{N^2}$$
$$W \leftarrow \frac{W}{\sqrt{S(1 - S)(1 + r^2) / 2} \cdot \sqrt{N}}$$
- **Sources:** Code: `02_HelperFunctions/RescaleConnectivity.m` (lines 1–8).

#### I. Cell Type–to–Cell Type Connectivity Metric $C_{ij}$
$$C_{ij} = \frac{\sum_{k \in \text{type } i,\, l \in \text{type } j} w_{kl}}{\sum_{k \in \text{type } i} w_k}$$
- **Sources:** Methods p. 13.

#### J. Population Root / Muscular Aggregate Readout ($A$)
$$A(t) = \sum_{j \in \text{Pool}} R_j(t)$$
Synthetic EMG signal with motor unit recruitment noise:
$$\text{sig}(t) = \left( A(t) \cdot \frac{\xi_1(t)}{5} \cdot \text{Binomial}\left(1, \Phi\left(\text{zscore}(A(t))\right)\right) \right) + \xi_2(t) \cdot \sigma_{\text{emg}}$$
$$\text{EMG}(t) = \text{movmean}(|\text{sig}(t)|, 20\text{ ms})$$
- $\xi_1, \xi_2 \sim \mathcal{N}(0, 1)$, $\sigma_{\text{emg}} = 0.1 - 0.2$.
- **Sources:** Methods p. 13; Code: `00_SpinalNetworkModel/@Network/PlotEMG.m`, `PlotNeurogram.m`.

#### K. Oscillation Frequency ($f$) & Amplitude ($\text{RMS}$)
$$f = \frac{1}{\text{IPI}}$$
$$\text{amplitude} \triangleq \frac{1}{N} \sum_{i=1}^N \sqrt{\frac{1}{T} \sum_{t=1}^T (R_{i}(t) - \bar{R}_i)^2}$$
- **Sources:** Methods p. 12–13.

---

### 3. Every Model Parameter Explicitly Reported

| Parameter Symbol | Description | Paper Value | Code Value | Exact Source |
| :--- | :--- | :--- | :--- | :--- |
| $\Delta t$ | Numerical integration Euler step | $1\text{ ms}$ | $1\text{ ms}$ (implicit $1\text{ step} = 1\text{ ms}$) | Methods p. 10; `Simulate.m` |
| $\tau$ (Standard) | Membrane time constant | $50\text{ ms}$ | `tau_V = 50` | Methods p. 10; `Simulate.m:5` |
| $\tau_E$ (BSG Model) | Excitatory time constant (BSG) | $50\text{ ms}$ | $50\text{ ms}$ | Methods p. 10 |
| $\tau_I$ (BSG Model) | Inhibitory time constant (BSG) | $20\text{ ms}$ | $20\text{ ms}$ | Methods p. 10 |
| $\sigma_{\text{noise}}$ | Noise standard deviation $\epsilon_i(t)$ | $0.4\text{ mV}$ | `noise_ampl = 0.5` | Methods p. 10; `Simulate.m:10` |
| $V_{\text{init}}$ | Initial membrane potential | UNKNOWN — NEED SOURCE CODE | `-70 mV` (std = $3\text{ mV}$) | `Simulate.m:13, 50` |
| $T$ | Compound tanh threshold | UNKNOWN — NEED SOURCE CODE | $40\text{ mV}$ (in `Celltype.m`) / $5\text{ mV}$ | `Celltype.m:77`, `NetworkParameters.m:33` |
| $g$ | Intrinsic activation gain | UNKNOWN — NEED SOURCE CODE | $0.7$ (in `Celltype.m`) / $1.0$ | `Celltype.m:75`, `NetworkParameters.m:31` |
| $f_{\max}$ | Max firing rate saturation | UNKNOWN — NEED SOURCE CODE | $60\text{ Hz}$ (in `Celltype.m`) / $50\text{ Hz}$ | `Celltype.m:76`, `NetworkParameters.m:32` |
| $I_e$ (Tonic Drive) | Constant baseline current | Fig. 4C: $25 - 30$ | `I_e = 30` (or `25`) | Paper Fig. 4C; `InstantiateModel.m:33` |
| $g_c$ | Global synaptic scale | UNKNOWN — NEED SOURCE CODE | $0.5$ | `InstantiateModel.m:6` |
| $D$ (Density) | Spatial sampling density factor | UNKNOWN — NEED SOURCE CODE | $0.8$ | `InstantiateModel.m:7` |
| `Symmetry` | Midline bilateral symmetry flag | UNKNOWN — NEED SOURCE CODE | $1$ (symmetric) | `InstantiateModel.m:8` |
| `Balance` | Row-wise E/I balancing flag | UNKNOWN — NEED SOURCE CODE | $1$ (balanced) | `InstantiateModel.m:9` |
| `ProjWidth` ($\sigma_{\text{spatial}}$) | Spatial projection std width | $500\ \mu\text{m}$ (tested 100–1700) | $500\ \mu\text{m}$ | Methods p. 15; `InstantiateModel.m:10` |
| $p_{\text{synapse}}$ (BSG) | Random network connection prob | $0.1$ | $0.1$ | Methods p. 10 |
| $\mu_w, \sigma_w$ (Weights) | Synaptic weight Gaussian draw | $\mu = 1.0, \sigma = 0.1$ | `normrnd(1, 0.1)` | Methods p. 10, 11; `InstantiateNetwork.m:200` |
| $C_a$ (Adaptation) | Calcium/rate coupling | UNKNOWN — NEED SOURCE CODE | $1.25$ | `Simulate.m:18` |
| $\tau_a$ (Kcnn+) | Adaptation time constant (Kcnn+) | UNKNOWN — NEED SOURCE CODE | $3000\text{ ms}$ | `Simulate.m:8` |
| $\tau_a$ (Kcnn-) | Adaptation time constant (Kcnn-) | UNKNOWN — NEED SOURCE CODE | $10000\text{ ms}$ | `Simulate.m:9` |

---

### 4. Network Sizes

1. **Random Recurrent Networks (BSG Model):**
   - $N = 500$ neurons ($n = 50$ network realizations generated).
   - Source: Methods p. 10 ("Random networks").

2. **1D Scaled Mexican-Hat Networks:**
   - $N \in \{200, 500, 1000, 2000, 5000, 10000\}$ neurons.
   - Uniform 1D line $[0, L_N]$.
   - Source: Methods p. 11 ("Scaling of networks").

3. **Mouse Lumbar/Sacral 3D Spinal Cord Model:**
   - Extent: 11 spinal segments (T13, L1, L2, L3, L4, L5, L6, S1, S2, S3, S4).
   - Total length: $\approx 11\text{ mm}$ (lumbar enlargement centered at L2–L5).
   - Neuron count: Set by density parameter $D = 0.8$ sampled across 9 cell types. Typical instantiated network size is $N \approx 800 - 1500$ neurons (depending on whether dorsal populations are masked out).
   - Network Sparsity: $97\%$ sparse ($0.97$).
   - Sources: Paper Main Text p. 4, Methods p. 11–12, Supplementary Fig. 6A–E; Code: `InstantiateModel.m`, `SpinalCordGeometry.m`.

---

### 5. Excitatory / Inhibitory Proportions

1. **Random Networks (BSG):**
   - Exactly $50\%$ Excitatory ($N/2 = 250$) and $50\%$ Inhibitory ($N/2 = 250$).
   - Source: Methods p. 10.

2. **1D 5-Subpopulation Network:**
   - 3 Excitatory subpopulations (`sp1`, `sp3`, `sp5`) and 2 Inhibitory subpopulations (`sp2`, `sp4`).
   - Uniform spatial density across $[0, L_N]$.
   - Source: Paper Fig. 1F, Methods p. 11.

3. **Mouse 3D Spinal Cord Model:**
   - Derived from snRNA-seq + spatial transcriptomics dataset (SeqSeek + GSE184370/GSE184369, 69 total neuronal populations: 38 excitatory, 28 inhibitory, 3 motoneuron-related).
   - Ventral locomotor circuit filtered to 9 major functional types:
     - **Excitatory (4 types):** V2a-1 (V2aNfib), V2a-2 (V2aZfhx), V0v, V3.
     - **Inhibitory (4 types):** V1, V2b, V0d, dI6.
     - **Motoneurons (1 class, 12 muscle pools):** MN (cholinergic/excitatory motor output).
   - Relative cell count fractions preserved from lumbar histological counts (Supplementary Fig. 6C).
   - Sources: Paper p. 3–4, Methods p. 11–12; Code: `SpinalCordGenetics.m`, `SpinalCordGeometry.m`.

---

### 6. Connection Probabilities

1. **BSG Model:**
   - Flat binomial probability $p_{\text{synapse}} = 0.1$ for every pair $(i, j), i \ne j$.
   - Source: Methods p. 10.

2. **1D 5-Subpopulation Model:**
   - $P_{\text{syn}}(i, j) = G_p \mathcal{N}(x_i - x_j \mid \mu^{p(j)}, \sigma^{p(j)})$.
   - Source: Methods p. 11.

3. **Mouse 3D Model:**
   - Multi-dimensional Gaussian product:
     $$P_{\text{syn}}(i, j) = \left( P_X(d_X) \cdot P_Y(d_Y) \cdot P_Z(d_Z) \right)^{1/3} \cdot \prod \text{Biases}$$
   - Distance terms:
     - RC: $d_X = -(x_i - x_j)$
     - ML: $d_Y = -( |y_i| - |y_j| )$
     - DV: $d_Z = -(z_i - z_j)$
   - Multiplicative bias modifiers:
     - $\text{BiasCI}$: Contralateral ($1$ if contra, $0$ if ipsi) or Ipsilateral ($1$ if ipsi, $0$ if contra).
     - $\text{BiasPop}$: Inter-population specific connection probability matrix (default $1.0$; Motoneuron feedback to interneurons reduced to $0.1$ via `SetCellBiasPop('MN', 'All', 0.1)`).
     - $\text{BiasLay}$: Laminar layer filter ($0.05$ if outside target layer).
     - $\text{BiasSeg}$: Segment filter ($0.5$ if outside target segment).
     - $\text{BiasMn}$: Motoneuron pool filter ($0.3$ if non-synergistic, $0.05$ if antagonistic).
   - Sources: Methods p. 12; Code: `InstantiateNetwork.m` (lines 48–190).

---

### 7. Weight Distributions

1. **Base Weight Sampling:**
   - $w_{ij} \sim \mathcal{N}(\mu = 1.0, \sigma = 0.1)$.
   - Excitatory columns: $w_{ij} = |w_{ij}| \cdot \text{SynStrength}_j$.
   - Inhibitory columns: $w_{ij} = -|w_{ij}| \cdot \text{SynStrength}_j$.
   - Self-synapses removed: $w_{ii} = 0$.
   - Source: Methods p. 10, 11; `InstantiateNetwork.m:200–205`.

2. **Synaptic Strengths per Cell Type (`SynStrength`):**
   - Global scale: $g_c = 0.5$.
   - V2a-2: $1.0 \times g_c = 0.5$
   - V2a-1: $1.0 \times g_c = 0.5$
   - V1: $0.2 \times g_c = 0.1$ (attenuated relative to other populations)
   - V2b: $1.0 \times g_c = 0.5$
   - V0d: $1.0 \times g_c = 0.5$
   - V0v: $1.0 \times g_c = 0.5$
   - dI6: $1.0 \times g_c = 0.5$
   - V3: $1.0 \times g_c = 0.5$
   - MN: $1.0 \times g_c = 0.5$ (with global target attenuation $0.1$)
   - Source: `InstantiateModel.m:16–27`.

3. **Balancing & Rescaling:**
   - Applied independently to left ($y < 0$) and right ($y > 0$) hemicord partitions:
     `Connectivity(SC.Latera > 0, :) = BalanceConnectivity(...)`
     `Connectivity(SC.Latera > 0, :) = RescaleConnectivity(...)`
   - Ensures each neuron receives zero net synaptic input on average ($\sum_j w_{ij} = 0$).
   - Sources: Methods p. 10; `BalanceConnectivity.m`, `RescaleConnectivity.m`.

---

### 8. Neuron Dynamics / Rate Equations

1. **Differential System:**
   $$\tau_i \dot{V}_i(t) = -V_i(t) + W R(t-1) + I_e(t) + \epsilon_i(t)$$
   $$R_i(t) = F(V_i(t) - a_i(t))$$

2. **Simulation Algorithm:**
   ```
   For t = 2 to t_steps:
       I_rec(:, t-1) = W * R(t-1, :)'
       I_tot(:, t-1) = I_rec(:, t-1) + I_noise(:, t-1) + I_e(:, t-1)
       dV = (-V(:, t-1) + I_tot(:, t-1)) / tau_V
       V(:, t) = V(:, t-1) + dV
       If Adaptation:
           da = (Ca * R(t-1, :)' - a(:, t-1)) / tau_a
           a(:, t) = a(:, t-1) + da
       R(t, :) = tanh_f_V(V(:, t) - a(:, t), threshold, gain, f_max)
   ```

3. **Poisson Spike Generation (for Raster / Neurogram):**
   $$R_{\text{norm}, i}(t) = \frac{R_i(t) - \min(R_i)}{\max(R_i) - \min(R_i)}$$
   $$\text{Spike}_i(t) \sim \text{Poisson}\left( \frac{R_{\text{norm}, i}(t)}{40} \right) > 0$$
   Gaussian convolution for instantaneous estimated rates: kernel width $w = 50\text{ ms}$, sampling rate $f_s = 1000\text{ Hz}$.
   - Sources: Methods p. 10; Code: `Simulate.m:59–74`, `Network.m:ComputeSpikes`, `GetGaussianFiring.m`.

---

### 9. Spatial Organization Rules

1. **Coordinate System:**
   - $X$-axis: Rostrocaudal (RC) axis ($0$ to $L_{\text{cord}} \approx 11,000\ \mu\text{m}$).
   - $Y$-axis: Mediolateral (ML) axis (Left $< 0$, Midline $= 0$, Right $> 0$, width $\approx 3500\ \mu\text{m}$).
   - $Z$-axis: Dorsoventral (DV) axis (Dorsal $> 0$, Ventral $< 0$, depth $\approx 2000\ \mu\text{m}$).

2. **Transcriptomic Voxels to Anatomical Coordinates:**
   - Spatial transcriptomics 2D coordinates scaled by conversion factor:
     $$\text{convfactor} = \frac{3500\ \mu\text{m}}{\text{range}(X_{\text{RCTD}})}$$
   - 3D coordinates constructed by assigning longitudinal $Z$-positions uniform within each segment length.
   - Spinal white matter (WM) and grey matter (GM) alpha-shapes generated to enforce physical cord boundaries.
   - Sources: Methods p. 11–12; Code: `SpinalCordGeometry.m:46–48, 206–225`.

3. **Hindlimb Motor Pool Stereotaxy:**
   - 12 Hindlimb motoneuron pools mapped across T13–S4:
     - L1–L2: Iliopsoas (`Ilio`, flexor), Vastus Medialis (`VM`, extensor), Vastus Lateralis (`VLat`, extensor).
     - L2–L4: Rectus Femoris (`RF`), Quadriceps (`Q`).
     - L3–L5: Tibialis Anterior (`TA`, flexor), Biceps Femoris (`BF`, flexor/extensor).
     - L4–L5: Gluteus (`GM`/`Glut`, extensor).
     - L5–S1: Soleus (`Sol`, extensor), Gastrocnemius (`GM`, extensor), Plantaris (`PF`), Extensor Digitorum Longus (`EdL`).
     - S2–S4: Tail muscles.
   - Sources: Paper Fig. 2D, Methods p. 13; `matMuscleSeg.mat`, `MotorneuronsDistribution.xlsx`.

---

### 10. Mexican-Hat Connectivity Rules

1. **Principle:**
   - Local net positive excitation within $\approx \pm 500\ \mu\text{m}$ of soma.
   - Longer-range net negative inhibition flanking the central lobe ($1000 - 4000\ \mu\text{m}$).
   - Longitudinal rostrocaudal skew (asymmetric projection lengths) creating directional drive.

2. **Projectome Definition:**
   $$\text{Projectome}(\Delta z) = \sum_{j \in \text{Pop}} w_{ij}(\Delta z) = \text{Excitation}(\Delta z) - \text{Inhibition}(\Delta z)$$
   - Ipsilateral Projectome: Mexican-hat shaped with rostral/caudal asymmetry.
   - Contralateral Projectome: Commissural projections regulating left-right alternation vs. synchrony.

3. **Symmetry vs. Wave Propagation:**
   - Asymmetric Mexican-hat: Generates propagating activity bumps ($\text{Im}(\lambda) > 0$, traveling wave).
   - Inverted Mexican-hat: Can oscillate, but unable to stably arrest/stop locomotion.
   - Non-Mexican-hat (pure local excitation + symmetric reciprocal inhibition): Fails to generate rostrocaudal traveling waves.
   - Sources: Paper Main Text p. 2, Fig. 1E–H, Methods p. 11, Supplementary Figs. 3, 9.

---

### 11. Random-Network Construction

1. **Generation Protocol:**
   - Size $N = 500$ ($250$ E, $250$ I).
   - Connection draw: $A_{ij} \sim \text{Bernoulli}(p = 0.1)$.
   - Weights: $w_{ij} \sim \mathcal{N}(1, 0.1)$, Dale's law enforced, $w_{ii} = 0$.
   - Row-balancing: $\sum_j w_{ij} = 0$.

2. **Phase-Space Unfolding Algorithm:**
   - Perform PCA on population rates $R(t)$.
   - Take 1st principal component $s_1(t)$.
   - For each neuron $i$, compute cross-correlation $C_{i}(\tau) = \text{xcorr}(s_1, R_i)$ and find peak lag $L_i$.
   - Compute dominant cycle period $T_{\text{cycle}}$ from autocorrelation peaks.
   - Assign 1D phase coordinate $\theta_i = \left( \frac{L_i \cdot 2\pi}{T_{\text{cycle}}} \right) \pmod{2\pi}$.
   - Sort neurons along line by $\theta_i$.
   - Result: Emergence of the asymmetric Mexican-hat connectivity profile.
   - Sources: Methods p. 10; `ComputeFiringPhaseSorting.m`, `Network.m:ComputePhase`.

---

### 12. Mouse Spinal-Cord Network Construction

1. **Transcriptomic Lineage Extraction:**
   - 69 cell populations identified by RCTD from single-nucleus RNA-seq (SeqSeek/GSE184370) and spatial transcriptomics (GSE184369).
   - Filtered for ventral horn laminae (excluding dorsal horn sensory interneurons).

2. **3D Neuron Sampling:**
   - For each cell type $p$, sample somatic coordinates $(x_i, y_i)$ from spatial density $P_p(x, y)$ using rejection/binomial sampling with $z$-score threshold $> 1.0$ and outlier removal (`rmoutliers`).
   - Sample longitudinal coordinate $z_i \sim \mathcal{U}(z_{\text{seg, min}}, z_{\text{seg, max}})$.
   - Assign motoneurons to motor pools according to `MuscleSeg` density.

3. **Connectivity Instantiation:**
   - Compute 3D pairwise distances $d_X, d_Y, d_Z$.
   - Evaluate directional bias kernels for RC, ML, DV, CI, layers, segments, motor pools.
   - Multiply by population probability bias matrix `BiasPop`.
   - Sample binary adjacency $A_{ij} \sim \text{Binomial}(1, \text{Prob}_{ij})$.
   - Sample Gaussian weights, apply Dale's sign, zero diagonals.
   - Balance left and right hemicords independently.
   - Rescale connectivity by theoretical matrix norm factor.
   - Compute eigenspectrum and dominant eigenmodes.
   - Sources: Methods p. 11–12; Code: `InstantiateNetwork.m`, `SpinalCordGeometry.m`.

---

### 13. Cell-Type Spatial Distributions

| Cell Type | Neurotransmitter | Ventral/Dorsal Layer | Mediolateral | Genetic Markers | References |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **V2a-1 (V2aNfib)** | Glutamatergic (+) | Intermediate (Laminae VII/VIII) | Medial | `Vsx2/Chx10`, `Nfib`, `Neurod2` | Kathe et al. 2022; Russ et al. 2021 |
| **V2a-2 (V2aZfhx)** | Glutamatergic (+) | Intermediate (Laminae VII/VIII) | Lateral | `Vsx2/Chx10`, `Zfhx3`, `Foxp2` | Kathe et al. 2022; Osseward et al. 2021 |
| **V0v** | Glutamatergic (+) | Ventral (Lamina VIII) | Medial | `Evx1`, `Pitx2` | Moran-Rivard et al. 2001 |
| **V3** | Glutamatergic (+) | Ventromedial (Lamina VIII) | Ventrolateral | `Sim1` | Zhang et al. 2008; Deska-Gauthier 2024 |
| **V1** | GABA/Glycinergic (-) | Ventrolateral (Laminae VII/IX) | Lateral | `En1`, `Foxd3` | Gosgnach et al. 2006; Britz et al. 2015 |
| **V2b** | GABA/Glycinergic (-) | Ventrolateral (Lamina VII) | Lateral | `Gata2/3`, `Foxp2` | Britz et al. 2015; Callahan et al. 2019 |
| **V0d** | GABA/Glycinergic (-) | Ventral/Medial (Lamina VIII) | Medial | `Evx1`, `Pax7` | Talpalar et al. 2013 |
| **dI6** | GABA/Glycinergic (-) | Ventromedial (Lamina VIII) | Medial | `Wt1`, `Dmrt3` | Andersson et al. 2012 |
| **MN** | Cholinergic (+) | Ventral Horn (Lamina IX) | Motor columns | `ChAT`, `Isl1`, `Mnx1/Hb9` | Bácskai et al. 2014 |

- Sources: Paper Fig. 2A–C, Methods p. 11–12, Supplementary Fig. 4, 6; Code: `04_Utilities/CellTypesCensus.xlsx`, `SpinalCordGenetics.m`.

---

### 14. Projection Probabilities & Directional Kernels

Parameters configured in `InstantiateModel.m` and `InstantiateNetwork.m`:

| Cell Type | Bias RC | Bias DV | Bias ML | Bias MN | Bias Contra/Ipsi | LengthScale ($\mu_p$) | SynStrength ($g_c \times$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **V2a-2** | Bilateral (`bi`) | Ventral (`ven`) | Lateral (`lat`) | None (`''`) | Ipsilateral (`ipsi`) | $7000\ \mu\text{m}$ | $1.0 \times g_c$ |
| **V2a-1** | Caudal (`cau`) | Ventral (`ven`) | Medial (`med`) | None (`''`) | Ipsilateral (`ipsi`) | $500\ \mu\text{m}$ | $1.0 \times g_c$ |
| **V1** | Rostral (`ro`) | Ventral (`ven`) | None (`''`) | None (`''`) | Ipsilateral (`ipsi`) | $2000\ \mu\text{m}$ | $0.2 \times g_c$ |
| **V2b** | Caudal (`cau`) | Ventral (`ven`) | Lateral (`lat`) | None (`''`) | Ipsilateral (`ipsi`) | $4000\ \mu\text{m}$ | $1.0 \times g_c$ |
| **V0d** | Local (`loc`) | Ventral (`ven`) | Medial (`med`) | None (`''`) | Contralateral (`contra`) | $500\ \mu\text{m}$ | $1.0 \times g_c$ |
| **V0v** | Rostral (`ro`) | Local (`loc`) | Medial (`med`) | None (`''`) | Contralateral (`contra`) | $3400\ \mu\text{m}$ | $1.0 \times g_c$ |
| **dI6** | Caudal (`cau`) | Dorsal (`dor`) | Medial (`med`) | None (`''`) | Contralateral (`contra`) | $5000\ \mu\text{m}$ | $1.0 \times g_c$ |
| **V3** | Caudal (`cau`) | Ventral (`ven`) | Lateral (`lat`) | None (`''`) | Contralateral (`contra`) | $500\ \mu\text{m}$ | $1.0 \times g_c$ |
| **MN** | Local (`loc`) | Ventral (`ven`) | Lateral (`lat`) | None (`''`) | Ipsilateral (`ipsi`) | $300\ \mu\text{m}$ | $1.0 \times g_c$ (targets: $0.1$) |

- Spatial std width parameter: `ProjWidth` = $500\ \mu\text{m}$.
- Sources: Paper Fig. 2C, Supplementary Table 1; `InstantiateModel.m:16–27`.

---

### 15. Descending Control Mechanisms

1. **Glutamatergic Drive (LPGi):**
   - Source: Lateral Paragigantocellular Nucleus (`LPGi`) in caudal medulla.
   - Terminal localization: Intermediate laminae (V2a, V0v, V3).
   - Mechanism: Additive increase in excitatory input current $I_e(t)$ from $0$ to $30\text{ pA}$.

2. **Serotonergic Drive (Raphe Nuclei: Mg, Ob):**
   - Source: Raphe Magnus (`Mg`) and Raphe Obscurus (`Ob`).
   - Terminal localization: Ventrolateral spinal cord.
   - Receptor targets:
     - 5-HT7 expressing neurons (V2a, V1, V2b): Gain multiplication $g \leftarrow g \cdot (1 + \alpha_{\text{5HT}})$, range $g \in [0.5, 3.0]$.
     - 5-HT1b expressing neurons: Gain attenuation.

3. **Gait Transitions (Walking $\to$ Trotting $\to$ Bounding):**
   - Low 5-HT / low LPGi drive: Symmetrical ipsilateral projectome + long-range contralateral excitation $\implies$ Slow walking ($\sim 2\text{ Hz}$, left-right alternation, $\Delta \phi \approx \pi$).
   - Medium drive: Trotting ($\sim 4\text{ Hz}$, left-right alternation).
   - High 5-HT / high LPGi drive: Asymmetric ipsilateral projectome + local contralateral excitation / long-range inhibition $\implies$ Dominant eigenvalue mode swaps from Mode 1 to Mode 2 $\implies$ Bounding ($\sim 6 - 8\text{ Hz}$, left-right synchrony, $\Delta \phi \approx 0$).
   - Sources: Paper Main Text p. 5–6, Fig. 4, Supplementary Fig. 11.

---

### 16. V0 Manipulation (Silencing & Ablation)

1. **Silencing (Hyperpolarization):**
   - Implemented as tonic inhibitory bias current $I_{\text{hyper}} = -30\text{ pA}$ or zeroing synaptic gain on V0 populations (V0v and V0d).
   - Result: Frequency increases; right-left L2 phase switches from $\pi$ (alternation) to $0$ (synchrony / hopping).

2. **Genetic Ablation:**
   - Removal of V0v and V0d from the network ($W_{:, \text{V0}} = 0, W_{\text{V0}, :} = 0$).
   - Result: Hopping gait across all frequencies; ipsilateral L2–L5 flexor-extensor alternation remains intact.
   - Sources: Paper Main Text p. 7–8, Fig. 5D–F.

---

### 17. Ablation Experiments

1. **V1 Silencing & Ablation:**
   - Manipulation: Hyperpolarization or removal of V1 interneurons.
   - Effect: Slowdown of locomotor rhythm (frequency decreases from $\sim 2.5\text{ Hz}$ to $\sim 1.0\text{ Hz}$); burst amplitude increases (hyperflexion phenotype); L–R and L2–L5 phase coordination preserved.
   - Mechanism: Loss of rostral inhibitory lobe ($sp_2$) delays caudal activity bump propagation.
   - Sources: Paper Fig. 5A–C.

2. **V2b Silencing & Dual V1+V2b Ablation:**
   - Silencing V2b: Loss of caudal inhibition, increase in amplitude.
   - Silencing both V1 and V2b: Uncontrolled spread of excitation, collapse of flexor-extensor alternation.
   - Sources: Paper Main Text p. 7.

3. **Structural Lesion & Targeted Regrowth:**
   - Lesion: Modeled by `MakeLesion(ypos)` zeroing connections crossing transection level $y_{\text{pos}}$.
   - Regrowth: `RegrowPop(pop)` selectively restoring synaptic weights of a targeted cell type across the lesion site.
   - Sources: Paper Main Text p. 9; `MakeLesion.m`, `RegrowPop.m`.

---

### 18. PCA Analysis & Rotational Dynamics

1. **Mathematical Pipeline:**
   - Rate matrix $R \in \mathbb{R}^{T \times N}$ centered: $\tilde{R} = R - \bar{R}$.
   - Covariance $C = \frac{1}{T} \tilde{R}^T \tilde{R} \in \mathbb{R}^{N \times N}$.
   - Eigen-decomposition: $C U_n = \lambda_n U_n$, sorted by descending eigenvalue $\lambda_n$.
   - Projected PC coordinates: $P_{\text{PC}} = \tilde{R} U \in \mathbb{R}^{T \times K}$.

2. **Rotational Metric & Phase Representation:**
   - Trajectories plotted in PC1–PC2 or PC1–PC2–PC3 subspace.
   - Circular orbits demonstrate rotational dynamics without pacemaker cells.
   - Radius in PC space reflects population burst amplitude.
   - Sources: Methods p. 12; `Network.m:ComputePC`, `PlotAnimatedNetworkEmgandPC.m`.

---

### 19. Frequency Measurement

1. **Inter-Peak Interval (IPI) on PC1:**
   - Project firing rates onto 1st principal component $P_1(t)$.
   - Detect peaks using `findpeaks(P_1)`.
   - Inter-peak intervals: $\text{IPI} = \text{mean}(\text{diff}(t_{\text{peaks}}))$.
   - Frequency: $f = \frac{1}{\text{IPI}}$ (Hz).

2. **Spectral Eigenspectrum Frequency:**
   - Dominant eigenvalue $\lambda_{\text{dom}} = \sigma + i \omega$.
   - Predicted oscillation frequency: $f_{\text{spectral}} = \frac{|\omega|}{2\pi \cdot \tau}$.
   - Sources: Methods p. 12–13; `ComputeEigenModesandNullSpace.m`.

---

### 20. Amplitude Measurement

1. **Root-Mean-Square (RMS) Amplitude:**
   $$\text{amplitude} \triangleq \frac{1}{N} \sum_{i=1}^N \sqrt{\frac{1}{T} \sum_{t=1}^T (R_i(t) - \bar{R}_i)^2}$$

2. **Root & Muscle Peak Amplitude:**
   - Mean envelope height of aggregate motoneuron firing $A(t) = \sum_{j \in \text{Pool}} R_j(t)$ for L2, L5, TA, GM, VM, BF.
   - Sources: Methods p. 13; `PlotNeurogram.m`, `PlotEMG.m`.

---

### 21. Left-Right Phase Analysis

1. **Metric:**
   - Cross-correlation or peak-to-peak phase lag between Left L2 motor pool and Right L2 motor pool:
     $$\Delta \phi_{\text{L-R}} = \frac{t_{\text{peak, Right L2}} - t_{\text{peak, Left L2}}}{T_{\text{cycle}}} \times 2\pi \pmod{2\pi}$$
   - Polar plots display mean vector angle and circular variance ($R$-value).
   - Alternation (Walking): $\Delta \phi \approx \pi$ ($180^\circ$).
   - Synchrony (Bounding / Hopping / V0 ablation): $\Delta \phi \approx 0$ ($0^\circ$).
   - Sources: Paper Fig. 3D, Fig. 4E, Fig. 5C, F, Methods p. 13.

---

### 22. Ipsilateral L2–L5 Phase Analysis

1. **Metric:**
   - Phase difference between ipsilateral L2 (flexor-dominant) and ipsilateral L5 (extensor-dominant) segmental motor outputs:
     $$\Delta \phi_{\text{L2-L5}} = \frac{t_{\text{peak, L5}} - t_{\text{peak, L2}}}{T_{\text{cycle}}} \times 2\pi \pmod{2\pi}$$
   - Measures intralimb flexor-extensor coordination.
   - Robust out-of-phase alternation ($\Delta \phi \approx 0.75\pi - \pi$) maintained across control, V1 silencing, and V0 ablation.
   - Sources: Paper Fig. 3D, Fig. 4E, Fig. 5C, F, Methods p. 13.

---

### 23. All Figures/Results That We Should Reproduce

| Target Figure | Specific Panels & Scientific Results | Computational Pipeline Required |
| :--- | :--- | :--- |
| **Figure 1** | **1D–E:** Unfolded 1D BSG Mexican-hat projectome & connectivity matrix.<br>**1F:** 5-subpopulation decomposition ($sp_1 - sp_5$).<br>**1G:** sp3 gain modulation $\implies$ selective amplitude increase; PC1–PC2 orbit expansion.<br>**1H:** sp2 gain modulation $\implies$ selective frequency control; preserved PC orbit radius. | Random network simulation, phase unfolding, 1D 5-pop rate simulation, gain sweep, PCA, frequency/amplitude extraction. |
| **Figure 2** | **2C:** 3D Gaussian projection kernels along RC, ML, DV axes for 9 ventral types.<br>**2D:** Hindlimb motoneuron pool segmental localization (T13–S4).<br>**2E:** $N \times N$ pairwise connectivity matrix and ipsi/contra decomposition.<br>**2F:** Cell type–cell type normalized connectivity matrix $C_{ij}$.<br>**2G:** Net lumbar spinal projectome (ipsi & contra Mexican-hat profiles). | Spatial transcriptomics sampling, 3D kernel synthesis, binomial adjacency generation, E/I balancing, projectome spatial binning. |
| **Figure 3** | **3A:** Eigenspectrum of $W$ showing oscillatory Modes 1 & 2.<br>**3B:** Spatial eigenvector profiles across segments and antagonist muscle pairs (VM-BF, TA-GM).<br>**3C:** Spatiotemporal traveling activity waves ($I_e = 30\text{ pA}$), muscle EMG envelopes, segmental neurograms.<br>**3D:** Polar phase plots (L–R L2 phase, ipsilateral L2–L5 phase).<br>**3E:** Continuous phase distribution (rotational dynamic proof).<br>**3F:** 2D/3D PCA rotational trajectory. | Full 3D network simulation ($10\text{ s}$), linear spectral analysis, EMG envelope filtering, cross-correlation phase extraction, PCA. |
| **Figure 4** | **4A:** Compound tanh gain modulation curves.<br>**4B:** Descending terminal maps: glutamatergic drive from LPGi and serotonergic drive from Raphe nuclei (Mg, Ob) targeting specific laminae and receptor subtypes (5-HT7, 5-HT1b).<br>**4C:** Descending input ramp ($I_{\text{LPGi}}$, $g_{\text{5HT}}$) and effective projectome modulation.<br>**4D:** Locomotor gait patterns: walking, trotting, bounding.<br>**4E:** Polar phase transitions ($\pi \to 0$).<br>**4F–G:** Locomotor frequency and muscle/nerve amplitude quantification across gaits. | Descending drive parameter sweep, dynamic projectome recalculation, multi-gait simulation, polar phase quantification. |
| **Figure 5** | **5A–C:** V1 silencing & ablation: rostral lobe attenuation, frequency slowdown, burst amplitude increase, preserved L–R & L2–L5 phase.<br>**5D–F:** V0 silencing & ablation: contralateral projectome alteration, frequency increase, L–R phase switch to synchrony (hopping), preserved L2–L5 phase. | Perturbation simulations ($V_1$ hyperpol/ablation, $V_0$ hyperpol/ablation), before/after neurograms, circular phase statistics, bar charts. |
| **Supplementary Figs** | **S2:** BSG eigenspectrum scaling collapse.<br>**S3:** 5-pop Mexican-hat parameter space.<br>**S4–S6:** Transcriptomic mapping, segmental cell counts, sparsity ($0.97$).<br>**S7:** TA/GM premotor interneuron distribution.<br>**S8:** Resilience to transverse scrambling vs sensitivity to motoneuron pool RC position.<br>**S9–S11:** 500-projectome parameter search, UMAP clustering, and descending eigenspectrum mode swaps.<br>**S12:** Margin of Stability $M$ & dominant mode variability $\Delta R / R$ vs density/projection width. | Scaling simulations ($N=200..10000$), transverse scrambling test, motoneuron RC permutation test, stability analysis. |

---

### 24. Implementation Architecture & Python Translation Roadmap

To achieve an independent, production-grade scientific reproduction without MATLAB dependency, the reproduction will be implemented in Python (using NumPy, SciPy, Matplotlib, scikit-learn, Pandas) matching the exact object-oriented architecture:

```
spinal_projectome_reproduction/
├── REPRODUCTION_PLAN.md                     # Detailed scientific blueprint
├── data/                                    # Extracted geometry & transcriptomics (.mat/.json)
│   ├── matGeometry.mat
│   ├── matDescending.mat
│   ├── matMuscleSeg.mat
│   └── matCellInfo.mat
├── src/
│   ├── __init__.py
│   ├── celltype.py                          # CellType definitions & spatial bias parameters
│   ├── network_parameters.py                # Parameter container & cell-to-cell bias manager
│   ├── spinal_geometry.py                   # 3D coordinate sampling & motor pool placement
│   ├── network.py                           # Network construction, adjacency, balancing, rescaling
│   ├── simulation.py                        # Euler rate-based ODE solver & compound tanh activation
│   ├── spectral_analysis.py                 # Eigenspectrum, dominant modes & stability analysis
│   ├── analyses.py                          # PCA, IPI frequency, RMS amplitude, polar phase metrics
│   └── visualization.py                     # 3D spatial scatters, neurograms, EMGs, polar plots
├── tests/
│   ├── test_rate_dynamics.py                # Unit test: compound tanh, Euler step, zero-mean balance
│   ├── test_connectivity.py                 # Unit test: Mexican-hat profile, sparsity, symmetry
│   └── test_eigenspectrum.py                # Unit test: Mode 1/2 stability & oscillatory frequencies
└── reproduce_all_figures.py                 # Master reproduction pipeline generating Figures 1–5
```

---
*End of REPRODUCTION_PLAN.md. Ready for user review.*
