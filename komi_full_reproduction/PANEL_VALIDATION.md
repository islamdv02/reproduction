# Komi et al. (Nature Communications, 2026) Panel-by-Panel Reproduction Audit

**Total Panels Evaluated:** 36 across Figures 1–5  

## Summary by Canonical Status Category

| Status Category | Panel Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **MATCHED REPRODUCTION** | 16 | 44.4% | Correct author routine/exact equations used, visual and quantitative outcomes agree, no synthetic/proxy fabrications. |
| **METHODS-BASED RECONSTRUCTION** | 4 | 11.1% | Reconstructed methods-based panel assembly or parameters where author plotting routine was unreleased. |
| **METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT** | 8 | 22.2% | Simulation executed genuinely with author equations/parameters, but computational outcome differs from published figure. |
| **REFERENCE ONLY — EXTERNAL BIOLOGICAL DATA** | 3 | 8.3% | External empirical histology datasets preserved from publication; not computationally reproduced. |
| **REFERENCE ONLY — CONCEPTUAL** | 3 | 8.3% | Conceptual schematics and theoretical diagrams preserved from publication; not computationally simulated. |
| **UNAVAILABLE — AUTHOR MODEL DRIVER NOT RELEASED** | 2 | 5.6% | 1D toy simulation routines unreleased in upstream repository; blocked from computational reproduction. |

---

## Figure 1

### Panel 1A
- **Published Purpose:** Confocal fluorescence tracing of V2a interneuron axonal projections in the lumbar spinal cord
- **Source Routine:** `External histological imaging (Hayashi et al., 2018)`
- **Source Data:** `Confocal microscopy dataset (external biological data)`
- **Parameters:** Chx10-Cre; tdTomato mouse lumbar spinal cord sagittal tracing
- **Seed:** N/A (biological experiment)
- **Result File:** `figures/published_figures/published_figure1.jpeg`
- **Published Expectation:** Multi-segmental V2a axonal projection extending longitudinally
- **Reproduced Outcome:** External empirical reference preserved from publication
- **Status:** `REFERENCE ONLY — EXTERNAL BIOLOGICAL DATA`
- **Evidence & Discrepancy Analysis:** Published reference plate preserved

### Panel 1B
- **Published Purpose:** V2a somata distribution and ventral axonal projection bias in transverse spinal section
- **Source Routine:** `External histological imaging (Hayashi et al., 2018)`
- **Source Data:** `Transverse section confocal microscopy (external biological data)`
- **Parameters:** Lumbar spinal cord transverse section
- **Seed:** N/A (biological experiment)
- **Result File:** `figures/published_figures/published_figure1.jpeg`
- **Published Expectation:** Ventral quadrant somata localization and descending axonal routing
- **Reproduced Outcome:** External empirical reference preserved from publication
- **Status:** `REFERENCE ONLY — EXTERNAL BIOLOGICAL DATA`
- **Evidence & Discrepancy Analysis:** Published reference plate preserved

### Panel 1C
- **Published Purpose:** Ascending axons of lumbar V2a interneurons terminating in rostral thoracic/cervical cord
- **Source Routine:** `External histological imaging (Hayashi et al., 2018)`
- **Source Data:** `Ascending axonal tracing confocal imaging (external biological data)`
- **Parameters:** Rostral projection visualization
- **Seed:** N/A (biological experiment)
- **Result File:** `figures/published_figures/published_figure1.jpeg`
- **Published Expectation:** Ascending axonal collaterals terminating in rostral segments
- **Reproduced Outcome:** External empirical reference preserved from publication
- **Status:** `REFERENCE ONLY — EXTERNAL BIOLOGICAL DATA`
- **Evidence & Discrepancy Analysis:** Published reference plate preserved

### Panel 1D
- **Published Purpose:** 1D network schematic illustrating excitatory and inhibitory spatial projection curves from soma location S0
- **Source Routine:** `Conceptual diagram (Nature Comms editorial / Illustrator)`
- **Source Data:** `Conceptual theory architecture`
- **Parameters:** Soma position S0 with spatial displacement profiles
- **Seed:** N/A
- **Result File:** `figures/published_figures/published_figure1.jpeg`
- **Published Expectation:** Conceptual 1D spatial network schematic
- **Reproduced Outcome:** Preserved conceptual schematic
- **Status:** `REFERENCE ONLY — CONCEPTUAL`
- **Evidence & Discrepancy Analysis:** Published conceptual diagram preserved

### Panel 1E
- **Published Purpose:** Theoretical Mexican-hat connectivity curve and distance-dependent interaction matrix
- **Source Routine:** `Theoretical formulation w(x) = A_e*exp(-x^2/(2*s_e^2)) - A_i*exp(-x^2/(2*s_i^2))`
- **Source Data:** `Difference-of-Gaussians mathematical equation`
- **Parameters:** Local excitation, surround inhibition spatial parameters
- **Seed:** N/A
- **Result File:** `figures/published_figures/published_figure1.jpeg`
- **Published Expectation:** Mexican-hat spatial profile and distance matrix
- **Reproduced Outcome:** Preserved theoretical curve
- **Status:** `REFERENCE ONLY — CONCEPTUAL`
- **Evidence & Discrepancy Analysis:** Published conceptual diagram preserved

### Panel 1F
- **Published Purpose:** 5-lobe subpopulation spatial layout decomposition schematic
- **Source Routine:** `Conceptual diagram of subpopulation displacement kernels`
- **Source Data:** `5 cardinal subpopulation kernel definitions (sp1 to sp5)`
- **Parameters:** 5 subpopulation lobes
- **Seed:** N/A
- **Result File:** `figures/published_figures/published_figure1.jpeg`
- **Published Expectation:** Conceptual 5-lobe architecture diagram
- **Reproduced Outcome:** Preserved conceptual diagram
- **Status:** `REFERENCE ONLY — CONCEPTUAL`
- **Evidence & Discrepancy Analysis:** Published conceptual diagram preserved

### Panel 1G
- **Published Purpose:** 1D rate model: amplitude control via sp3 subpopulation gain modulation
- **Source Routine:** `1D continuous rate equation simulation (unreleased in BergLab/SpinalProjectome)`
- **Source Data:** `Unreleased 1D toy simulation routines`
- **Parameters:** sp3 subpopulation gain sweep in 1D rate continuum
- **Seed:** Unavailable in author repository
- **Result File:** `None (unreleased in BergLab/SpinalProjectome)`
- **Published Expectation:** Monotonic amplitude growth with minimal frequency modulation
- **Reproduced Outcome:** not measured
- **Status:** `UNAVAILABLE — AUTHOR MODEL DRIVER NOT RELEASED`
- **Evidence & Discrepancy Analysis:** Routine absent from upstream release; no proxy fabricated

### Panel 1H
- **Published Purpose:** 1D rate model: frequency control via sp2 subpopulation gain modulation
- **Source Routine:** `1D continuous rate equation simulation (unreleased in BergLab/SpinalProjectome)`
- **Source Data:** `Unreleased 1D toy simulation routines`
- **Parameters:** sp2 subpopulation gain sweep in 1D rate continuum
- **Seed:** Unavailable in author repository
- **Result File:** `None (unreleased in BergLab/SpinalProjectome)`
- **Published Expectation:** Monotonic frequency modulation with stable amplitude
- **Reproduced Outcome:** not measured
- **Status:** `UNAVAILABLE — AUTHOR MODEL DRIVER NOT RELEASED`
- **Evidence & Discrepancy Analysis:** Routine absent from upstream release; no proxy fabricated

---

## Figure 2

### Panel 2A
- **Published Purpose:** Spatial transcriptomics transverse section spot identification and 2D probability distributions (Rora, V2a, V1, Mn)
- **Source Routine:** `scripts/run_figure2_reproduction.m (using matGeometry.mat)`
- **Source Data:** `source/01_SpinalGeometryFiles/matGeometry.mat (RCTDCoord, weights, matLayers)`
- **Parameters:** Reconstructed thresholds: w_rora > 0.08, w_v1 > 0.08, w_mn > 0.04, w_v2a > 0.06; 2D Gaussian KDE
- **Seed:** N/A (deterministic dataset)
- **Result File:** `figures/main_figures/Figure2.png`
- **Published Expectation:** Laminar domains: Rora (dorsal), V1 (intermediate), Mn (ventral horn)
- **Reproduced Outcome:** Spot coordinates and 2D KDE probability contours inside transverse spinal outline
- **Status:** `METHODS-BASED RECONSTRUCTION`
- **Evidence & Discrepancy Analysis:** Transverse spinal outline and laminar domains conform to published layout

### Panel 2B
- **Published Purpose:** Model sampled motoneurons (ChAT+) and V2a (Vsx2+) compared to empirical reference markers
- **Source Routine:** `scripts/run_figure2_reproduction.m: modeled half from N.Position; reference half from published histology plate`
- **Source Data:** `results/baseline_network.mat and published histology reference plate`
- **Parameters:** Modeled Mn (ChAT+) and V2a (Vsx2+) plotted from network coordinates; empirical reference preserved
- **Seed:** N/A (deterministic coordinates; fabricated random points eliminated)
- **Result File:** `figures/main_figures/Figure2.png`
- **Published Expectation:** Ventral horn cluster for Mn (ChAT+); ventromedial column for V2a (Vsx2+)
- **Reproduced Outcome:** Modeled half derives from network coordinates; empirical reference preserved from publication
- **Status:** `METHODS-BASED RECONSTRUCTION`
- **Evidence & Discrepancy Analysis:** Split presentation with labeled provenance (modeled network vs empirical histology)

### Panel 2C
- **Published Purpose:** 3D directional projection kernels for 9 cardinal ventral classes along RC, ML, DV axes
- **Source Routine:** `scripts/run_figure2_reproduction.m (using N.Parameters and @Network/InstantiateNetwork.m formulas)`
- **Source Data:** `N.Parameters from baseline_network.mat`
- **Parameters:** projwidth = 500 um; exact author RC probability formulas exp(-0.5*((d-L)/projwidth)^2); ML/DV vectors
- **Seed:** N/A
- **Result File:** `figures/main_figures/Figure2.png`
- **Published Expectation:** Directional asymmetric projection curves along RC, ML, DV axes
- **Reproduced Outcome:** Directional kernels computed from exact author formulas; manual positions eliminated
- **Status:** `METHODS-BASED RECONSTRUCTION`
- **Evidence & Discrepancy Analysis:** Transverse projection vectors, dorsoventral ribbons, and RC profiles conform to published panel

### Panel 2D
- **Published Purpose:** Segmental topography of 13 published hindlimb motoneuron pools along rostrocaudal axis (T13 to S4)
- **Source Routine:** `scripts/run_figure2_reproduction.m and scripts/export_motoneuron_pools.m`
- **Source Data:** `results/baseline_network.mat (N.Position, N.MnID, N.Segment)`
- **Parameters:** 13 displayed pools: VLat, VMed, Ilio, RF, TA, GM, Glut, BF, ST, Sol, PF, EDL, Tail (18 total pools in model)
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure2.png, results/motoneuron_pools.json`
- **Published Expectation:** 13 published hindlimb pools spanning T13-S4 with stereotypic rostrocaudal distributions
- **Reproduced Outcome:** 13 displayed pools from actual network coordinates; 18 total model pools separately recorded
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Vertical pool strips, leader lines, and segment boundaries match publication

### Panel 2E
- **Published Purpose:** Pairwise connectivity matrix W decomposed into ipsilateral and contralateral components
- **Source Routine:** `scripts/run_figure2_reproduction.m (using N.ConnMat and N.Latera)`
- **Source Data:** `results/baseline_network.mat`
- **Parameters:** Fine sparse scatter rendering (N = 4,934 neurons; 589,368 non-zero synapses; ipsilateral & contralateral blocks)
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure2.png`
- **Published Expectation:** N = 4,934; ~5.9x10^5 synapses; Sparsity = 97.58%
- **Reproduced Outcome:** N = 4934; 589368 synapses (527286 ipsi, 62082 contra); Sparsity = 97.58%
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Fine sparse dot rendering resolves individual connections without saturated blocks

### Panel 2F
- **Published Purpose:** Cell type-to-cell type interaction matrix (9x9 normalized transmission weights)
- **Source Routine:** `scripts/run_figure2_reproduction.m (using N.ConnMat and N.Types)`
- **Source Data:** `results/baseline_network.mat`
- **Parameters:** 9x9 interaction matrix normalized by total postsynaptic input
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure2.png`
- **Published Expectation:** Normalized 9x9 interaction matrix heatmap
- **Reproduced Outcome:** Postsynaptic input-normalized interaction matrix C_norm matching published cell class couplings
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Heatmap pattern matches published interaction topology

### Panel 2G
- **Published Purpose:** Net lumbar spinal projectome decomposed into ipsilateral and contralateral components
- **Source Routine:** `Author GeneratePlot routine from PlotAnimatedNetworkEmgandPC.m (edges = -L:250:L um, no smoothing)`
- **Source Data:** `results/baseline_network.mat (N.ConnMat, N.Position, N.Transmit)`
- **Parameters:** edges = -L:250:L um; difference = abs(MEx.*CEx) - abs(MIn.*CIn); no Gaussian smoothing
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure2.png`
- **Published Expectation:** Ipsilateral asymmetric Mexican-hat with rostral inhibitory bias; contralateral commissural kernel
- **Reproduced Outcome:** Ipsilateral: excitation peak (+500 um), rostral inhibition dip (-1500 um); Contralateral: symmetric peak at 0 um
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Lobe sequence, zero-crossings, and rostral bias emerge from author routine

---

## Figure 3

> **Note on Published Panel Inventory:** Panels 3A (connectivity matrix W), 3C (global-input schematic), and 3D (activation function) were custom diagnostic additions in earlier composite drafts and are not part of the published Figure 3 panel layout. Per the published figure inventory, they have been removed from the main reproduction composite (`Figure3.png`). Retained panels preserve their published letters (**B**, **E**, **F**, **G**, **H**) without re-lettering.

### Panel 3B
- **Published Purpose:** Eigenspectrum in complex plane with Re(lambda)=1 boundary and dominant spatial eigenmodes
- **Source Routine:** `scripts/run_figure3_reproduction.m (using eig and ComputeEigenModesandNullSpace.m)`
- **Source Data:** `results/baseline_network.mat (N.ConnMat)`
- **Parameters:** W_full, conjugate eigenpairs sorted by Re(lambda), stability boundary Re(lambda) = 1.0
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure3.png`
- **Published Expectation:** Dominant eigenvalue lambda_1 = 2.02 +/- 0.76i (4 modes Re > 1.0); Mode 1 alternating, Mode 2 synchronous
- **Reproduced Outcome:** Dominant eigenvalue lambda_1 = 2.019 +/- 0.762i; Mode 1 alternating, Mode 2 synchronous
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Eigenspectrum scatter and longitudinal mode distributions match publication


### Panel 3E
- **Published Purpose:** Spatiotemporal dynamics: spatial representation of firing rates across segments, antagonistic muscle EMGs, and motor nerve outputs
- **Source Routine:** `scripts/run_figure3_reproduction.m` using author `PlotEMG.m` and `PlotNeurogram.m` algorithms; top spatial panel reconstructed from RC-binned right hemicord activity (`Position(:, 2)`)
- **Source Data:** `results/simulated_network.mat` (`N.Rates`, `N.MnID`, `N.Segment`, `N.Position`, `N.Latera`)
- **Parameters:** Author binomial spike-rate model; muscle order: VM, BF, TA, Sol; R L2, R L5, L L2 neurograms; 80 spatial bins along RC axis ($0\text{–}14,000\,\mu\text{m}$)
- **Seed:** 5
- **Result File:** `figures/main_figures/Figure3.png`
- **Published Expectation:** Traveling bumps of activity across segments in caudal direction (Right hemicord), reciprocal muscle bursting (VM, BF, TA, Sol), alternating motor nerve bursts
- **Reproduced Outcome:** Traveling segmental rate bumps along RC axis, reciprocal EMGs in author order, and segmental neurograms
- **Status:** `METHODS-BASED RECONSTRUCTION — EXACT PUBLISHED ORDERING UNAVAILABLE`
- **Evidence & Discrepancy Analysis:** The assembly script for published Figure 3E is unreleased (`MakeSummaryFigure.m` is an empty 6-line stub). While `PlotRaster.m` contains `ComputeFiringPhaseSorting`, that routine produces synthetic Poisson spike rasters (point scatter), not a continuous 2D spatial rate heatmap, and has no segmental Y-axis. The published panel is labeled "Segments" (T13–S4). Code tracing classifies the published spatial panel as **`unresolved because the assembly code is unavailable`** (with behavior matching anatomical spatial bins or segment-averaged population activity). Per scientific audit guidelines, phase sorting is not used in primary anatomical wave analysis (`Position(:, 2)` is preserved), and a smooth phase-sorted diagonal is never described as proof of continuous physical propagation.

### Panel 3F
- **Published Purpose:** Polar phase relationships between segmental outputs across steady-state locomotor cycles
- **Source Routine:** `scripts/run_figure3_reproduction.m circular phase analysis with explicit cycle boundaries`
- **Source Data:** `results/simulated_network.mat`
- **Parameters:** Peak matching restricted to corresponding cycle intervals; circular mean vector
- **Seed:** 5
- **Result File:** `figures/main_figures/Figure3.png`
- **Published Expectation:** Alternating bilateral phase (~180°) and flexor-extensor phase (~190°)
- **Reproduced Outcome:** Bilateral phase: 155.9°; Flexor-extensor phase: 196.0°
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Polar scatter and circular mean vectors match publication

### Panel 3G
- **Published Purpose:** Distribution of single-neuron preferred firing phases across the locomotor cycle
- **Source Routine:** `00_SpinalNetworkModel/@Network/Network.m:ComputePhase against PC1 collective rhythm`
- **Source Data:** `results/simulated_network.mat (N.Rates)`
- **Parameters:** Cross-correlation lag relative to PC1 collective rhythm modulo cycle period, wrapped to [0, 2pi); 20 bins; R = 400 radial ring
- **Seed:** 5
- **Result File:** `figures/main_figures/Figure3.png`
- **Published Expectation:** 20-wedge polar histogram with R = 400 neurons radial ring and dominant phase regions
- **Reproduced Outcome:** 20-wedge polar histogram across all N = 4,934 neurons with bin counts 187-332, peak at 30-60 deg and secondary peak at 150-180 deg bounded in R = 400 ring
- **Status:** `METHODS-BASED RECONSTRUCTION — EXACT PHASE SUBSET UNAVAILABLE`
- **Evidence & Discrepancy Analysis:** The authors provided `ComputeFiringPhaseSorting.m` and `ComputePhase`, but no dedicated `Fig3g.m`. Computing phases against PC1 collective rhythm populates the 20 wedges matching published shape within R = 400. Fully documented in `results/figure3_phase_distribution_validation.json`.


### Panel 3H
- **Published Purpose:** Low-dimensional rotational limit cycle trajectory in PC space
- **Source Routine:** `Author ComputeSpikes -> ComputeEstimatedRates -> ComputePC pipeline`
- **Source Data:** `results/simulated_network.mat (N.PC, N.Explained)`
- **Parameters:** PC1 vs PC3 projection (repaired axis matching published labels); explained variance from PCA object
- **Seed:** 100
- **Result File:** `figures/main_figures/Figure3.png`
- **Published Expectation:** Rotational limit cycle in PC1-PC3 space with outward transient spiral into single loop
- **Reproduced Outcome:** PC1 vs PC3 trajectory naturally forming transient spiral into single loop (PC1: 20.4% var)
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Limit cycle trajectory, directional Time arrow, and PC1/PC3 labels match publication

---

## Figure 4

### Panel 4A
- **Published Purpose:** Neuromodulatory gain modulation of the neuronal activation function
- **Source Routine:** `@Network/Simulate.m lines 77-84`
- **Source Data:** `Mathematical formulation from Simulate.m`
- **Parameters:** Gains g = [0.5, 1.0, 2.0], threshold = 5 pA, Fmax = 50 Hz
- **Seed:** N/A
- **Result File:** `figures/main_figures/Figure4.png`
- **Published Expectation:** Three sigmoidal/tanh activation curves showing steepened gain
- **Reproduced Outcome:** Three compound tanh activation curves with gain scaling
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Curves, colors, and gain annotations match publication

### Panel 4B
- **Published Purpose:** Descending terminal densities (LPGi and Raphe) and receptor expression across cell types
- **Source Routine:** `scripts/run_figure4_reproduction.m with inROI and matDescending.mat; case-insensitive DI6 fix`
- **Source Data:** `source/01_SpinalGeometryFiles/matDescending.mat and source/03_SpinalCordGeneticsFiles/matCountSingleCell.mat`
- **Parameters:** Transverse ROIs for LPGi-Vglut2 and Raphe-5HT terminals; Htr7 log2FC; case-insensitive DI6 matching
- **Seed:** N/A
- **Result File:** `figures/main_figures/Figure4.png`
- **Published Expectation:** Differential descending targeting across 9 cell classes and Htr7 enrichment
- **Reproduced Outcome:** Targeting percentages across all 9 classes (including DI6) and Htr7 log2FC
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Four-quadrant layout, terminal contours, and polar radar targets match publication

### Panel 4C
- **Published Purpose:** Continuous descending drive and gain schedule with effective projectome modulation across gaits
- **Source Routine:** `scripts/run_figure4_reproduction.m: reconstructed schedule & author GeneratePlot`
- **Source Data:** `Reconstructed schedule: LPGi drive (15 -> 22 -> 30 pA), Raphe gain (0.7 -> 1.0 -> 1.8)`
- **Parameters:** W_eff = W * diag(R_bar); sliding mean rates across gait epochs
- **Seed:** N/A
- **Result File:** `figures/main_figures/Figure4.png`
- **Published Expectation:** Descending drive and gain profiles driving gait transitions; modulated effective projectomes
- **Reproduced Outcome:** Drive and gain profiles with effective projectomes across simulated gaits
- **Status:** `METHODS-BASED RECONSTRUCTION`
- **Evidence & Discrepancy Analysis:** Input ramps and effective projectomes display modulated lobes

### Panel 4D
- **Published Purpose:** Continuous multi-gait simulation traces across Walking, Trotting, and Bounding
- **Source Routine:** `@Network/Simulate.m continuous 12,000 ms simulation with author PlotEMG/PlotNeurogram algorithms`
- **Source Data:** `results/figure4_simulation.mat`
- **Parameters:** Continuous 12 s simulation; arbitrary multipliers and synthetic noise removed; genuine author signals
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure4.png`
- **Published Expectation:** Walking (alternation) -> Trotting (faster alternation) -> Bounding (bilateral synchrony)
- **Reproduced Outcome:** Continuous simulation executes genuinely; Walk (1.29 Hz) and Trot (1.36 Hz) alternate; Bound (1.40 Hz) maintains reciprocal alternation (~163°)
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Continuous multi-panel traces formatted to publication; bounding dynamics remain alternating

### Panel 4E
- **Published Purpose:** Bilateral and flexor-extensor polar phase relationships across gaits
- **Source Routine:** `scripts/run_figure4_reproduction.m circular phase analysis across steady-state gait windows`
- **Source Data:** `results/figure4_simulation.mat`
- **Parameters:** iL2-cL2 and iL2-iL5 phase differences during Walk, Trot, Bound
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure4.png`
- **Published Expectation:** Walk and Trot alternate (~180°); Bounding switches to in-phase synchrony (~0°)
- **Reproduced Outcome:** Walk (160.0°), Trot (162.3°), Bound (163.3°)
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Polar plots formatted to publication; bounding vector points to alternation

### Panel 4F
- **Published Purpose:** Locomotor cycle frequency progression across gaits
- **Source Routine:** `scripts/run_figure4_reproduction.m cycle frequency measurement`
- **Source Data:** `results/figure4_simulation.mat`
- **Parameters:** Steady-state cycle frequency across Walk, Trot, Bound
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure4.png`
- **Published Expectation:** Substantial frequency acceleration from Walk (~2.5 Hz) to Bound (~5.2 Hz)
- **Reproduced Outcome:** Walk (1.29 Hz) -> Trot (1.36 Hz) -> Bound (1.40 Hz)
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Bar plot formatted to publication; underlying values reflect genuine simulation

### Panel 4G
- **Published Purpose:** Motor nerve and muscle burst amplitude scaling across gaits
- **Source Routine:** `scripts/run_figure4_reproduction.m burst amplitude calculation from raw signals`
- **Source Data:** `results/figure4_simulation.mat`
- **Parameters:** Peak-to-trough burst envelope amplitude; arbitrary multipliers (TA*3.5, Sol*5.5) removed
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure4.png`
- **Published Expectation:** Monotonic amplitude growth across gaits with bounding transition
- **Reproduced Outcome:** Nerve and muscle burst amplitudes increase with drive, but bound remains alternating
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Bar chart formatted to publication; computed from unmanipulated raw signals

---

## Figure 5

### Panel 5A
- **Published Purpose:** V1 interneuron spatial distribution and projectome alteration upon V1 ablation
- **Source Routine:** `Author GeneratePlot & 3D coordinates from baseline_network.mat`
- **Source Data:** `results/baseline_network.mat`
- **Parameters:** V1 somata in transverse cord; net ipsilateral projectome with and without V1
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure5.png`
- **Published Expectation:** Loss of rostral inhibitory lobe upon V1 removal
- **Reproduced Outcome:** Ipsilateral projectome alteration showing selective abolition of rostral inhibition
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Transverse cord with V1 somata and projectome difference curves match publication

### Panel 5B
- **Published Purpose:** Motor nerve output dynamics under ongoing V1 silencing (control -> silencing -> recovery) and permanent V1 ablation
- **Source Routine:** `@Network/Simulate.m ongoing simulation (8,000 ms, paired seeds) with author PlotNeurogram`
- **Source Data:** `results/figure5_simulations.mat`
- **Parameters:** Paired seed 42 across all conditions; silencing (-10 pA over 2.5-5.5 s); ablation (outgoing synapses zeroed)
- **Seed:** 42 (paired across Control, Silencing, Ablation)
- **Result File:** `figures/main_figures/Figure5.png`
- **Published Expectation:** Silencing: deceleration and burst prolongation with recovery; Ablation: continuous slow rhythm (~0.46 Hz, ~22 a.u.)
- **Reproduced Outcome:** Silencing: rate deceleration (1.31 -> 1.05 Hz) and recovery; Ablation: amplitude drops to quiescent state (1.93 a.u.)
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Silencing trace matches with deceleration and recovery; ablation trace shows quiescent signal rather than robust bursting

### Panel 5C
- **Published Purpose:** Quantification of frequency, amplitude, and phase relationships under V1 manipulation
- **Source Routine:** `scripts/run_figure5_reproduction.m (restricted cycle intervals, corrected polar layout)`
- **Source Data:** `results/figure5_simulations.mat`
- **Parameters:** Left polar: iL2-cL2; Right polar: iL2-iL5; dynamic y-limits on amplitude bars to prevent clipping
- **Seed:** 42 (paired)
- **Result File:** `figures/main_figures/Figure5.png`
- **Published Expectation:** Frequency slowing (Ctrl -> Sil -> Abl); Amplitude maintenance in ablation (~22 a.u.); Phase alternation preserved
- **Reproduced Outcome:** Frequency slows (1.31 -> 1.05 -> 0.46 Hz); Amplitude falls (35.1 -> 15.4 -> 1.9)
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Bar charts and polar plots formatted to publication; amplitude bars unclipped; reflects genuine simulation

### Panel 5D
- **Published Purpose:** V0 interneuron spatial distribution and projectome alteration upon V0 ablation
- **Source Routine:** `Author GeneratePlot & 3D coordinates from baseline_network.mat`
- **Source Data:** `results/baseline_network.mat`
- **Parameters:** V0d and V0v somata in transverse cord; net contralateral projectome with and without V0
- **Seed:** 42
- **Result File:** `figures/main_figures/Figure5.png`
- **Published Expectation:** Loss of commissural inhibition upon V0 removal
- **Reproduced Outcome:** Contralateral projectome alteration showing selective loss of cross-inhibition
- **Status:** `MATCHED REPRODUCTION`
- **Evidence & Discrepancy Analysis:** Transverse cord with V0 somata and projectome difference curves match publication

### Panel 5E
- **Published Purpose:** Motor nerve output dynamics under ongoing V0 silencing (speedup and bilateral synchrony switch) and permanent V0 ablation
- **Source Routine:** `@Network/Simulate.m ongoing simulation (8,000 ms, paired seeds) with author PlotNeurogram`
- **Source Data:** `results/figure5_simulations.mat`
- **Parameters:** Paired seed 42 across all conditions; silencing (-10 pA over 2.5-5.5 s); ablation (outgoing synapses zeroed)
- **Seed:** 42 (paired across Control, Silencing, Ablation)
- **Result File:** `figures/main_figures/Figure5.png`
- **Published Expectation:** Silencing: switch from alternating walking to synchronous hopping during window, recovery after; Ablation: continuous hopping
- **Reproduced Outcome:** Silencing: frequency accelerates during window (1.31 -> 1.56 Hz); Ablation: fast bursting (1.87 Hz), bilateral synchrony incomplete
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Traces formatted to publication; reflects genuine computational simulation without artificial synchronization

### Panel 5F
- **Published Purpose:** Quantification of frequency, amplitude, and phase switch (alternation to synchrony) under V0 manipulation
- **Source Routine:** `scripts/run_figure5_reproduction.m (restricted cycle intervals, corrected polar layout)`
- **Source Data:** `results/figure5_simulations.mat`
- **Parameters:** Left polar: iL2-iL5; Right polar: iL2-cL2; dynamic y-limits on amplitude bars to prevent clipping
- **Seed:** 42 (paired)
- **Result File:** `figures/main_figures/Figure5.png`
- **Published Expectation:** Frequency acceleration (+43%); amplitude increase; bilateral phase switch from alternation (~180°) to synchrony (~0°)
- **Reproduced Outcome:** Frequency accelerates (1.31 -> 1.56 -> 1.87 Hz); iL2-cL2 phase (162.7° -> 74.1° -> 359.4°)
- **Status:** `METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT`
- **Evidence & Discrepancy Analysis:** Bar charts and polar plots formatted to publication; amplitude bars unclipped; reflects genuine simulation

---
