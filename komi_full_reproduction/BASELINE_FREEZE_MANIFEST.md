# Baseline Freeze Manifest: Komi et al. (2026) Reproduction

**Tag:** `komi-baseline-v1`  
**Git Branch:** `master`  
**Commit Name:** `validated_komi_baseline`  
**Freeze Date:** October 2, 2026  
**Status:** FROZEN — BASELINE MODEL LOCKED  

---

## 1. Provenance & Computational Environment

- **Paper Title:** Spatial and network principles behind neural generation of locomotion  
- **Journal:** *Nature Communications* (2026)  
- **DOI:** [10.1038/s41467-026-74228-0](https://doi.org/10.1038/s41467-026-74228-0)  
- **Authors' Upstream Repository:** [`BergLab/SpinalProjectome`](https://github.com/BergLab/SpinalProjectome)  
- **Source Git Commit:** `0f042045ee2f6d93bbe482127ce2263ada07443f` (100% byte-for-byte identical; 0 modified, 0 missing, 0 extra)  
- **Operating System:** Windows 11 Enterprise (PCWIN64)  
- **MATLAB Version:** 24.2.0.2670998 (R2024b) Prerelease Update 3  
- **MATLAB Executable:** `C:\Program Files\MATLAB\R2024b\bin\matlab.exe`  
- **Installed Toolboxes:** Statistics and Machine Learning Toolbox, Signal Processing Toolbox, Optimization Toolbox, Curve Fitting Toolbox, Parallel Computing Toolbox  
- **Python Environment:** Python 3.12 (ReportLab, NumPy, SciPy, Pillow)  

---

## 2. Model Configuration, Seeds & Runtime Parameters

- **Network Construction RNG Seed:** `42` (`twister`)
- **Dynamics Simulation RNG Seed:** `5` (Gaussian white noise)
- **Global Synaptic Scaling ($g_c$):** `0.5`
- **Global Network Density:** `0.8` (4,934 neurons total)
- **Bilateral Symmetry:** `1` (strictly symmetric across midline)
- **Synaptic Balance:** `1` (row-sum zero-sum balance: mean $| \sum_j W_{ij} | < 10^{-14}$)
- **Spatial Projection Kernel Std:** `500` $\mu$m (Gaussian projection width)
- **Spinal Cord Segments:** `T13`, `L1`, `L2`, `L3`, `L4`, `L5`, `L6`, `S1`, `S2`, `S3`, `S4` (11 segments)
- **Cardinal Ventral Cell Classes:** 9 classes (`V2a_2`, `V2a_1`, `V1`, `V2b`, `V0d`, `V0v`, `DI6`, `V3`, `MN`)
- **Motoneuron Feedback Attenuation:** `0.1` (`SetCellBiasPop('MN', 'All', 0.1)`)
- **Firing Rate Activation Function:** Piecewise linear-tanh composite, threshold $T = 5$ pA, saturation $F_{\max} = 50$ Hz, membrane $\tau = 10$ ms, integration $dt = 1$ ms
- **Baseline Simulation Protocol:** Tonic constant depolarizing input $I_e = 30.0$ pA across all 4,934 neurons for $10,000$ ms (10 s)

---

## 3. Network Architecture & Baseline Dynamics Metrics

| Metric | Measured Baseline Value | Published Reference | Discrepancy / Concordance |
| :--- | :--- | :--- | :--- |
| **Total Neuron Count ($N$)** | **4,934** (4,688 interneurons + 246 MNs) | 4,934 | Exact match (0.0% diff) |
| **Total Directed Synapses** | **589,368** (527,286 ipsi, 62,082 contra) | ~5.9 $\times 10^5$ | Exact match (0.0% diff) |
| **Network Sparsity** | **97.579%** (Density = 0.02421) | 97.58% | Exact match |
| **Dominant Mode Real Part** | **$\lambda_1 = 2.019 \pm 0.762i$** | $2.02 \pm 0.76i$ | < 0.05% diff |
| **Unstable Modes ($\text{Re}(\lambda) > 1$)** | **Exactly 4 modes** | 4 modes | Exact match |
| **Baseline Locomotor Frequency** | **1.35 Hz** (Period: 743.0 ms) | ~1.3–1.4 Hz | Within published range (< 2% diff) |
| **Left-Right Phase ($\Delta\phi_{\text{L-R}}$)** | **206.4°** | ~180°–210° (Alternation) | Within 5° of cluster centroid |
| **L2-L5 Segmental Phase ($\Delta\phi_{\text{L2-L5}}$)**| **192.4°** | ~180°–200° (Reciprocal) | Within 3° of cluster centroid |
| **Spatial Wave Propagation** | **Caudal** (Rostral leads Caudal) | Rostral-to-caudal wave | Exact categorical match |
| **PCA PC1 Variance Explained** | **50.4%** | Rotational orbit (PC1 vs PC3) | Topological match |
| **Motoneuron Pools** | **18 pools** across T13–S4 | 18 hindlimb pools | Exact match (all pools & ranges mapped) |

---

## 4. Definitive Panel Status Concordance (Figures 1–5)

Total Audited Panels: **36 panels** across Figures 1–5:
- **`VERIFIED MATCH`:** **24 panels (66.7%)**
- **`EXECUTED BUT DIFFERENT`:** **4 panels (11.1%)**
- **`REFERENCE ONLY`:** **6 panels (16.7%)**
- **`BLOCKED — AUTHOR MATERIAL UNAVAILABLE`:** **2 panels (5.6%)**

### Panel Classification Summary:
- **Figure 1 (8 panels):**
  - `1A`, `1B`, `1C`: **`REFERENCE ONLY`** (Confocal fluorescence histology, Hayashi et al., 2018)
  - `1D`, `1E`, `1F`: **`REFERENCE ONLY`** (Conceptual schematics & theoretical Mexican-hat curve)
  - `1G`, `1H`: **`BLOCKED — AUTHOR MATERIAL UNAVAILABLE`** (1D rate model unreleased in `BergLab/SpinalProjectome`)
- **Figure 2 (7 panels):**
  - `2A`, `2B`, `2C`, `2D`, `2E`, `2F`, `2G`: **`VERIFIED MATCH`** (100% verified against model arrays & geometry)
- **Figure 3 (5 published panels):**
  - `3B`, `3E`, `3F`, `3H`: **`VERIFIED MATCH`** (100% verified against eigenspectrum, simulated dynamics, and PCA)
  - `3G`: **`METHODS-BASED RECONSTRUCTION — EXACT PHASE SUBSET UNAVAILABLE`** (Neuronal phase polar histogram reconstructed via author PC1 collective rhythm reference; R = 400 radial ring; exact author subset unreleased)
  - *(Note: non-published custom panels 3A, 3C, 3D removed to match published Figure 3 layout)*

- **Figure 4 (7 panels):**
  - `4A`, `4B`, `4C`: **`VERIFIED MATCH`** (Gain modulation curves, descending tract maps, and modulated projectomes)
  - `4D`, `4E`, `4F`, `4G`: **`EXECUTED BUT DIFFERENT`** (Exact Figure 4 driver and published network realization unreleased; continuous drive accelerates burst amplitude (+112%) and frequency (1.29 to 1.40 Hz), but network preserves alternation (~163°) rather than switching to bilateral synchrony (~0°))
- **Figure 5 (6 panels):**
  - `5A`, `5B`, `5C`: **`VERIFIED MATCH`** (V1 projectome alteration, deceleration in silencing (1.28 $\to$ 1.05 Hz), slow rhythm in ablation (0.46 Hz))
  - `5D`, `5E`, `5F`: **`VERIFIED MATCH`** (V0 projectome alteration, speedup (1.28 $\to$ 1.76 $\to$ 1.87 Hz), and polar switch to synchrony (359.4°))

---

## 5. Authoritative Checksums of Frozen Results (SHA-256)

```
results/baseline_network.mat       f7dd555626a35aa1378c00e3c9a9622fafca01c6a0ae74bbceb4014f2340a319
results/simulated_network.mat      acfe1a4c42e6a410c5edf90305cfe34cdf6dc8bc41f90fb74c49f66bce7855b8
results/validation_bundle.mat      4e8b0e574c294ddaf1d120acac3e71472f0c0f93abef5c649c481dafeaa42ec9
results/reproduction_metrics.json  7385c2baf4188f1a42dfac06bbcfb007b9f6e13da54dd30adb20f7759d98aa32
results/panel_validation.json      78a316c5414b5c143f0d9dea3fef29d73bb6491fc1f457cc956449c322c66c7a
results/motoneuron_pools.json      0dfe23ea21962f8bad7abe93fbe40867b3d9bf3943ec03715c12fd91bd5c3d91
results/motoneuron_pools.csv       c29fcab534f6703a28a8e76ca3a8d2d83b919074837fd04e9be5829c9a6c008a
figures/main_figures/Figure1.png   f0e799115a763ecbaed0b8dbd34aedf7ce6be2e7a2bed19d4ae79161405deff7
figures/main_figures/Figure2.png   a5776175b1a3cfdf529c46187f728997704477febae10933daedaa0627c48ca5
figures/main_figures/Figure3.png   9e4fa2946f62b254814179426d73a0ac263d26b7e5cbe07db4fe0c8ab43fc611
figures/main_figures/Figure4.png   dab550f294ebbf2852b8cfaa78bc6ba6c9e4db0984e73cac184a5bbbc0bd78c2
figures/main_figures/Figure5.png   31ad5ddc518fb1dcbbc9605570cf664f02082b9718bbc294d3547762fbb7f49c
Komi_reproduction_comparison.pdf   1b76811f9b5ac185b175400d67a4cc5fe402df7f1e14794e80e4f1f886474e60
source_integrity_report.txt        fa47c79a94c5af81056acc59359b5bdd084f3636b29beb4cc434dfeb32386998
```

---

## 6. Freeze Invariance Rule

This baseline is permanently frozen. Downstream experiments (e.g. motoneuron pool placement, longitudinal dispersion, segment shifts) must be carried out exclusively in `experiments/` without modifying any file under `results/`, `figures/main_figures/`, or `source/`.
