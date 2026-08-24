# Network and Synapse Construction Specification

This document details the mathematical framework, equations, parameters, and algorithms used to construct the spinal cord neural projectome network, faithfully reproducing **Komi et al., Nature Communications, 2026** and the original MATLAB implementation in [BergLab/SpinalProjectome](https://github.com/BergLab/SpinalProjectome).

---

## 1. Network Architecture Overview

The spinal network model simulates interconnected populations of spinal interneurons and motoneurons positioned in a realistic 3D anatomical volume representing the mouse lumbar spinal cord ($T_{13}$–$S_4$, rostrocaudal extent $\approx 11,000\ \mu\text{m}$, transverse width $3,500\ \mu\text{m}$).

### Simulated Populations
The standard locomotion circuit (configured in `InstantiateModel.m`) comprises 9 canonical ventral interneuron and motoneuron populations:
1. **$V2a\text{-}2$**: Excitatory interneurons ($T = +1$), long-range bilateral rostrocaudal projections ($L = 7,000\ \mu\text{m}$), ventrolateral, ipsilateral.
2. **$V2a\text{-}1$**: Excitatory interneurons ($T = +1$), caudal-projecting ($L = 500\ \mu\text{m}$), ventromedial, ipsilateral.
3. **$V1$**: Inhibitory interneurons ($T = -1$), rostral-projecting ($L = 2,000\ \mu\text{m}$), ventral, ipsilateral, gain $0.2$.
4. **$V2b$**: Inhibitory interneurons ($T = -1$), caudal-projecting ($L = 4,000\ \mu\text{m}$), ventrolateral, ipsilateral.
5. **$V0d$**: Inhibitory interneurons ($T = -1$), local commissural ($L = 500\ \mu\text{m}$), ventromedial, contralateral.
6. **$V0v$**: Excitatory interneurons ($T = +1$), rostral commissural ($L = 3,400\ \mu\text{m}$), intermediate/medial, contralateral.
7. **$dI6$**: Inhibitory interneurons ($T = -1$), long-range caudal commissural ($L = 5,000\ \mu\text{m}$), dorsomedial, contralateral.
8. **$V3$**: Excitatory interneurons ($T = +1$), caudal commissural ($L = 500\ \mu\text{m}$), ventrolateral, contralateral.
9. **$\text{MN}$**: Motoneurons ($T = +1$), local motor output ($L = 300\ \mu\text{m}$), ventrolateral, ipsilateral.

---

## 2. Mathematical Formulation of Connectivity

### A. Coordinate System and Pairwise Spatial Distances
For neurons $i$ (postsynaptic target) and $j$ (presynaptic source) with 3D positions $\mathbf{x}_i = (X_i, Y_i, Z_i)$ and $\mathbf{x}_j = (X_j, Y_j, Z_j)$:
- **Rostrocaudal Distance**:
  $$D_{\text{RC}}(i, j) = Z_i - Z_j$$
  $(D_{\text{RC}} > 0 \implies \text{neuron } i \text{ is caudal to } j;\ D_{\text{RC}} < 0 \implies \text{neuron } i \text{ is rostral to } j)$
- **Mediolateral Distance**:
  $$D_{\text{ML}}(i, j) = |X_i| - |X_j|$$
- **Dorsoventral Distance**:
  $$D_{\text{DV}}(i, j) = Y_i - Y_j$$
- **Crossed/Ipsilateral Coordinate**:
  $$D_{\text{CI}}(i, j) = \text{Latera}_i \cdot \text{Latera}_j \quad \text{where } \text{Latera} \in \{-1, +1\}$$
  $(D_{\text{CI}} > 0 \implies \text{ipsilateral};\ D_{\text{CI}} < 0 \implies \text{contralateral})$

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Lines 49–52.

---

### B. Directional Bias Matrices

Let $\sigma_{\text{proj}} = 500\ \mu\text{m}$ be the global projection distribution spatial standard deviation (`ProjWidth`), and $L_j$ be the characteristic axonal projection length scale of presynaptic cell type $j$ (`Parameters.LengthScales`).

#### 1. Rostrocaudal Bias $B_{\text{RC}}(i, j)$
Each cell type is assigned a rostrocaudal projection profile:
- **Caudal Projecting (`'cau'`)**:
  $$B_{\text{RC}}(i, j) = \frac{D_{\text{RC}}(i, j) - (L_j + \epsilon)}{\sigma_{\text{proj}}}, \quad \epsilon \sim \mathcal{N}(0, 0.1 L_j)$$
- **Rostral Projecting (`'ro'`)**:
  $$B_{\text{RC}}(i, j) = \frac{D_{\text{RC}}(i, j) + (L_j + \epsilon)}{\sigma_{\text{proj}}}$$
- **Bilateral Projecting (`'bi'`)**:
  $$B_{\text{RC}}(i, j) = \frac{|D_{\text{RC}}(i, j)| - (L_j + \epsilon)}{\sigma_{\text{proj}}}$$
- **Local Projecting (`'loc'`)**:
  $$B_{\text{RC}}(i, j) = \frac{D_{\text{RC}}(i, j)}{L_j + \epsilon}$$

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Lines 71–95.

#### 2. Mediolateral Bias $B_{\text{ML}}(i, j)$
- **Lateral Bias (`'lat'`)**:
  $$B_{\text{ML}}(i, j) = \begin{cases} \frac{|D_{\text{ML}}(i, j)|}{2 \sigma_{\text{proj}}}, & D_{\text{ML}} > 0 \\ \frac{|D_{\text{ML}}(i, j)|}{\sigma_{\text{proj}} / 5}, & D_{\text{ML}} < 0 \end{cases}$$
- **Medial Bias (`'med'`)**:
  $$B_{\text{ML}}(i, j) = \begin{cases} \frac{|D_{\text{ML}}(i, j)|}{\sigma_{\text{proj}} / 5}, & D_{\text{ML}} > 0 \\ \frac{|D_{\text{ML}}(i, j)|}{2 \sigma_{\text{proj}}}, & D_{\text{ML}} < 0 \end{cases}$$
- **Local Bias (`'loc'`)**:
  $$B_{\text{ML}}(i, j) = \frac{|D_{\text{ML}}(i, j)|}{\sigma_{\text{proj}} / 5}$$

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Lines 97–112.

#### 3. Dorsoventral Bias $B_{\text{DV}}(i, j)$
- **Dorsal Bias (`'dor'`)**:
  $$B_{\text{DV}}(i, j) = \begin{cases} \frac{|D_{\text{DV}}(i, j)|}{2 \sigma_{\text{proj}}}, & D_{\text{DV}} > 0 \\ \frac{|D_{\text{DV}}(i, j)|}{\sigma_{\text{proj}} / 5}, & D_{\text{DV}} < 0 \end{cases}$$
- **Ventral Bias (`'ven'`)**:
  $$B_{\text{DV}}(i, j) = \begin{cases} \frac{|D_{\text{DV}}(i, j)|}{\sigma_{\text{proj}} / 5}, & D_{\text{DV}} > 0 \\ \frac{|D_{\text{DV}}(i, j)|}{2 \sigma_{\text{proj}}}, & D_{\text{DV}} < 0 \end{cases}$$
- **Local Bias (`'loc'`)**:
  $$B_{\text{DV}}(i, j) = \frac{|D_{\text{DV}}(i, j)|}{\sigma_{\text{proj}} / 5}$$

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Lines 114–129.

#### 4. Contralateral / Ipsilateral Bias $B_{\text{CI}}(i, j)$
- **Contralateral (`'contra'`)**: $B_{\text{CI}}(i, j) = 1$ if $D_{\text{CI}} < 0$ (opposite sides), else $0$.
- **Ipsilateral (`'ipsi'`)**: $B_{\text{CI}}(i, j) = 1$ if $D_{\text{CI}} > 0$ (same side), else $0$.
- **Bilateral (`'bi'`)**: $B_{\text{CI}}(i, j) = 1$ if $D_{\text{CI}} < 0$, and $0.2$ if $D_{\text{CI}} > 0$.

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Lines 131–144.

#### 5. Population-Specific Scaling $B_{\text{pop}}(i, j)$
Specified by `SetCellBiasPop(source, target, value)`. For instance, motoneurons targeting interneurons are scaled by $0.1$:
$$B_{\text{pop}}(i, j) = 0.1 \quad \text{if } \text{Type}_j = \text{'MN'} \text{ and } \text{Type}_i \neq \text{'MN'}$$

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Line 35; `InstantiateModel.m`, Line 27.

---

### C. Joint Synaptic Probability Synthesis
The overall connection probability $P(i, j) \in [0, 1]$ combines all geometric directional biases using the geometric mean of the normalized Gaussian density functions:

$$P(i, j) = \left( \exp\left(-\frac{B_{\text{ML}}(i, j)^2}{2}\right) \cdot \exp\left(-\frac{B_{\text{DV}}(i, j)^2}{2}\right) \cdot \exp\left(-\frac{B_{\text{RC}}(i, j)^2}{2}\right) \right)^{1/3} \cdot B_{\text{CI}}(i, j) \cdot B_{\text{pop}}(i, j) \cdot B_{\text{lay}}(i, j) \cdot B_{\text{seg}}(i, j) \cdot B_{\text{MN}}(i, j)$$

Simplifying the geometric mean of Gaussians:
$$P(i, j) = \exp\left(-\frac{B_{\text{ML}}^2 + B_{\text{DV}}^2 + B_{\text{RC}}^2}{6}\right) \cdot \prod_k B_k(i, j)$$

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Lines 184–191.

---

### D. Sparsification, Synaptic Weights, and Dale's Principle

1. **Bernoulli Synapse Sampling**:
   $$S_{ij} \sim \text{Bernoulli}(P(i, j))$$
2. **Initial Weight Distribution**:
   $$W_{ij}^{\text{raw}} \sim \mathcal{N}(1.0, 0.1^2)$$
3. **Dale's Principle Sign Assignment**:
   $$W_{ij} = \begin{cases} +|W_{ij}^{\text{raw}}| \cdot g_j, & \text{if presynaptic neuron } j \text{ is Excitatory } (T_j = +1) \\ -|W_{ij}^{\text{raw}}| \cdot g_j, & \text{if presynaptic neuron } j \text{ is Inhibitory } (T_j = -1) \end{cases}$$
   where $g_j = g_c \cdot \text{SynStrength}_j$.
4. **Graph Sparsification & Self-Connection Removal**:
   $$W_{ij} \leftarrow W_{ij} \cdot S_{ij}$$
   $$W_{ii} = 0 \quad (\text{no autapses / self-synapses})$$

*Source Code Reference*: `@Network/InstantiateNetwork.m`, Lines 199–205.

---

### E. E/I Input Balancing Algorithm (`BalanceConnectivity`)
To establish stable network dynamics without runaway excitation or quiescence, each postsynaptic neuron's total excitatory and inhibitory synaptic inputs are balanced per hemichord:

For each neuron row $i$:
1. Calculate net input sum:
   $$\text{balance}_i = \sum_j W_{ij}$$
2. Excitatory and inhibitory subsets:
   $$\mathcal{E}_i = \{j \mid W_{ij} > 0\}, \quad \mathcal{I}_i = \{j \mid W_{ij} < 0\}$$
3. Balanced target values:
   $$b_i^+ = \sum_{j \in \mathcal{E}_i} W_{ij} - \frac{\text{balance}_i}{2}, \quad b_i^- = \sum_{j \in \mathcal{I}_i} W_{ij} - \frac{\text{balance}_i}{2}$$
4. Balancing scaling factors:
   $$\text{fac}_i^+ = \frac{b_i^+}{\sum_{j \in \mathcal{E}_i} W_{ij}}, \quad \text{fac}_i^- = \frac{b_i^-}{\sum_{j \in \mathcal{I}_i} W_{ij}}$$
5. Apply scaling:
   $$W_{ij} \leftarrow W_{ij} \cdot \text{fac}_i^+ \quad (\forall j \in \mathcal{E}_i)$$
   $$W_{ij} \leftarrow W_{ij} \cdot \text{fac}_i^- \quad (\forall j \in \mathcal{I}_i)$$

*Source Code Reference*: `02_HelperFunctions/BalanceConnectivity.m`, Lines 1–17.

---

### F. Spectral Radius Rescaling (`RescaleConnectivity`)
The connectivity matrix is scaled to normalize synaptic variance and control the spectral radius:
1. Calculate excitation-to-inhibition ratio:
   $$r = \frac{|\{(i, j) \mid W_{ij} > 0\}|}{|\{(i, j) \mid W_{ij} < 0\}|}$$
2. Calculate matrix sparsity:
   $$\rho = \frac{|\{(i, j) \mid W_{ij} = 0\}|}{N^2}$$
3. Variance scaling standard deviation:
   $$\sigma_{\text{scale}} = \sqrt{\rho (1 - \rho) \frac{1 + r^2}{2}} \cdot \sqrt{N}$$
4. Normalized connectivity:
   $$W_{ij} \leftarrow \frac{W_{ij}}{\sigma_{\text{scale}}}$$

*Source Code Reference*: `02_HelperFunctions/RescaleConnectivity.m`, Lines 1–8.

---

## 3. The Asymmetric Mexican-Hat Connectivity Profile

The combination of:
1. **Short-range excitation** ($\sigma_E \approx 500\ \mu\text{m}$, local $V2a$, $V3$, $MN$)
2. **Asymmetric long-range inhibition** ($\sigma_I \approx 2,000\text{--}5,000\ \mu\text{m}$, rostrally biased $V1$, caudally biased $V2b$ and $dI6$)
3. **Contralateral coordination** (inhibitory $V0d$ and excitatory $V0v$)

produces a spatial interaction kernel $\Delta W(d_{\text{RC}})$ characterized by local recurrent excitation surrounded by an asymmetric inhibitory surround along the rostrocaudal spinal cord axis, which acts as the physical substrate for travelling wave generation during locomotion.
