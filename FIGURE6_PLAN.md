# Figure 6 Scientific Reproduction Plan: Spinal Cord Lesion, Targeted Axonal Regrowth, and High-Density Electrophysiology

**Paper Title**: *A spatial-projectome-based neural network model for speed and gait control in the spinal cord*  
**Citation**: Komi et al., *Nature Communications*, 2026  
**Original Repository**: BergLab MATLAB Codebase (`@Network/MakeLesion.m`, `@Network/RegrowPop.m`, `@Network/Simulate.m`, `02_HelperFunctions/PositionElectrodeAndSample3D.m`, `@Network/ComputeSpikes.m`, `@Network/ComputeEstimatedRates.m`)  
**Reproduction Stage**: Step 7 (Figure 6: Scientific Analysis & Implementation Blueprint)  
**Status**: 📋 **Scientific Analysis & Blueprint (Pre-Implementation)**  

---

## 1. Scientific Question Addressed by Figure 6

Figure 6 investigates the structural vulnerability and restorative capacity of the spinal projectome, as well as its validation against high-density in vivo electrophysiological recordings:

1. **Structural Lesion (Spinal Cord Injury / Transection)**:  
   *Scientific Question*: What happens to the emergent traveling wave dynamics and multi-muscle coordination when long-range axonal pathways are severed by a transverse spinal cord lesion?  
   *Hypothesis*: Because the Mexican-hat projectome relies on continuous rostrocaudal asymmetry ($\mu_{\text{RC}}$) to generate directional phase progression, a transverse lesion severs crossing axons ($W_{ij} = 0$), breaking traveling wave propagation across the lesion site and decoupling or silencing the sub-lesional motor pools.

2. **Targeted Axonal Regrowth (Cell-Type Specific Reinnervation)**:  
   *Scientific Question*: Which genetically defined neuronal populations are necessary and sufficient to restore coordinated locomotor traveling waves and bilateral motor bursts across a lesion gap upon targeted axonal regeneration?  
   *Hypothesis*: Only populations with long-range longitudinal projection architectures (specifically excitatory V2a-2 interneurons with $\mu = 7,000\ \mu\text{m}$) possess the spatial reach and asymmetric excitation needed to re-establish the Mexican-hat projectome and bridge traveling waves across the lesion site. Local interneurons or inhibitory populations fail to restore coordinated propulsion.

3. **High-Density Electrophysiological Validation (Silicon Probe / Neuropixels Sampling)**:  
   *Scientific Question*: How does the continuous 3D network model translate into physical multi-electrode recordings, and does simulated multi-channel spiking match the sequential phase progression observed with high-density silicon probes in vivo?  
   *Hypothesis*: Virtual insertion of multi-channel linear probes / Neuropixels shanks into the 3D lumbar cord captures the rostrocaudal/dorsoventral phase delays of propagating activity waves, demonstrating that spatial-temporal sequence activation is directly measurable on physical recording channels.

---

## 2. Experimental Paradigms & Target Populations

| Paradigm | Component / Population | Transmitter | Axon Projection & Bias | Target Manipulation |
| :--- | :--- | :--- | :--- | :--- |
| **Intact Control** | All 11 populations ($N=5,229$) | Full E/I balance | Full 3D anisotropic projectome | Baseline simulation ($I_e = 30.0\text{ pA}$, trot regime) |
| **Transverse Lesion** | All crossing axons ($z_i < z_{\text{lesion}} < z_j$ or $z_j < z_{\text{lesion}} < z_i$) | All types | Cross-lesion connections severed | Structural zeroing: $W_{ij} = 0$ for all pairs crossing $z_{\text{lesion}}$ |
| **V2a-2 Regrowth** | V2a-2 excitatory interneurons | Glutamatergic ($+1$) | Long-range bilateral ($\mu = 7,000\ \mu\text{m}$, lateral) | Selective restoration: $W_{\text{restored}} = \text{mean}(\|W_{\text{V2a-2}}\|)$ |
| **V1 Regrowth** | V1 inhibitory interneurons | GABA/Glycinergic ($-1$) | Rostral inhibitory lobe ($\mu = 2,000\ \mu\text{m}$, lateral) | Selective restoration: $W_{\text{restored}} = \text{mean}(\|W_{\text{V1}}\|)$ |
| **V0v / V3 Regrowth** | V0v / V3 commissural neurons | Glutamatergic ($+1$) | Contralateral rostral/caudal ($\mu = 3,400 / 500\ \mu\text{m}$) | Selective restoration across midline / lesion |
| **Probe Recording** | High-density linear probe (32-ch / Neuropixels) | Extracellular readout | Spatial detection radius $r \le 50\ \mu\text{m}$ | Virtual electrode insertion & Poisson spike sampling |

---

## 3. Mathematical Formulations & MATLAB Source Mapping

### 3.1 Structural Lesion Operator (`MakeLesion.m`)
In BergLab's MATLAB implementation (`@Network/MakeLesion.m`), a transverse lesion at rostrocaudal position $z_{\text{lesion}}$ is defined by identifying all neuron pairs where one soma lies rostral to $z_{\text{lesion}}$ and the other lies caudal to $z_{\text{lesion}}$:
$$\text{Source}_i = (z_i < z_{\text{lesion}}) \land \text{Filter}_i$$
$$\text{Target}_j = (z_j > z_{\text{lesion}}) \land \text{Filter}_j$$
$$\text{LesionMask}_{ij} = (\text{Source}_i \land \text{Target}_j \lor \text{Target}_i \land \text{Source}_j) \land (W_{ij} \ne 0)$$
$$W_{ij} \leftarrow 0 \quad \forall (i, j) \in \text{LesionMask}$$

### 3.2 Targeted Axonal Regrowth Operator (`RegrowPop.m`)
In BergLab's MATLAB implementation (`@Network/RegrowPop.m`), selective axonal regrowth of a specific population $P_{\text{target}}$ restores severed connections in the lesion mask:
$$\text{RestoreMask}_{ij} = \text{LesionMask}_{ij} \land (\text{Type}_j = P_{\text{target}})$$
$$W_{ij} \leftarrow \text{mean}\left( |W_{kl}| \mid \text{Type}_l = P_{\text{target}}, W_{kl} \ne 0 \right) \cdot \text{sign}(\text{Transmitter}_{P_{\text{target}}})$$
$$\text{LesionMask}_{ij} \leftarrow 0 \quad \forall (i, j) \in \text{RestoreMask}$$

### 3.3 High-Density Virtual Probe Sampling (`PositionElectrodeAndSample3D.m`)
For an electrode array with $K$ recording sites at 3D coordinates $\mathbf{E}_k = (X_k^E, Y_k^E, Z_k^E)$ and $N$ simulated neurons at somatic positions $\mathbf{x}_i = (X_i, Y_i, Z_i)$:
$$d_{ik} = \|\mathbf{x}_i - \mathbf{E}_k\|_2 = \sqrt{(X_i - X_k^E)^2 + (Y_i - Y_k^E)^2 + (Z_i - Z_k^E)^2}$$
A neuron $i$ is detected on channel $k$ if:
$$d_{ik} < r_{\text{detect}} \quad (r_{\text{detect}} = 50\ \mu\text{m}) \quad \text{and} \quad k = \arg\min_{m} d_{im}$$
The multi-unit instantaneous activity on channel $k$ is given by:
$$A_k(t) = \sum_{i \in \text{Channel } k} R_i(t)$$

### 3.4 Poisson Spike Generation & Rate Estimation (`ComputeSpikes.m`, `ComputeEstimatedRates.m`)
Normalized rate:
$$R_{\text{norm}, i}(t) = \frac{R_i(t) - \min(R_i)}{\max(R_i) - \min(R_i)}$$
Inhomogeneous Poisson spike draw:
$$S_i(t) \sim \text{Poisson}\left( \frac{R_{\text{norm}, i}(t)}{75} \right) > 0$$
Instantaneous rate estimation via Gaussian kernel convolution:
$$\hat{R}_i(t) = (S_i * g_\sigma)(t), \quad g_\sigma(t) = \frac{1}{\sqrt{2\pi}\sigma} \exp\left(-\frac{t^2}{2\sigma^2}\right), \quad \sigma = 50\text{ ms}$$

---

## 4. Invariant Parameters (Preserved Across Experiments)

All baseline physical and dynamical parameters from Figures 3–5 remain identical:
- **Geometry**: 11 spinal segments ($T_{13}$–$S_4$), $N = 5,229$ neurons ($D = 0.8$, seed 42).
- **Coordinate Calibration**: Mediolateral $X \in [-1750, 1750]\ \mu\text{m}$, Dorsoventral $Y \in [0, 1613]\ \mu\text{m}$, Rostrocaudal $Z \in [0, 11000]\ \mu\text{m}$.
- **Drive Current**: Baseline excitatory drive $I_e = 30.0\text{ pA}$.
- **Integration**: Forward Euler, $\Delta t = 1.0\text{ ms}$, duration $10,000\text{ ms}$ ($10\text{ s}$).
- **Membrane Time Constant**: $\tau_V = 50.0\text{ ms}$, Gaussian noise $\sigma_{\text{noise}} = 0.5\text{ pA}$.
- **Activation Function**: Compound $\tanh$ with cell-type thresholds $T_i$, gains $g_i$, and $f_{\max, i}$.

---

## 5. Panel-by-Panel Specifications for Figure 6

```mermaid
graph TD
    subgraph Figure 6 Architecture
        subgraph Lesion & Disruption
            P6A[Panel 6A: Anatomical Lesion & Broken Projectome]
            P6B[Panel 6B: Spatiotemporal Wave Arrest Post-Lesion]
        end

        subgraph Targeted Regrowth
            P6C[Panel 6C: Cell-Type Specific Axonal Regrowth Matrices]
            P6D[Panel 6D: Functional Recovery of Locomotor Waves & EMG]
        end

        subgraph Electrophysiology Validation
            P6E[Panel 6E: High-Density Silicon Probe 3D Insertion]
            P6F[Panel 6F: Channel-by-Channel Spiking Sequence & Phase Lags]
        end
    end

    P6A --> P6B
    P6B --> P6C
    P6C --> P6D
    P6D --> P6E
    P6E --> P6F
```

### 5.1 Panel 6A: Anatomical Lesion & Projectome Disruption
- **Scientific Target**: Illustrate the 3D transverse lesion plane at the $L_2/L_3$ boundary ($z_{\text{lesion}} = 4,000\ \mu\text{m}$) and show the pre- vs. post-lesion Mexican-hat projectome profile.
- **Visuals**:
  1. 3D spinal cord diagram with somatic positions and transverse lesion cut line.
  2. Ipsilateral projectome curve $\Delta z$ before vs. after lesion, showing truncation of long-range projection tails.
- **MATLAB Grounding**: `@Network/MakeLesion.m`, `02_HelperFunctions/GenerateSynapticDistrib.m`.
- **Python Target**: `src/figure6_analysis.py:plot_panel_6a_lesion_projectome()`.

### 5.2 Panel 6B: Spatiotemporal Locomotor Dynamics Post-Lesion
- **Scientific Target**: Demonstrate the breakdown of traveling wave propagation and motor output following complete transverse transection.
- **Visuals**:
  1. Spatiotemporal firing rate heatmaps sorted along the rostrocaudal axis ($T_{13} \to S_4$), showing active oscillations rostral to the lesion and arrest/quiescence caudal to the lesion.
  2. Multi-muscle synthetic EMG traces (Left/Right Tibialis Anterior and Gastrocnemius) comparing intact control vs. post-lesion.
- **MATLAB Grounding**: `@Network/Simulate.m`, `@Network/PlotNeurogram.m`, `@Network/PlotEMG.m`.
- **Python Target**: `src/figure6_analysis.py:plot_panel_6b_post_lesion_dynamics()`.

### 5.3 Panel 6C: Targeted Axonal Regrowth (Cell-Type Specific Comparison)
- **Scientific Target**: Compare the structural reinnervation capacity of different genetically defined candidate populations across the lesion site.
- **Tested Populations**:
  1. `V2a-2`: Long-range descending excitatory interneurons ($\mu = 7,000\ \mu\text{m}$).
  2. `V1`: Mid-range rostral inhibitory interneurons ($\mu = 2,000\ \mu\text{m}$).
  3. `V0v`: Contralateral commissural excitatory interneurons ($\mu = 3,400\ \mu\text{m}$).
  4. `V3`: Local/mid-range commissural excitatory interneurons ($\mu = 500\ \mu\text{m}$).
- **Visuals**: Synaptic connectivity matrices and projectome profiles comparing intact, lesioned, and population-specific regrowth.
- **MATLAB Grounding**: `@Network/RegrowPop.m`, `02_HelperFunctions/GenerateSynapticDistrib.m`.
- **Python Target**: `src/figure6_analysis.py:plot_panel_6c_regrowth_comparison()`.

### 5.4 Panel 6D: Recovery of Locomotor Dynamics & EMG Following Targeted Regrowth
- **Scientific Target**: Demonstrate that only V2a-2 long-range excitatory regrowth successfully rescues the rostrocaudal traveling wave and restores coordinated bilateral EMG bursting.
- **Visuals**:
  1. Post-regrowth spatiotemporal firing rate raster ($T_{13} \to S_4$) under V2a-2 regrowth vs. V1/V0v regrowth.
  2. Synthetic EMG traces showing restored flexor-extensor and left-right alternation.
  3. Quantitative recovery score: Root-mean-square amplitude and coordination phase metrics across regrowth conditions.
- **MATLAB Grounding**: `@Network/Simulate.m`, `@Network/PlotEMG.m`, `@Network/Network.m/ComputePhase`.
- **Python Target**: `src/figure6_analysis.py:plot_panel_6d_functional_recovery()`.

### 5.5 Panel 6E: High-Density Silicon Probe Electrophysiology Sampling
- **Scientific Target**: Model the physical insertion of a 32-channel linear silicon probe / Neuropixels array into the lumbar spinal cord and map detected units to recording channels.
- **Visuals**:
  1. 3D anatomical transverse cross-section showing probe shank insertion trajectory through Rexed laminae VII–IX.
  2. Spatial distribution of detected neurons color-coded by channel depth ($0\ \mu\text{m} \to 1,500\ \mu\text{m}$).
  3. Histogram of detected cell types per channel.
- **MATLAB Grounding**: `02_HelperFunctions/PositionElectrodeAndSample3D.m`, `04_Utilities/ChannelMaps/Linear32kilosortChanMap.mat`.
- **Python Target**: `src/figure6_analysis.py:plot_panel_6e_probe_insertion()`.

### 5.6 Panel 6F: Multi-Channel Spiking Sequence & Cross-Channel Phase Progression
- **Scientific Target**: Display the channel-by-channel synthetic spike rasters and estimated multi-unit firing rates ordered by depth, validating continuous phase lags along the probe.
- **Visuals**:
  1. Multi-channel spike raster plot showing sequential activation across channels during locomotor cycles.
  2. Gaussian-filtered multi-unit firing rate heatmap demonstrating continuous traveling wave phase shifts across probe depth.
  3. Polar phase plot of channel-to-channel phase lags relative to the cycle reference.
- **MATLAB Grounding**: `@Network/ComputeSpikes.m`, `@Network/ComputeEstimatedRates.m`, `@Network/PlotRaster.m`.
- **Python Target**: `src/figure6_analysis.py:plot_panel_6f_multichannel_spiking()`.

### 5.7 Composite Figure 6
- **Target File**: `plots/20_figure6_complete.png` (Publication-quality 6-panel composite).

---

## 6. Python Translation & Architecture Plan

```
reproduction/
├── src/
│   ├── network.py              # Intact 3D network construction (reused from Steps 1–6)
│   ├── dynamics.py             # Euler ODE rate solver (reused from Steps 1–6)
│   ├── locomotion.py           # Synthetic EMG generator (reused from Steps 1–6)
│   ├── gait_control.py         # Circular phase analysis (reused from Steps 1–6)
│   ├── perturbations.py        # [EXTEND] Add create_transverse_lesion & regrow_population_connections
│   ├── electrophysiology.py    # [NEW] VirtualProbe, PositionElectrodeAndSample3D, Poisson spike sampling
│   └── figure6_analysis.py     # [NEW] Master Figure 6 simulation and 6-panel visualization pipeline
├── tests/
│   └── test_figure6.py         # [NEW] Automated tests for lesion, regrowth, probe sampling, and recovery
├── plots/
│   ├── 20_fig6a_lesion_projectome.png
│   ├── 21_fig6b_post_lesion_dynamics.png
│   ├── 22_fig6c_regrowth_comparison.png
│   ├── 23_fig6d_functional_recovery.png
│   ├── 24_fig6e_probe_insertion.png
│   ├── 25_fig6f_multichannel_spiking.png
│   └── 26_figure6_complete.png
└── results/
    ├── figure6_summary.json
    └── figure6_simulation_results.npz
```

---

## 7. Direct Reproduction vs. Implementation Choices

| Component | Original MATLAB Implementation | Python Reproduction Implementation | Classification |
| :--- | :--- | :--- | :--- |
| **Lesion Cutting** | `@Network/MakeLesion.m` boolean plane mask | Vectorized NumPy boolean broadcasting across $Z$-coordinates | **Direct Reproduction** |
| **Axonal Regrowth** | `@Network/RegrowPop.m` weight mean assignment | Exact mean nonzero weight restoration formula | **Direct Reproduction** |
| **Probe Sampling** | `PositionElectrodeAndSample3D.m` Euclidean distance | Vectorized pairwise distance matrix calculation | **Direct Reproduction** |
| **Coordinate System** | Transverse $X, Y$, Longitudinal $Z$ ($0..11000\ \mu\text{m}$) | Consistent $(X, Y, Z)$ spatial coordinate system | **Direct Reproduction** |
| **Spike Conversion** | `poissrnd(RIsp / 75)` in MATLAB | `numpy.random.poisson(R_norm / 75.0)` | **Direct Reproduction** |
| **Rate Smoothing** | `GetGaussianFiring.m` ($w = 50\text{ ms}$, $f_s = 1000\text{ Hz}$) | `scipy.ndimage.gaussian_filter1d(..., sigma=50.0)` | **Python Implementation Choice** |
| **Channel Maps** | MATLAB `.mat` files in `ChannelMaps/` | NumPy structured array with 32 channels, $50\ \mu\text{m}$ pitch | **Python Implementation Choice** |

---

## 8. Uncertainties & Resolution Strategies

1. **Lesion Level Sensitivity**:
   - *Issue*: Lesion at $L_2/L_3$ ($z \approx 4,000\ \mu\text{m}$) vs. $T_{13}/L_1$ ($z \approx 2,000\ \mu\text{m}$).
   - *Resolution*: Parameterize $z_{\text{lesion}}$ in `create_transverse_lesion`. Default to $L_2/L_3$ boundary ($z = 4,000\ \mu\text{m}$) as standard since it bisects the lumbar enlargement between flexor (L1–L3) and extensor (L4–L6) pools.
2. **Post-Regrowth E/I Rebalancing**:
   - *Issue*: In `RegrowPop.m`, the balancing call `%obj.ConnMat = BalanceConnectivity(...)` was commented out in MATLAB.
   - *Resolution*: Provide `rebalance: bool = False` option. By default, follow the active MATLAB behavior (unbalanced raw mean weight injection), and include unit test comparison of both modes.
3. **Probe Insertion Site**:
   - *Issue*: Transverse insertion depth into intermediate vs. ventral horn.
   - *Resolution*: Place the virtual 32-channel linear probe with tip in the ventral horn ($Y \approx 400\ \mu\text{m}$, Lamina IX) passing through the intermediate zone (Lamina VII/VIII) at segment L2/L3 ($Z = 3,500\ \mu\text{m}$).

---

## 9. Validation & Acceptance Criteria

To declare Figure 6 successfully reproduced in subsequent steps:
1. **Lesion Validation**: Transverse lesion at $z = 4,000\ \mu\text{m}$ must sever $\ge 99\%$ of cross-boundary connections and abolish or decouple caudal motor oscillations.
2. **Regrowth Validation**:
   - V2a-2 regrowth must restore $> 80\%$ of baseline oscillation frequency and re-establish alternating EMG bursting.
   - V1 or non-projecting regrowth must fail to restore rhythmic propagation.
3. **Probe Validation**: Virtual 32-channel probe must detect $\ge 50$ distinct neurons across laminae and display clear depth-dependent phase delays along the shank during locomotion.
4. **Test Suite Integrity**: All prior 41/41 unit tests for Figures 3, 4, and 5 must remain 100% passing, with new Figure 6 tests bringing total passing tests to $\ge 46/46$.
5. **Publication Quality**: All 6 individual panels and the unified composite must be rendered in publication style.

---
*End of FIGURE6_PLAN.md. Awaiting user instruction before proceeding to implementation.*
