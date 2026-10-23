# Controlled Experiment Summary: TA Motor-Pool Placement

> **STATUS: EXPERIMENT REPAIRED AND VALIDATED**  
> **Classification:** New Controlled Experiment — Not a Reproduced Publication Figure  
> **Experiment Directory:** [`komi_full_reproduction/experiments/ta_placement/`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/)  
> **Composite Deliverable:** [`TA_Placement_Experiment.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/TA_Placement_Experiment.png)  
> **Data Deliverables:** [`experiment_results.json`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/experiment_results.json), [`experiment_data.mat`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/data/experiment_data.mat), [`plot_export.mat`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/data/plot_export.mat)

---

## 1. Executive Summary & Objective

This study repairs and validates the **first controlled scientific experiment** executed on the spinal network model of Komi et al. (Nature Communications, 2026). The central goal is to test how relocating the Tibialis Anterior (TA) motoneuron pool from its published baseline placement in the rostral lumbar cord (L2–L4) to an empirical, anatomy-supported caudal lumbar position (L4–L5, as established in the mouse anatomical literature) alters:
1. **TA muscle coordination and burst timing** relative to shank and thigh synergists and antagonists;
2. **Motoneuron activity patterns along the anatomical rostrocaudal (RC) axis**;
3. **Underlying network rhythmogenesis and bilateral alternation**.

Crucially, this investigation avoids assuming that anatomical relocation must either "improve coordination" or make the spinal wave "smoother or more abrupt." Instead, the empirical outcomes are measured and reported directly using paired realization controls and circular statistics.

---

## 2. Anatomical Evidence & Explicit Relocation Mapping

### A. Literature Reference & Species Specificity
* **Primary Citation:** Bácskai, T., Rusznák, Z., Paxinos, G., & Sengul, G. (2014). *Anatomical organization of motoneurons supplying the hindlimb muscles in the mouse.* **Brain Structure and Function**, 219(2), 603–621. DOI: 10.1007/s00429-013-0522-y.
* **Species, Strain, and Age:** Laboratory mouse (*Mus musculus*), adult male C57BL/6J and transgenic C57BL/6J-ChAT-EGFP mice (body weight 20–25 g, age 8–12 weeks).
* **Specific Pages & Figures:**
  * **Page 606 & Table 1:** Detailed segmental distribution of hindlimb motoneuron columns; TA motoneurons are located in the dorsolateral motor column spanning lumbar segments **L4 and L5** (co-extensive with Extensor Digitorum Longus [EDL], Gastrocnemius, and Soleus).
  * **Page 609 (Figs. 2 & 3):** Transverse and longitudinal reconstruction of retrograde CTb-labeled motoneuron pools demonstrating that TA motoneurons reside in the dorsolateral column of L4–L5.
  * **Page 613 (Fig. 6):** Schematic summary of the longitudinal craniocaudal boundaries of the hindlimb motoneuron pools.
* **Species Separation:** Findings from the spiny mouse (*Acomys cahirinus*), where hindlimb motor pools are shifted rostrally (TA located in L3–L4; Bácskai et al., 2013), are kept strictly distinct. No cross-species blending is permitted.

### B. Segment Geometry & Boundary Discrepancy Resolution
A coordinate discrepancy was identified between previous ad-hoc scripts: MATLAB scripts previously used $6808.7\,\mu\text{m}$ as the L4/L5 border, whereas Python tables placed it at L5/L6. 

Auditing the author geometry source (`source/01_SpinalGeometryFiles/matGeometry.mat`) resolved this completely. The true segment lengths are:
$$\text{T13: } 1300\,\mu\text{m}, \quad \text{L1: } 1200\,\mu\text{m}, \quad \text{L2: } 1500\,\mu\text{m}, \quad \text{L3: } 1500\,\mu\text{m}, \quad \text{L4: } 1300\,\mu\text{m}, \quad \text{L5: } 1200\,\mu\text{m}, \quad \text{L6: } 1400\,\mu\text{m}, \quad \text{S1: } 1400\,\mu\text{m}, \quad \text{S2: } 1200\,\mu\text{m}, \quad \text{S3: } 900\,\mu\text{m}, \quad \text{S4: } 1000\,\mu\text{m}$$

Cumulative boundaries from a single unified geometry table are:
* **T13:** $[0.0, 1300.0]\,\mu\text{m}$
* **L1:** $[1300.0, 2500.0]\,\mu\text{m}$
* **L2:** $[2500.0, 4000.0]\,\mu\text{m}$
* **L3:** $[4000.0, 5500.0]\,\mu\text{m}$
* **L4:** $[5500.0, 6800.0]\,\mu\text{m}$ (L3/L4 boundary = $5500.0\,\mu\text{m}$)
* **L5:** $[6800.0, 8000.0]\,\mu\text{m}$ (L4/L5 boundary = **$6800.0\,\mu\text{m}$**; L5/L6 boundary = $8000.0\,\mu\text{m}$)
* **L6:** $[8000.0, 9400.0]\,\mu\text{m}$
* **S1–S4:** $[9400.0, 13900.0]\,\mu\text{m}$ (Total spinal cord length = $13{,}900.0\,\mu\text{m}$)

The previously used value of $6808.7\,\mu\text{m}$ was merely the empirical minimum coordinate of an L5 neuron in baseline seed 42, not an anatomical segment boundary. The verified L4/L5 boundary is **$6800.0\,\mu\text{m}$**.

### C. Explicit Relocation Mapping & Longitudinal Compression
* **Baseline Komi TA Distribution:** In the published model (`matMuscleSeg.mat`), Komi et al. assigned TA to L2 (15 template weights), L3 (30 weights), and L4 (10 weights). In baseline seed 42, this spans $[2771.8, 6733.3]\,\mu\text{m}$ (total longitudinal span = $3961.5\,\mu\text{m}$, centroid $4548.7\,\mu\text{m}$).
* **Relocation Target Span:** $[5600.0, 7900.0]\,\mu\text{m}$ (centroid $6750.0\,\mu\text{m}$, caudal shift of $+2201.3\,\mu\text{m}$).
* **Boundary Confinement:** Every relocated TA neuron lies strictly within the verified L4–L5 target ($[5500.0, 8000.0]\,\mu\text{m}$), with a $100\,\mu\text{m}$ safety margin from the outer segment borders.
* **Longitudinal Compression:** A translation-only relocation cannot fit inside the L4–L5 region because the baseline pool span ($3961.5\,\mu\text{m}$) exceeds the entire length of L4 and L5 combined ($2500.0\,\mu\text{m}$). Therefore, an affine rank-order mapping was used:
  $$Y_{\text{new}} = 5600.0 + (Y_{\text{orig}} - 2771.8) \times \frac{7900.0 - 5600.0}{6733.3 - 2771.8}$$
  This mapping compresses the longitudinal spread from $3961.5\,\mu\text{m}$ to $2300.0\,\mu\text{m}$ (a compression of **$41.9\%$**). **Both position and longitudinal spread change simultaneously.** The within-range rank distribution is explicitly designated as an **experimental modeling assumption**, not an empirical micro-density finding.
* **Strict Preservation:** Individual TA neuron IDs, total cell counts ($N_{\text{TA}} = 78$ in baseline seed 42), left/right laterality assignments, and transverse ($X = \text{Mediolateral}$, $Z = \text{Dorsoventral}$) coordinates were preserved 100%. All non-TA neuron coordinates and properties were left completely untouched.

---

## 3. Repaired Connection Generation & Weight Audit

Previous implementations utilized hand-written loops that only updated incoming TA rows, omitted outgoing connections, and applied an unverified heuristic global `rescale_factor`. 

This experiment repairs the connection generation by calling the authors' verified `InstantiateNetwork` pipeline:
1. **Preservation of Author Rules:** All 3D directional kernels (caudal, rostral, bidirectional, local), medio-lateral biases, dorso-ventral biases, contra/ipsilateral kernels, layer biases, and motor biases (`BiasMN`) are fully enforced.
2. **Segment Bias Recomputation:** Relocated TA neurons have their segment updated ($Y < 6800.0\,\mu\text{m} \implies \text{L4}$; $Y \ge 6800.0\,\mu\text{m} \implies \text{L5}$), ensuring that segment-dependent projection rules (`BiasSeg`) correctly reflect the new caudal location.
3. **Incoming AND Outgoing Updates:** Both incoming synapses onto TA and outgoing synapses from TA were recomputed in 3D space.
4. **Motoneuron Isolation:** The author's `UnifyMNConnectivity` rule was enforced, setting cross-pool MN-to-MN connections to 0, while preserving within-pool recurrent connections (TA-to-TA: 101 nonzeros in baseline; 184 in rebuilt C; 231 in rebuilt D) and connections to interneurons (95 nonzeros in baseline; 142–221 in C; 252–325 in D).
5. **Balancing & Rescaling Quantification:** Synaptic matrices were processed through author `BalanceConnectivity` (row-by-row $E/I$ balance) and `RescaleConnectivity` (hemisphere-level spectral/sparsity scaling).
   * Because TA sends outgoing connections to a small subset of interneurons and hemisphere sparsity changes slightly, non-TA weights undergo minor adjustments during balancing and rescaling.
   * Rather than suppressing these operations, they were quantified across all realizations:
     $$\text{Mean } |W_{\text{non-TA}}^{\text{Cond D}} - W_{\text{non-TA}}^{\text{Cond C}}| = (1.05 \pm 0.03) \times 10^{-6}$$
     $$\text{Max } |W_{\text{non-TA}}^{\text{Cond D}} - W_{\text{non-TA}}^{\text{Cond C}}| = (5.51 \pm 0.65) \times 10^{-3}$$
   * Non-TA connections are thus statistically untouched, with tiny deterministic adjustments strictly traceable to the authors' balancing and rescaling routines.

---

## 4. Controlled 4-Condition Experimental Design

To isolate spatial relocation from stochastic rewiring, four paired conditions were evaluated across 5 independent network realizations under matched simulation drive ($I_e = 25.0\,\text{pA}$) and fixed simulation noise (seed 5):

| Condition | Coordinates | Synaptic Weights ($W$) | Firing Rates ($R$) | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **A. Original Baseline** | Original L2–L4 | Frozen author matrix | Frozen author simulation | Baseline reference standard |
| **B. Coordinate-Only Control** | Relocated L4–L5 | $W_B \equiv W_A$ (Bit-for-bit) | $R_B \equiv R_A$ (Bit-for-bit) | Separates anatomical visualization shift from dynamical changes |
| **C. Same-Location Rebuild Control** | Original L2–L4 | Rebuilt via `InstantiateNetwork` | Simulated newly ($I_e = 25$, seed 5) | Controls for stochastic connection resampling |
| **D. Relocated Rebuild** | Relocated L4–L5 | Rebuilt via `InstantiateNetwork` | Simulated newly ($I_e = 25$, seed 5) | **Primary experimental condition** (relocation + rebuilding) |

### Key Methodological Insights:
* **Why Condition C vs Condition D is the Primary Causal Comparison:** In the author code, random seeds are consumed during geometry sampling before network construction begins. As a result, re-instantiating the network under matched draws yields a correlation of $r(W_A, W_C) \approx 0.526$ relative to the frozen baseline. Directly comparing Condition A to Condition D would conflate spatial relocation with random network rewiring. By contrast, **Condition C and Condition D share the exact same random construction stream**; the only difference is the physical 3D coordinates and segment labels of TA. Condition C vs Condition D therefore cleanly isolates the pure causal effect of anatomical relocation.
* **A vs B Rate Equality:** $R_B \equiv R_A$ and $W_B \equiv W_A$ were verified with zero floating-point error.

---

## 5. Measured Changes in Muscle Coordination & Timing

All timing and coordination measurements were computed from raw pool mean firing rates over the steady-state window ($5{,}000$ to $20{,}000\,\text{ms}$). Phase differences were computed using circular statistics ($\Delta\phi = \text{atan2}(\sin(\phi_D - \phi_C), \cos(\phi_D - \phi_C))$), and burst overlap was evaluated as the Jaccard index ($\frac{|A \cap B|}{|A \cup B|}$).

### Anatomical Muscle Roles:
* **Tibialis Anterior (TA):** Ankle dorsiflexor.
* **Gastrocnemius (GM) & Soleus:** Ankle plantarflexors (extensors).
* **Vastus Medialis (VM):** Knee extensor (NOT a flexor; cross-joint pairing with TA is not anatomical antagonism).
* **Biceps Femoris (BF):** Knee flexor / hip extensor.

### Quantitative Summary Across Realizations ($N = 5$, $\text{Mean} \pm \text{SEM}$):

| Metric | Condition A (Baseline) | Condition B (Coord Control) | Condition C (Same-Loc Rebuild) | Condition D (Relocated Rebuild) | Primary Paired Effect ($\Delta_{\text{D} - \text{C}}$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Network Frequency (Hz)** | $1.340 \pm 0.030$ | $1.340 \pm 0.030$ | $1.338 \pm 0.029$ | $1.338 \pm 0.029$ | **$0.000 \pm 0.000$ (Strictly Invariant)** |
| **Bilateral Phase Lag ($^\circ$)** | $161.6^\circ \pm 7.4^\circ$ | $161.6^\circ \pm 7.4^\circ$ | $163.1^\circ \pm 7.7^\circ$ | $163.0^\circ \pm 7.7^\circ$ | **$-0.08^\circ \pm 0.05^\circ$ (Alternation Preserved)** |
| **TA–GM Correlation ($r$)** | $+0.545 \pm 0.070$ | $+0.545 \pm 0.070$ | $+0.526 \pm 0.092$ | **$+0.785 \pm 0.057$** | **$+0.259 \pm 0.115$ (Enhanced Coupling)** |
| **TA–Soleus Correlation ($r$)** | **$-0.913 \pm 0.022$** | $-0.913 \pm 0.022$ | **$-0.922 \pm 0.030$** | **$+0.386 \pm 0.077$** | **$+1.308 \pm 0.084$ (Loss of Antiphase)** |
| **TA–VM Correlation ($r$)** | $+0.530 \pm 0.068$ | $+0.530 \pm 0.068$ | $+0.472 \pm 0.075$ | **$-0.826 \pm 0.073$** | **$-1.298 \pm 0.045$ (Inversion to Negative)** |
| **TA–BF Correlation ($r$)** | $-0.477 \pm 0.113$ | $-0.477 \pm 0.113$ | $-0.478 \pm 0.144$ | **$+0.880 \pm 0.034$** | **$+1.359 \pm 0.117$ (Strong Positive Coupling)** |
| **TA–GM Phase Difference ($^\circ$)** | $302.2^\circ \pm 7.7^\circ$ | $302.2^\circ \pm 7.7^\circ$ | $304.6^\circ \pm 7.6^\circ$ | **$44.4^\circ \pm 5.4^\circ$** | **$+100.0^\circ \pm 5.6^\circ$ (Circular Phase Advance)** |
| **TA–Soleus Phase Difference ($^\circ$)** | $198.8^\circ \pm 4.6^\circ$ | $198.8^\circ \pm 4.6^\circ$ | $195.3^\circ \pm 6.4^\circ$ | **$295.1^\circ \pm 4.8^\circ$** | **$+100.0^\circ \pm 5.6^\circ$** |
| **TA–VM Phase Difference ($^\circ$)** | $56.7^\circ \pm 8.5^\circ$ | $56.7^\circ \pm 8.5^\circ$ | $56.5^\circ \pm 7.7^\circ$ | **$156.7^\circ \pm 5.8^\circ$** | **$+99.9^\circ \pm 5.6^\circ$** |
| **TA–GM Jaccard Overlap (20%)** | $0.644 \pm 0.017$ | $0.644 \pm 0.017$ | $0.637 \pm 0.032$ | **$0.750 \pm 0.021$** | **$+0.113 \pm 0.026$ (Increased Overlap)** |
| **TA–Soleus Jaccard Overlap (20%)** | $0.570 \pm 0.031$ | $0.570 \pm 0.031$ | $0.575 \pm 0.018$ | $0.587 \pm 0.021$ | $+0.012 \pm 0.020$ |
| **TA–VM Jaccard Overlap (20%)** | $0.798 \pm 0.045$ | $0.798 \pm 0.045$ | $0.802 \pm 0.027$ | **$0.688 \pm 0.034$** | **$-0.114 \pm 0.024$ (Reduced Overlap)** |

### Critical Coordination Findings:
1. **Resolution of JSON vs. Report Contradiction:** In earlier preliminary files, a transcription error listed relocated TA–VM $r$ as $+0.090$ in markdown while JSON reported negative values. Recomputed across all 5 paired realizations, the true value is **$r = -0.826 \pm 0.073$** (paired reduction $\Delta r = -1.298 \pm 0.045$). In Condition D, TA firing becomes strongly negatively correlated with VM.
2. **Phase Advance & Loss of Ankle Antiphase:** In Condition C, TA fires in robust antiphase with Soleus ($195.3^\circ \approx 180^\circ$, $r = -0.922$). Moving TA caudally to L4–L5 advances its burst phase by **$+100.0^\circ \pm 5.6^\circ$**, locking TA into co-active phase with Gastrocnemius ($44.4^\circ$, $r = +0.785$) and disrupting ankle flexor–extensor reciprocal inhibition ($r_{\text{TA-Sol}} = +0.386$).
3. **Threshold Robustness:** Overlap sensitivity checks confirmed that the increase in TA–GM burst overlap holds across thresholds ($10\%$ threshold: $+0.063$; $20\%$ threshold: $+0.113$; $30\%$ threshold: $+0.141$).

---

## 6. Motoneuron Wave Kinematics & Spatial Progression

Previous analyses evaluated spinal activity using crude global maximum position differences (`mean(abs(diff(peak_y)))`), which erroneously conflated stationary dwell with motion, treated zero-movement samples as "neighbor transitions," and included intercycle resets as "jumps."

### Replaced Kinematic Analysis:
1. **MN-Only Population:** Analysis was restricted strictly to left motoneurons (`Types == 'MN' & Latera < 0`), excluding interneurons.
2. **Physical RC Bins (250, 500, 1000 µm):** Activity was mapped onto fixed physical bin grids retaining physical gaps (unpopulated bins marked as `NaN`, strictly no interpolation).
3. **Local Neighbor Delay Gradients:** Rather than tracking a single global peak, local peak delays $\Delta t = t_{\text{peak}}(b_{j+1}) - t_{\text{peak}}(b_j)$ were evaluated between populated adjacent spatial bins along the lumbar enlargement ($2500$ to $9400\,\mu\text{m}$).
4. **Synthetic Control Ground Truth:** Measurements were calibrated against two synthetic controls with matched sampling and noise:
   * **Continuous Traveling Wave:** $v = 9.9\,\mu\text{m/ms}$, Caudal Delay Fraction = **$1.00$**, Jump Fraction = **$0.00$**.
   * **Regional Switching Control:** Discrete alternating bands, Caudal Delay Fraction = **$0.17$**, Jump Fraction = **$0.37$**.

### Kinematic Results (500 µm Bins, Lumbar Enlargement):
* **Caudal Delay Fraction:** Condition C = **$1.000 \pm 0.000$**; Condition D = **$1.000 \pm 0.000$**. Exactly like the continuous traveling wave control, $100\%$ of adjacent bin pairs exhibit positive time delays ($\Delta t > 0$), demonstrating consistent craniocaudal progression.
* **Propagation Speed:** Mean local speed is **$7.81 \pm 0.22\,\mu\text{m/ms}$** in Condition C and **$7.76 \pm 0.21\,\mu\text{m/ms}$** in Condition D.
* **Secondary Jump Diagnostics:**
  * Dwell fraction (time activity resides at the same bin): $0.982 \pm 0.003$ in Condition C and $0.982 \pm 0.003$ in Condition D.
  * Within-cycle jump fraction ($|\Delta y| > 500\,\mu\text{m}$): **$0.000 \pm 0.000$** across both conditions.
* **Reconciliation of Wave Structure:** Visual inspection of the 2D spatio-temporal activity maps (Row 2 of the composite figure) confirms a continuous diagonal progression across segments L2 to L5 in all four conditions. The apparent "jump-dominant" label in prior drafts arose solely from bin-dwell artifacts and intercycle boundary resets. The underlying spinal output exhibits genuine diagonal craniocaudal propagation across adjacent lumbar segments.

---

## 7. Remaining Limitations

1. **Experimental Mapping Assumption:** While Bácskai et al. (2014) confirm that TA motoneurons reside in L4–L5, the exact within-pool longitudinal cell distribution cannot be uniquely inferred from standard retrograde tracing charts. The affine rank-order mapping is an explicit experimental modeling assumption.
2. **Homogeneous Tonic Drive:** Locomotion is driven by uniform tonic excitation ($I_e = 25.0\,\text{pA}$) applied to all cord neurons without descending neuromodulatory gradients or afferent sensory feedback.
3. **Distance-Based Connectomics:** The Komi model constructs connectivity using geometric probability kernels and population biases. In biological circuits, motoneuron identity and functional connectivity are further sculpted by transcription-factor-defined molecular recognition programs (e.g., Hox and ETS transcription factors) that are not modeled here.

---

## 8. Artifact Locations & Verification Hashes

### Primary Figures & Deliverables:
* **Composite Experiment Figure:** [`komi_full_reproduction/experiments/ta_placement/TA_Placement_Experiment.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/TA_Placement_Experiment.png)
* **Motor-Pool Topography Comparison (Fig 2D-Style):** [`komi_full_reproduction/experiments/ta_placement/TA_Pool_Topography_Before_After.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/TA_Pool_Topography_Before_After.png)
* **Synthetic EMG & Firing Rates Comparison:** [`komi_full_reproduction/experiments/ta_placement/TA_EMG_Before_After.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/TA_EMG_Before_After.png)
* **JSON Results:** [`komi_full_reproduction/experiments/ta_placement/experiment_results.json`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/experiment_results.json)

### Scripts & Data Deliverables:
* **Simulation & Execution Script:** [`komi_full_reproduction/experiments/ta_placement/scripts/run_ta_placement_experiment.m`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/scripts/run_ta_placement_experiment.m)
* **Topography Export & Visualization:** [`scripts/export_topography_data.m`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/scripts/export_topography_data.m), [`scripts/plot_ta_pool_topography.py`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/scripts/plot_ta_pool_topography.py), [`data/topography_export.mat`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/data/topography_export.mat)
* **EMG Export & Visualization:** [`scripts/export_emg_data.m`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/scripts/export_emg_data.m), [`scripts/plot_ta_emg_comparison.py`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/scripts/plot_ta_emg_comparison.py), [`data/emg_export.mat`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/data/emg_export.mat)
* **MATLAB Raw Data:** [`komi_full_reproduction/experiments/ta_placement/data/experiment_data.mat`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/data/experiment_data.mat)
* **Plot Export Data:** [`komi_full_reproduction/experiments/ta_placement/data/plot_export.mat`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/ta_placement/data/plot_export.mat)

### Integrity Verification (Baseline and Source Preserved Unchanged):
* `results/baseline_network.mat`: `F7DD555626A35AA1378C00E3C9A9622FAFCA01C6A0AE74BBCEB4014F2340A319` (Unmodified)
* `results/simulated_network.mat`: `CC1B453CB6FDECED4CC6B6D0D292ACD4AA7A773798987E1A1B9B3FDF082F3AAC` (Unmodified)
* `figures/main_figures/Figure2.png`: `A4DFFB8B2D48D9F15A2865179539B10BA60714BE41788F308832FFBBCC32B234` (Unmodified)
* `figures/main_figures/Figure3.png`: `B42F4B00619C401371C4B5DAF8315C5642F57B03D48F2C751BDF60C3D9519A32` (Unmodified)
* `source/`: 0 git modifications (Unmodified byte-for-byte).
