# Continuation Guide: Running and Extending the Komi et al. (2026) Reproduction at Home

This repository branch (`komi-home-continuation`) contains the complete codebase, validated reproduction pipeline, and experiment suites for the **Komi et al. (Nature Communications, 2026)** spinal cord network model and TA-relocation studies.

---

## 1. Quick Start: Clone and Setup on Your Home Laptop

Clone the dedicated continuation branch directly from GitHub:

```bash
git clone -b komi-home-continuation https://github.com/islamdv02/reproduction.git
cd reproduction/komi_full_reproduction
```

### System Requirements
- **Operating System:** Windows, macOS, or Linux.
- **RAM:** 16 GB minimum recommended (32 GB preferred for running 22-second full-cord ODE simulations).
- **Disk Space:** ~10 GB free space (to store regenerated simulation `.mat` files).

---

## 2. Software & Environment Requirements

### A. MATLAB Setup
- **Recommended Version:** MATLAB R2024b or higher (R2023b+ compatible).
- **Required MATLAB Toolboxes:**
  1. **Statistics and Machine Learning Toolbox** (principal component analysis, probability distributions, clustering).
  2. **Signal Processing Toolbox** (cross-correlation, peak detection, cycle filtering).
  3. **Image Processing Toolbox** (anatomical spatial masks and polygon boundary operations).
  4. **Parallel Computing Toolbox** (recommended for parallelizing multi-seed or multi-condition simulations).

> [!NOTE]
> All custom author classes (`@Network`, `@NetworkParameters`, `@Celltype`, `@SpinalCordGeometry`, `@SpinalCordGenetics`) and author utility libraries are located in `source/` and are automatically added to the MATLAB path by the execution scripts.

### B. Python Setup (For Composites and Scientific Diagnostics)
- **Python Version:** 3.10, 3.11, or 3.12.
- **Required Packages:**
  ```bash
  pip install numpy scipy matplotlib h5py pillow
  ```

---

## 3. Large Excluded Files & Simulation Regeneration

To comply with GitHub's 100 MB file limit and avoid gigabyte-scale Git bloat, large generated simulation arrays and high-dimensional sequencing matrices were excluded from this Git repository. Local copies were preserved on the lab machine, and all necessary files can be easily regenerated or downloaded.

### A. Simulation Files to Regenerate Locally

| File Path | Typical Size | Regeneration Script | Estimated Runtime | Notes |
|---|---|---|---|---|
| `results/baseline_network.mat` | ~404 MB | `scripts/run_baseline_simulation.m` | ~2–3 min | Instantiates 4,934-neuron baseline network (`net_seed = 42`). |
| `results/simulated_network.mat` | ~2.7 GB | `scripts/run_baseline_simulation.m` | ~8–12 min | 22-second ODE simulation (`I_e = 25.0 pA`, `simSeed = 5`). |
| `results/figure4_simulation.mat` | ~1.3 GB | `scripts/run_figure4_reproduction.m` | ~6–8 min | Descending tract recruitment simulation. |
| `results/figure5_simulations.mat` | ~900 MB | `scripts/run_figure5_reproduction.m` | ~5–7 min | Speed modulation / ablation simulations. |
| `experiments/ta_placement/data/experiment_data.mat` | ~611 MB | `experiments/ta_placement/scripts/run_ta_placement_experiment.m` | ~15–20 min | Condition C vs D comparison (seeds 42 & 5). |
| `experiments/all_pool_analysis/data/ta_relocated_all_pools.mat` | ~245 MB | Tracked via **Git LFS** (`git lfs pull`) | Instant (LFS) / ~8–10 min if re-simulating | Condition D all-motoneuron rate matrix $R_{\text{MN}}$ ($1{,}795 \times 22{,}000$). Included via Git LFS! |

> [!NOTE]
> `ta_relocated_all_pools.mat` is tracked via **Git LFS** on this branch (`komi-home-continuation`). When cloning on your home laptop, ensure Git LFS is installed (`git lfs install`) and run `git lfs pull` to download the file directly.

### B. Large Author Genetics Input Files (>100 MB)
Two original sequencing count matrices exceed GitHub's upload limits:
1. `source/03_SpinalCordGeneticsFiles/matCountSingleCell.mat` (299.6 MB)
2. `source/03_SpinalCordGeneticsFiles/matCountSpatialScaled.mat` (116.0 MB)

**Original Download Location:**
Both files are publicly available from the author repository at [BergLab/SpinalProjectome](https://github.com/BergLab/SpinalProjectome/tree/main/03_SpinalCordGeneticsFiles).

**How to Download:**
```bash
# Optional: Only needed if rebuilding cell-type genetics from scratch
git clone https://github.com/BergLab/SpinalProjectome.git
cp SpinalProjectome/03_SpinalCordGeneticsFiles/matCountSingleCell.mat source/03_SpinalCordGeneticsFiles/
cp SpinalProjectome/03_SpinalCordGeneticsFiles/matCountSpatialScaled.mat source/03_SpinalCordGeneticsFiles/
```
> [!TIP]
> You do **not** need these two files to run network simulations or figure analyses! The spatial transcriptomics spot assignments and cell-type weights are fully encapsulated in `source/01_SpinalGeometryFiles/matGeometry.mat` (3.05 MB), which is **already included** in this repository.

---

## 4. Execution Workflow

All scripts should be executed from within `komi_full_reproduction/`.

### Step 1: Run Baseline Simulation
Generate the baseline 3D network and 22-second tonic drive simulation:
```matlab
% In MATLAB command window:
cd('path/to/reproduction/komi_full_reproduction');
run('scripts/run_baseline_simulation.m');
```
This produces `results/baseline_network.mat` and `results/simulated_network.mat`.

### Step 2: Regenerate Figure Reproduction Panels
```matlab
run('scripts/run_figure2_reproduction.m');
run('scripts/run_figure3_reproduction.m');
run('scripts/run_figure4_reproduction.m');
run('scripts/run_figure5_reproduction.m');
```
To assemble the high-resolution publication composites:
```bash
python scripts/build_figure1_composite.py
python scripts/build_figure2_composite.py
python scripts/build_figure3_composite.py
python scripts/build_figure4_composite.py
python scripts/build_figure5_composite.py
python scripts/build_comparison_pdf.py
```

### Step 3: Run the TA Placement Experiment
Simulate Condition C (same-location rebuilt control) vs Condition D (relocated to L4–L5):
```matlab
run('experiments/ta_placement/scripts/run_ta_placement_experiment.m');
```
Assemble the experimental diagnostic figures:
```bash
python experiments/ta_placement/scripts/plot_ta_placement_results.py
python experiments/ta_placement/scripts/plot_ta_pool_topography_before_after.py
python experiments/ta_placement/scripts/plot_ta_emg_before_after.py
```

### Step 4: Run the All-Pool Analysis (TA-Relocated Model)
Extract all 14 hindlimb motor pools from Condition D:
```matlab
run('experiments/all_pool_analysis/scripts/simulate_ta_relocated_all_pools.m');
```
Run the rigorous all-pool timing, neighboring-bin delay, and composite rendering pipeline:
```bash
python experiments/all_pool_analysis/scripts/analyze_and_plot_all_pools.py
```
This generates:
- `experiments/all_pool_analysis/AllPool_Hip_Knee_Ankle_TA_Relocated.png`
- `experiments/all_pool_analysis/all_pool_metrics.json`
- `experiments/all_pool_analysis/pool_inventory.csv`

---

## 5. Repository Structure Overview

```
komi_full_reproduction/
├── CONTINUE_AT_HOME.md               # This setup and continuation guide
├── REPRODUCTION_STATUS.md            # Comprehensive scientific status report
├── PANEL_VALIDATION.md               # Subpanel-by-subpanel validation matrix
├── Komi_reproduction_comparison.pdf  # Side-by-side reproduction PDF report
├── source/                           # Complete author model classes & geometry
│   ├── 00_SpinalNetworkModel/        # @Network, @Celltype, @SpinalCordGeometry
│   ├── 01_SpinalGeometryFiles/       # matGeometry.mat, matDescending.mat, ZeroMap.mat
│   ├── 02_HelperFunctions/           # BalanceConnectivity, GenerateSynapticDistrib
│   └── 04_Utilities/                 # Colormaps, ChannelMaps, genetic algorithm
├── scripts/                          # Main reproduction pipelines
│   ├── run_baseline_simulation.m     # Core network & simulation builder
│   ├── run_figure2_reproduction.m    # Figure 2 anatomy & projectome
│   ├── run_figure3_reproduction.m    # Figure 3 traveling wave & PCA
│   ├── run_figure4_reproduction.m    # Figure 4 descending tracts
│   ├── run_figure5_reproduction.m    # Figure 5 speed control & ablation
│   └── compat/                       # Native fallback functions for MATLAB
├── figures/                          # Generated figures & published comparisons
│   ├── main_figures/                 # High-resolution Figures 1–5 composites
│   ├── subpanels_fig2/ to fig5/      # Individual subpanels
│   └── comparisons/                  # Side-by-side published vs reproduced
├── results/                          # JSON metrics, CSV inventories, tables
│   ├── reproduction_metrics.json     # Quantitative validation metrics
│   ├── motoneuron_pools.csv          # 18-pool inventory & coordinates
│   └── wave_baseline/                # Wave baseline benchmarks
└── experiments/                      # Specialized research experiments
    ├── ta_placement/                 # TA relocation experiment (Conditions A-D)
    │   ├── scripts/                  # Simulation & plotting scripts
    │   ├── TA_Placement_Experiment.png
    │   ├── TA_Pool_Topography_Before_After.png
    │   ├── TA_EMG_Before_After.png
    │   └── EXPERIMENT_SUMMARY.md
    └── all_pool_analysis/            # Hip, knee, ankle all-pool study (Condition D)
        ├── scripts/                  # simulate_ta_relocated_all_pools.m & python analyzer
        ├── data/mn_metadata.json     # Ground truth metadata for all 1,795 motoneurons
        ├── AllPool_Hip_Knee_Ankle_TA_Relocated.png
        ├── all_pool_metrics.json
        ├── pool_inventory.csv
        └── ALL_POOL_SUMMARY.md
```

---

## 6. Key Scientific Findings & Context

1. **TA Relocation Impact:**
   - In baseline ($L2–L4$, centroid $4549\ \mu\text{m}$), TA fires at $\sim 280^\circ$ (in phase with *Iliopsoas*, $r = +0.88$; anti-phase with *Soleus*, $r = -0.76$).
   - When relocated to verified anatomical boundaries ($L4–L5$, centroid $6773\ \mu\text{m}$), TA shifts to **$29.2^\circ$**, firing synchronously with caudal extensors (*Gluteus* $r = +0.94$, *Soleus* $r = +0.89$, *Gastrocnemius* $r = +0.86$).
   - In a proximity-dependent connectome ($\sigma = 500\ \mu\text{m}$), anatomical relocation embeds TA into the caudal extensor wave, causing physiological co-contraction.
2. **Anatomical Wave Progression:**
   - Timing advances steadily from rostral to caudal across the lumbar enlargement ($1500–9500\ \mu\text{m}$) with positive signed delays ($\Delta t \approx 54–57\ \text{ms}$ per 500 µm, $v \approx 8.8–9.2\ \text{mm/s}$, consistency $R_\Delta > 0.9999$).
   - Wavefront traversal exceeds $1.5$ full locomotor cycles ($559.3^\circ$), meaning spatial wavelength ($\lambda \approx 6.8\ \text{mm}$) is shorter than cord length ($10.7\ \text{mm}$), producing multiple concurrent active bands in space-time maps.
