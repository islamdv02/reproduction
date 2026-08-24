# Biological Data Description: Mouse Spinal Cord Model

This document provides a comprehensive, rigorous description of all original biological data files from the repository [BergLab/SpinalProjectome](https://github.com/BergLab/SpinalProjectome) supporting **Komi et al., Nature Communications, 2026**.

---

## 1. Inventory of Required Biological Data Files

| File Path | Format | Size | Description / Scientific Role |
|:---|:---|:---:|:---|
| `01_SpinalGeometryFiles/matGeometry.mat` | MAT-5 (MATLAB) | 3.1 MB | Core spatial transcriptomics dataset containing 20,755 spatial voxels, 80 cell types, deconvolution weights, $(X, Y)$ spot coordinates, layer designations, and 31 segment lengths. |
| `01_SpinalGeometryFiles/matDescending.mat` | MAT-5 (MATLAB) | 64.1 KB | 16 descending motor pathway termination zone boundary polygons in transverse spinal coordinates. |
| `01_SpinalGeometryFiles/matMuscleSeg.mat` | MAT-5 (MATLAB) | 2.1 KB | Distribution matrix of motoneuron pools across spinal segments and flexor/extensor classifications for 35 muscles. |
| `04_Utilities/CellTypesCensus.xlsx` | Excel (.xlsx) | 12.8 KB | Single-nucleus RNA-seq census of 69 spinal cord cell clusters, lamina distributions, putative developmental lineages, and molecular markers. |
| `04_Utilities/MotorneuronsDistribution.xlsx` | Excel (.xlsx) | 15.3 KB | Experimental retrograde tracing data quantifying hindlimb motoneuron distribution across segments T13–S4 in mice. |
| `01_SpinalGeometryFiles/ZeroMap.mat` | MAT v7.3 (HDF5) | 13.9 KB | 2D spinal cord boundary mask matrix $(456 \times 312)$ defining anatomical margins. |
| `03_SpinalCordGeneticsFiles/matCountSingleCell.mat` | MAT-5 (MATLAB) | 306.8 MB | High-dimensional single-cell UMI count matrix across spinal cell clusters. |
| `03_SpinalCordGeneticsFiles/matCountSpatialScaled.mat` | MAT-5 (MATLAB) | 118.8 MB | High-dimensional spatial transcriptomics gene expression count matrix across 20,755 spots. |

---

## 2. File Contents & Data Structures

### A. `matGeometry.mat`
- `weights`: $(20755 \times 80)$ matrix of `float64` values $[0, 0.986]$. Represents the Robust Cell Type Deconvolution (RCTD) cell-type proportion weights at each spatial voxel.
- `RCTDCoord`: Table containing $(20755 \times 2)$ unscaled spatial coordinates (`coord_x`, `coord_y`).
- `RCTDCellTypes`: Table listing 80 cell type identifiers and neurotransmitter phenotype vector (+1 for excitatory/cholinergic, -1 for inhibitory).
- `matLayers`: Categorical classification of spots into anatomical layers (`highres`, `medres`, `lowres`: grey matter, white matter, DRG).
- `SegmentLength`: $(1 \times 31)$ array of `uint16` values containing rostrocaudal lengths (in $\mu\text{m}$) for each mouse spinal segment ($C_1$ to $Co_3$).
- `Segments`: Categorical names of all 31 spinal segments.

### B. `matDescending.mat`
Contains transverse boundary polygons for 16 descending motor pathways:
1. **Corticospinal** (Left / Right)
2. **Rubrospinal** (Left / Right)
3. **Medullary Reticulospinal** (Left / Right)
4. **Pontine Reticulospinal** (Left / Right)
5. **Medial Vestibulospinal** (Left / Right)
6. **LPGi Vglut2+ (Glutamatergic)** (Left / Right)
7. **LPGi Vglyt2+ (Glycinergic)** (Left / Right)
8. **Raphe Obscurus** (Left / Right)

### C. `matMuscleSeg.mat`
- `MuscleSeg`: Matrix of relative motoneuron proportions across spinal segments ($C_1$–$S_4$ or $T_{13}$–$S_4$) for 35 distinct muscle groups.
- `FlexExt`: Classification of each muscle pool into functional categories:
  - `Flex` (Flexor)
  - `Ext` (Extensor)
  - `Bi` (Bifunctional)
  - `Axial` (Axial / Trunk musculature)

### D. `CellTypesCensus.xlsx`
69 transcriptomically defined cell types organized as:
- `Cluster`: Cell type identifier (e.g. `MN-alpha`, `MN-gamma`, `PGC`, `CSF-cN`, `Excit-01` to `Excit-38`, `Inhib-01` to `Inhib-27`).
- `Lamina`: Anatomical laminar location (Rexed laminae 1–10).
- `%`: Relative cellular abundance in spinal cord.
- `NT`: Neurotransmitter identity (`Glut`, `GABA/Gly`, `ACh`).
- `Family`: Major neuronal class (Excitatory, Inhibitory, Motor, Sympathetic).
- `Putative Lineage`: Cardinal developmental progenitor domain ($dI1$–$dI6$, $V0$, $V1$, $V2a$, $V2b$, $V3$, $MN$).

---

## 3. Cell Numbers & Cell Types

1. **Spatial Voxels**: $N_{\text{voxels}} = 20,755$ spatial transcriptomic sequencing spots.
2. **Cell Types in Spatial Geometry Model**: 80 cell types:
   - **Excitatory Interneurons**: 38 types (`Excit-01` to `Excit-38`, Transmitter = $+1$)
   - **Inhibitory Interneurons**: 27 types (`Inhib-01` to `Inhib-27`, Transmitter = $-1$)
   - **Motor Neurons**: 2 types (`MN-alpha`, `MN-gamma`, Transmitter = $+1$)
   - **Autonomic / Sympathetic**: 1 type (`PGC` Preganglionic, Transmitter = $+1$)
   - **Cerebrospinal Fluid-contacting Neurons**: 1 type (`CSF-cN`, Transmitter = $-1$)
   - **Sensory / DRG / Peripheral Classes**: 11 types (`PEP1`–`PEP2`, `NP1`–`NP3`, `NF1`–`NF5`, `TH`, Transmitter = $+1$)
3. **Simulated Model Populations**: When instantiated with standard model density ($D = 1.0$), the model samples $N = 6,528$ neurons across the lumbar spinal cord.

---

## 4. Spatial Coordinate System & Units

The model uses a Cartesian 3D coordinate system:

| Coordinate Axis | Anatomical Direction | Scaling / Range | Physical Units |
|:---|:---|:---:|:---:|
| **$X$** | **Mediolateral (ML)** | $[-1750.0, +1750.0]$ | $\mu\text{m}$ (micrometers) |
| **$Y$** | **Dorsoventral (DV)** | $[0.0, 1613.3]$ | $\mu\text{m}$ (micrometers) |
| **$Z$** | **Rostrocaudal (RC)** | $[0.0, 11000.0]$ | $\mu\text{m}$ (micrometers) |

### Physical Calibration Rule
The raw spatial transcriptomics coordinates $\mathbf{x}_{\text{raw}}$ are scaled to the physical transverse width of the adult mouse spinal cord ($3,500\ \mu\text{m}$):
$$\text{ScaleFactor} = \frac{3500.0}{\max(\mathbf{x}_{\text{raw}}) - \min(\mathbf{x}_{\text{raw}})}$$
$$X_{\mu\text{m}} = (\mathbf{x}_{\text{raw}} - \min(\mathbf{x}_{\text{raw}})) \times \text{ScaleFactor} - 1750.0$$
$$Y_{\mu\text{m}} = (\mathbf{y}_{\text{raw}} - \min(\mathbf{y}_{\text{raw}})) \times \text{ScaleFactor}$$

---

## 5. Anatomical Regions Represented

1. **Rexed Laminae (I–X)**:
   - Superficial dorsal horn: Laminae I–II (`1Sp`, `2SpO`, `2SpL`)
   - Deep dorsal horn: Laminae III–VI (`3Sp`, `4Sp`, `5Sp`, `6Sp`)
   - Intermediate zone: Lamina VII (`7Sp`, `10Sp` around central canal)
   - Ventral horn: Laminae VIII–IX (`8Sp`, `Ad9`, `Q9`, `CFl9`, `Ps9` motoneuron columns)
2. **Spinal Cord Segments**:
   - Cervical ($C_1$–$C_8$)
   - Thoracic ($T_1$–$T_{13}$)
   - Lumbar ($L_1$–$L_6$, total length $\approx 8,100\ \mu\text{m}$)
   - Sacral ($S_1$–$S_4$, total length $\approx 4,500\ \mu\text{m}$)
   - Coccygeal ($Co_1$–$Co_3$)

---

## 6. Data Preprocessing in MATLAB Code

In `SpinalCordGeometry.m` (`GetMouseGeometry`), the following sequence of operations is performed:
1. **Grey Matter Masking**: Filtering spots to retain only grey matter voxels (`lowres == 'grey'`), removing white matter tracks and dorsal root ganglia spots.
2. **Weight Normalization**: For each cell type $k$, the RCTD weight vector $\mathbf{w}_k$ is standardized:
   $$Z(\mathbf{w}_k) = \frac{\mathbf{w}_k - \mu(\mathbf{w}_k)}{\sigma(\mathbf{w}_k)}$$
3. **Thresholding**: Spot locations with $Z(\mathbf{w}_k) > 1.0$ (or $\mathbf{w}_k > 0.4 \max(\mathbf{w}_k)$) are identified as valid anatomical locations for cell type $k$.
4. **Spatial Sampling**: Neurons are sampled across active spots with local Gaussian spatial jitter ($\sigma_{\text{jitter}} = 15\ \mu\text{m}$) and distributed along the rostrocaudal axis $[0, L_Z]$.
5. **Motor Pool Alignment**: Motoneuron positions ($\text{MN}_\alpha, \text{MN}_\gamma$) are assigned to specific motor columns and segments based on `MuscleSeg` probabilities.

---

## 7. Connection to Network Architecture

The loaded biological data directly determines all downstream structural features of the projectome network:
1. **Pairwise Spatial Distance Matrix $D_{ij}$**:
   $$D_{ij} = \sqrt{(X_i - X_j)^2 + (Y_i - Y_j)^2 + (Z_i - Z_j)^2}$$
2. **Gaussian Synaptic Probability $P_{ij}^{\text{dist}}$**:
   $$P_{ij}^{\text{dist}} = \exp\left(-\frac{D_{ij}^2}{2\sigma_{\text{spatial}}^2}\right)$$
3. **Directional & Segmental Bias Tensors**:
   - Rostrocaudal bias matrix $M_{ij}^{\text{RC}}$
   - Dorsoventral bias matrix $M_{ij}^{\text{DV}}$
   - Mediolateral / Crossed bias matrix $M_{ij}^{\text{ML}}$
   - Rexed layer connectivity matrix $M_{ij}^{\text{layer}}$
4. **EI Balance & Spectral Normalization**:
   - Synaptic weights $W_{ij}$ scaled according to transmitter vector $T_i \in \{-1, +1\}$ and spectral radius targeting stability.

---

## 8. Diagnostic Validation Figures

Diagnostic plots generated directly from the loaded data are saved in `plots/`:
- `01_3d_neuron_locations.png`: 3D scatter plot of excitatory and inhibitory neurons in $(X, Y, Z)$ coordinates.
- `02_neuron_locations_by_celltype.png`: Transverse cross-sections showing spatial distributions of motoneurons and interneurons.
- `03_cell_type_counts.png`: Bar chart of sampled cell counts across all 80 cell types color-coded by neurotransmitter.
- `04_spatial_distribution_rostrocaudal.png`: Stacked histogram along the rostrocaudal spinal cord axis showing segmental distribution.
