# Spatiotemporal Activation of Lumbosacral Motoneurons in the Locomotor Step Cycle

**Computational Reproduction of Yakovenko et al. (2002)**  
*Journal of Neurophysiology* 87(3): 1542–1553. DOI: [10.1152/jn.00479.2001](https://doi.org/10.1152/jn.00479.2001)

---

## 1. Project Overview

This sub-project is an independent, self-contained computational reproduction of the 3D spatiotemporal model of cat lumbosacral spinal motoneuron activation during normal locomotion from **Yakovenko et al. (2002)**.

The central scientific goals of Yakovenko et al. (2002) were:
1. Reconstruct the 3D anatomical layout of **27 hindlimb motoneuron pools** across the cat lumbosacral enlargement ($L_4 \to S_1$, $28.8\text{ mm}$ length, 30 transverse slices, 100 normalized levels, 4,034 total motoneurons).
2. Synthesize standardized piecewise-linear electromyographic (EMG) profiles for the 27 muscles across the normalized step cycle ($30\%$ swing / $70\%$ stance).
3. Compute the dynamic 3D spatiotemporal recruitment of spinal motoneurons, longitudinal slice activity profiles, and center-of-activity trajectories ($r_{\text{cm}}(t)$) across four recruitment conditions.
4. Evaluate the functional role of bifunctional hamstrings and digit flexors (the **"retractor"** group: BFp, Gracilis, ST, SMp, FDL) and test classical hypotheses of CPG organization (e.g. half-center balance vs. distributed unit oscillators).

---

## 2. Directory Structure

```text
yakovenko_2002_reproduction/
├── pyproject.toml                     # Package configuration and pytest settings
├── README.md                          # Master documentation (this file)
├── FINAL_REPRODUCTION_AUDIT.md        # Comprehensive panel-by-panel scientific audit
├── FINAL_REPRODUCTION_REPORT.md       # Comprehensive scientific report
│
├── FIGURE1_PLAN.md                    # Pre-implementation blueprint for Figure 1
├── FIGURE1_REPRODUCTION.md            # Detailed scientific report for Figure 1
├── FIGURE2_PLAN.md                    # Pre-implementation blueprint for Figure 2
├── FIGURE2_REPRODUCTION.md            # Detailed scientific report for Figure 2
├── FIGURE3_PLAN.md                    # Pre-implementation blueprint for Figure 3
├── FIGURE3_REPRODUCTION.md            # Detailed scientific report for Figure 3
├── FIGURE4_PLAN.md                    # Pre-implementation blueprint for Figure 4
├── FIGURE4_REPRODUCTION.md            # Detailed scientific report for Figure 4
├── FIGURE5_PLAN.md                    # Pre-implementation blueprint for Figure 5
├── FIGURE5_REPRODUCTION.md            # Detailed scientific report for Figure 5
│
├── src/                               # Source modules
│   ├── anatomy.py                     # 30-slice cat lumbosacral anatomy & 27 MN pools
│   ├── emg_profiles.py                # 27 muscle standardized piecewise-linear EMG profiles
│   ├── spatiotemporal_model.py        # 3D/slice activity grid & center of mass trajectory r_cm(t)
│   ├── figure1_analysis.py            # Figure 1 3D pool models & unit oscillator metrics
│   ├── figure2_analysis.py            # Figure 2 Rostrocaudal MN distributions (2A, 2B, 2C)
│   ├── figure3_analysis.py            # Figure 3 27-Muscle EMG chart (Flexor/Extensor/Retractor)
│   ├── figure4_analysis.py            # Figure 4 3D Spatiotemporal surface plot (2 cycles)
│   └── figure5_analysis.py            # Figure 5 Plan views & center of mass trajectories (5A-5D)
│
├── tests/                             # Automated test suite (30/30 tests passing)
│   ├── test_anatomy.py                # Tests for dimensions, 27 pools, and Table 1 consistency
│   ├── test_emg_profiles.py           # Tests for EMG profiles, normalization, and bounds
│   ├── test_spatiotemporal_model.py   # Tests for activity summation, r_cm(t), and velocities
│   ├── test_figure1.py                # Tests for Figure 1 plots & unit oscillator distances
│   ├── test_figure2.py                # Tests for Figure 2A-2C distributions & exact Table 1 match
│   ├── test_figure3.py                # Tests for Figure 3 EMG chart generation
│   ├── test_figure4.py                # Tests for Figure 4 3D surface plot generation
│   └── test_figure5.py                # Tests for Figure 5A-5D plan views & trajectory metrics
│
├── plots/                             # Generated publication-quality figures (300 DPI)
│   ├── figure1_mn_pool_anatomy.png    # Composite Figure 1 (Hip, Knee, Ankle 3D models)
│   ├── figure2_mn_distributions.png   # Composite Figure 2 (2A, 2B, 2C Rostrocaudal distributions)
│   ├── figure3_emg_profiles.png       # Composite Figure 3 (27 muscle EMG chart)
│   ├── figure4_spatiotemporal_activity.png # Composite Figure 4 (3D Spatiotemporal surface)
│   └── figure5_parametric_sensitivity.png  # Composite Figure 5 (5A, 5B, 5C, 5D plan views)
│
├── results/                           # Quantitative data outputs (JSON & CSV)
│   ├── master_figure_summary.csv      # Unified Master Table across Figures 1–5
│   ├── master_figure_summary.json     # Machine-readable Master Table
│   ├── final_reproduction_audit.json  # Machine-readable audit
│   ├── table1_rostral_caudal_counts.csv # Exact Table 1 comparison
│   ├── figure1_pool_centers_of_mass.csv # Centers of mass and rostrocaudal ranges
│   ├── figure4_spatiotemporal_grid.npz  # 30 slices x 200 time bins activity matrix
│   └── figure5_center_of_mass_trajectories.csv # r_cm(t), velocity, and displacement metrics
│
├── run_figure1_reproduction.py        # Runner for Figure 1
├── run_figure2_reproduction.py        # Runner for Figure 2
├── run_figure3_reproduction.py        # Runner for Figure 3
├── run_figure4_reproduction.py        # Runner for Figure 4
├── run_figure5_reproduction.py        # Runner for Figure 5
└── run_all_reproduction.py            # Master pipeline runner for Figures 1–5
```

---

## 3. Running the Reproduction

### Run Master Pipeline
```bash
python yakovenko_2002_reproduction/run_all_reproduction.py
```

### Run Test Suite
```bash
pytest yakovenko_2002_reproduction/tests
```
*Result: 30 passed in ~18s.*

---

## 4. Master Results Summary

| Figure | Published Phenomenon | Reproduction Finding | Epistemic Class | Status |
| :--- | :--- | :--- | :---: | :---: |
| **Figure 1** | 3D MN pool columns; unit oscillator half-centers separated by 20–61 levels. | 27 pools mapped; Hip separation $= 61.8\text{ lvl}$, Knee $= 55.8\text{ lvl}$, Ankle $= 25.5\text{ lvl}$. | **[DR]** | **Verified** |
| **Figure 2 & Table 1** | 4,034 MNs; severe extensor/caudal bias ($77\%$ extensors caudal, $81\%$ flexors rostral). | Exact 100% match across all 12 cells of Table 1 ($4,034\text{ MNs}$). | **[DR]** | **Verified** |
| **Figure 3** | 27 standardized piecewise linear EMG profiles (30% swing / 70% stance). | 27 normalized profiles; flexor swing bursts, extensor stance & $E_1$ bursts, retractor stance-swing bursts. | **[DR]** | **Verified** |
| **Figure 4** | 3D spatiotemporal landscape; dominant caudal stance peak ($\approx 204\text{ MNs/slice}$). | $30 \times 200$ activity grid; caudal stance peak $\approx 204\text{ MNs}$, small rostral swing peak. | **[MD]** | **Verified** |
| **Figure 5** | Plan views (5A-5D) & center of mass trajectory $r_{\text{cm}}(t)$; caudal detour arrows a, b, c. | Displacement spans $39.5\text{ levels}$ ($11.3\text{ mm}$, $52.9\%$ of range); velocities $217 - 438\text{ mm/s}$. | **[MD]** | **Verified** |

---

## 5. Verification Summary

- **Total Repository Tests for Yakovenko**: **30/30 passed (100% pass rate)**.
- **Independence**: The Komi et al. (2026) codebase and test suite (**64/64 passed**) remain completely untouched and isolated.
