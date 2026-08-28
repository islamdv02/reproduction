# Method Transfer Mapping: Komi et al. (2026) Framework Applied to Yakovenko et al. (2002) Biological Data

**Purpose**: This document provides the explicit conceptual, mathematical, and algorithmic mapping between the biological datasets of **Yakovenko et al. (2002)** and the computational network architecture of **Komi et al. (2026)**.

---

## 1. Executive Concept

| Dimension | Yakovenko et al. (2002) Original Approach | Komi et al. (2026) Transferred Methodology | Scientific Purpose of Transfer |
| :--- | :--- | :--- | :--- |
| **Model Type** | Descriptive / Kinematic reconstruction ($A(s, t) = \sum N_{m,s} \cdot \text{EMG}_m(t)$) | Generative recurrent rate dynamics ($\tau \dot{R}_i = -R_i + f(\sum W_{ij} R_j + I)$) | Test whether recurrent network dynamics autonomously generate locomotor waves in cat anatomy. |
| **Spatial Organization** | Discrete 30 slices / 100 levels from $L_4 \to S_1$ ($28.8\text{ mm}$) | 3D continuous coordinates ($X, Y, Z$) + anisotropic projection kernels | Evaluate how cat spinal geometry shapes 3D synaptic wiring and projectomes. |
| **Cell Populations** | 27 Motoneuron Pools partitioned into Flexors, Extensors, Retractors | 9 Cardinal Ventral Classes (Excitatory, Inhibitory, Commissural) + Motor Pools | Map functional groups into E/I/Commissural interneurons and motor targets. |
| **Connectivity** | None (purely feedforward mapping of empirical EMG to MNs) | Spatially dependent Bernoulli connectome + exact row-wise zero-sum E/I balance | Test whether emergent Mexican-hat connectivity and limit cycles arise in cat spinal cord. |
| **Phase & Dynamics** | Pre-assigned from empirical EMG (fixed 30% swing / 70% stance) | Spontaneous limit cycle dynamics, PCA phase unfolding ($\theta_i = \arg\max \text{xcorr}$), traveling waves | Test if traveling wave propagation ($v_{\text{wave}}$) and left-right alternation emerge naturally. |
| **Neuromodulation** | None (static cycle) | Decoupled gain control: Excitatory gain ($sp_3$) vs. Inhibitory gain ($sp_2$) | Test whether speed (frequency) and force (amplitude) can be independently gated in cat anatomy. |

---

## 2. Anatomical & Spatial Mapping

### A. Coordinate System Conversion
- **Longitudinal ($Z$)**:
  - *Yakovenko Data `[YAK-DATA]`*: 30 transverse slices ($0.96\text{ mm/slice}$) spanning caudal $L_4$ to rostral $S_1$ (total length $28.8\text{ mm}$), normalized to 100 levels.
  - *Komi Framework `[KOMI-METHOD]`*: Continuous coordinate $Z_i \in [0, 28.8]\text{ mm}$ sampled uniformly within each slice's anatomical boundaries.
- **Mediolateral ($X$) & Dorsoventral ($Y$)**:
  - *Yakovenko Data `[YAK-DATA]`*: $L_7$ width $= 3.6 \pm 0.04\text{ mm}$ (midline to lateral edge), DV thickness $= 5.5 \pm 0.1\text{ mm}$.
  - *Komi Framework `[KOMI-METHOD]`*: Bounded elliptical ventral horn cross-section ($X_i \in [-3.6, 3.6]\text{ mm}$, $Y_i \in [0, 5.5]\text{ mm}$).

### B. Population Abstraction Layer
Yakovenko provides motoneuron counts for 27 muscles grouped into Flexors, Extensors, and Retractors. In the Komi framework, functional interneuron populations drive these pools:
1. **Rostral Flexor Circuit (RFlex-E, RFlex-I)**: Excitatory and inhibitory interneurons co-localized with rostral flexor MN pools ($L_4 - L_6$, levels 0–50).
2. **Caudal Extensor Circuit (CExt-E, CExt-I)**: Excitatory and inhibitory interneurons co-localized with caudal extensor MN pools ($L_6 - L_7$, levels 50–90).
3. **Caudal Retractor Circuit (CRet-E, CRet-I)**: Excitatory and inhibitory interneurons co-localized with retractor MN pools (BFp, ST, SMp, Gracilis, FDL in $L_7 - S_1$, levels 60–100).
4. **Commissural Population (Comm-Contra)**: Contralaterally projecting interneurons mediating left-right cross-cord inhibition and coordination.
5. **Motoneuron Output Pools (MN-27)**: 27 specific hindlimb motor pools receiving synaptic input from premotor interneurons.

---

## 3. Projectome Construction & E/I Balancing

### A. Anisotropic Projection Kernels
Synaptic connection probability between presynaptic neuron $j$ at $(x_j, y_j, z_j)$ and postsynaptic neuron $i$ at $(x_i, y_i, z_i)$ follows Komi's 3D Gaussian kernel:
$$P(i, j) = \exp\left( -\frac{(x_i - x_j)^2}{2\sigma_{x, p}^2} - \frac{(y_i - y_j)^2}{2\sigma_{y, p}^2} - \frac{(z_i - z_j - \mu_{z, p})^2}{2\sigma_{z, p}^2} \right) \cdot \text{BiasPop}_{p}$$
where $\mu_{z, p}$ defines the directional projection bias (e.g. descending bias $\mu_z > 0$ for long-range excitatory interneurons, local/rostral bias $\mu_z \le 0$ for inhibitory interneurons).

### B. Exact Row-Wise Zero-Sum E/I Balancing
To reproduce Komi's balanced sequence generation (BSG) regime, the initial random sparsified matrix $W^{(0)}$ is balanced row-by-row for each neuron $i$:
$$W_{ij} = W_{ij}^{(0)} \cdot \left( \frac{\sum_{k \in \text{Exc}} W_{ik}^{(0)}}{\sum_{k \in \text{Inh}} |W_{ik}^{(0)}|} \right) \quad \text{for } j \in \text{Inh}$$
ensuring $\sum_j W_{ij} = 0.0 \pm 10^{-12}$ for every receiving neuron.

---

## 4. Neural Dynamics & Activation Function

Neural activity evolves according to Komi's leaky rate equation:
$$\tau \frac{dR_i(t)}{dt} = -R_i(t) + f\left( \sum_{j=1}^N W_{ij} R_j(t) + I_i^{\text{ext}}(t) + I_i^{\text{tonic}} + \eta_i(t) \right)$$
with time constant $\tau = 20\text{ ms}$, integration step $\Delta t = 1.0\text{ ms}$, tonic drive $I^{\text{tonic}}$, Gaussian noise $\eta_i(t) \sim \mathcal{N}(0, \sigma_{\text{noise}}^2)$, and compound hyperbolic tangent non-linearity:
$$f(I) = f_{\max} \tanh\left( \frac{\max(0, I - T)}{f_{\max}} \right)$$
where $f_{\max} = 100\text{ Hz}$ and threshold $T = 0.0\text{ pA}$.

---

## 5. Emergent Projectome & Phase Analysis

1. **Circular Phase Sorting**: Firing phase $\theta_i \in [0, 2\pi)$ derived from cross-correlation lag against PC1:
   $$\theta_i = \arg\max_\tau \text{xcorr}(\text{PC1}(R), R_i) \cdot \frac{2\pi}{T_{\text{cycle}}}$$
2. **Net Projectome Quantification**: Calculating net synaptic weight profile as a function of longitudinal distance $\Delta Z = z_i - z_j$:
   $$\Pi(\Delta Z) = \frac{1}{|\mathcal{S}(\Delta Z)|} \sum_{(i, j) \in \mathcal{S}(\Delta Z)} W_{ij}$$
   Testing for emergent Mexican-hat profile (local excitation peak flanked by surround inhibition).
3. **Traveling Wave Velocity ($v_{\text{wave}}$)**:
   $$v_{\text{wave}} = \frac{\Delta Z}{\Delta t_{\text{peak}}}$$
   measuring the speed of activity propagation from $L_4$ to $S_1$ along the $28.8\text{ mm}$ cat lumbar enlargement.

---

## 6. Epistemic Labels Used Throughout Project

- `[YAK-DATA]`: Directly extracted from Yakovenko et al. (2002) anatomical/EMG data.
- `[KOMI-METHOD]`: Computational equation, algorithm, or parameter transferred from Komi et al. (2026).
- `[DERIVED]`: Emergent result produced by executing the Komi framework on Yakovenko data.
- `[ASSUMPTION]`: Explicit modeling assumption required where Yakovenko data do not specify parameter.
- `[CONTROL]`: Comparative control condition (e.g. randomized geometry, unstructured connectivity, unbalanced E/I).
