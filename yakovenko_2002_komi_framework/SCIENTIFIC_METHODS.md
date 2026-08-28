# Scientific Methods & Mathematical Formulations

## Mathematical Framework: Transferring Komi et al. (2026) to Yakovenko et al. (2002)

---

### 1. Spatial Coordinate Embedding

Each neuron $i \in \{1, \dots, N\}$ in the model is assigned a 3D physical position $\mathbf{r}_i = (x_i, y_i, z_i)$:
- **Rostrocaudal ($Z$)**: $z_i \in [0, L_{\text{cord}}]$ where $L_{\text{cord}} = 28.8\text{ mm}$ (cat lumbar enlargement $L_4 \to S_1$). Slices $s \in \{1, \dots, 30\}$ occupy intervals $[(s-1)\Delta z, s\Delta z]$ with $\Delta z = 0.96\text{ mm}$.
- **Mediolateral ($X$)**: $x_i \in [-w_{\text{cord}}, w_{\text{cord}}]$ where $w_{\text{cord}} = 3.6\text{ mm}$. Left hemicord: $x_i < 0$; Right hemicord: $x_i > 0$.
- **Dorsoventral ($Y$)**: $y_i \in [0, h_{\text{cord}}]$ where $h_{\text{cord}} = 5.5\text{ mm}$ (ventral horn coordinates $y \in [1.0, 4.5]\text{ mm}$).

---

### 2. Synaptic Probability & Anisotropic Projection Kernels

The connection probability between presynaptic neuron $j$ of population $p$ and postsynaptic neuron $i$ is:
$$P(i, j) = p_0 \cdot \exp\left( -\frac{(x_i - x_j)^2}{2\sigma_{x, p}^2} - \frac{(y_i - y_j)^2}{2\sigma_{y, p}^2} - \frac{(z_i - z_j - \mu_{z, p})^2}{2\sigma_{z, p}^2} \right) \cdot \Phi_{\text{side}}(i, j)$$
where:
- $p_0 = 0.15$ (baseline peak connection probability).
- $\sigma_{x, p} = 0.8\text{ mm}$, $\sigma_{y, p} = 0.8\text{ mm}$ (transverse axonal dispersion).
- $\sigma_{z, p}$ is the longitudinal axonal span:
  - Long-range Excitatory (Descending): $\sigma_{z, \text{Exc}} = 5.0\text{ mm}$, bias $\mu_{z, \text{Exc}} = +3.5\text{ mm}$ (descending).
  - Short-range Inhibitory: $\sigma_{z, \text{Inh}} = 2.0\text{ mm}$, bias $\mu_{z, \text{Inh}} = -1.0\text{ mm}$ (rostral/local).
  - Commissural Interneurons: $\sigma_{z, \text{Comm}} = 4.0\text{ mm}$, contralateral targeting ($\Phi_{\text{side}} = 1$ when $\text{sgn}(x_i) \ne \text{sgn}(x_j)$).

---

### 3. Row-Wise Zero-Sum E/I Balancing

Initial weights $W_{ij}^{(0)}$ sampled from Bernoulli distributions with Dale's law ($W_{ij} > 0$ for Excitatory, $W_{ij} < 0$ for Inhibitory) are scaled to achieve exact row-wise zero-sum balance:
$$\sum_{j \in \text{Presyn}} W_{ij} = 0 \quad \forall i \in \{1, \dots, N\}$$
Implemented via:
$$W_{ij} = W_{ij}^{(0)} \cdot \left( \frac{\sum_{k \in \text{Exc}} W_{ik}^{(0)}}{\sum_{k \in \text{Inh}} |W_{ik}^{(0)}|} \right) \quad \text{for } j \in \text{Inh}$$
followed by spectral radius normalization:
$$W = \frac{g_{\text{spec}}}{\rho(W)} W$$
with $g_{\text{spec}} = 1.25$ ensuring self-sustaining rotational limit cycle dynamics.

---

### 4. Recurrent Rate Dynamics & Compound Hyperbolic Tangent

The network rate vector $\mathbf{R}(t) = [R_1(t), \dots, R_N(t)]^T$ is integrated via Forward Euler:
$$R_i(t + \Delta t) = R_i(t) + \frac{\Delta t}{\tau} \left( -R_i(t) + f\left( \sum_{j=1}^N W_{ij} R_j(t) + I_i^{\text{tonic}} + I_i^{\text{ext}}(t) + \eta_i(t) \right) \right)$$
where:
- $\tau = 20.0\text{ ms}$, $\Delta t = 1.0\text{ ms}$.
- $I_i^{\text{tonic}} = 15.0\text{ pA}$ (uniform baseline drive).
- $\eta_i(t) \sim \mathcal{N}(0, \sigma_{\eta}^2)$ with $\sigma_{\eta} = 0.5\text{ pA}$.
- Compound activation function:
  $$f(I) = f_{\max} \tanh\left( \frac{\max(0, I - T)}{f_{\max}} \right)$$
  with $f_{\max} = 100.0\text{ Hz}$, threshold $T = 0.0\text{ pA}$.

---

### 5. Functional Phase Unfolding & Limit Cycle Analysis

1. **Principal Component Analysis (PCA)**:
   The zero-mean rate matrix $\tilde{R} = R - \bar{R}$ is decomposed via SVD. The planar variance captured by PC1 and PC2 is:
   $$\text{Var}_{\text{planar}} = \frac{\lambda_1 + \lambda_2}{\sum_k \lambda_k}$$
2. **Circular Phase Sorting**:
   For each neuron $i$, cross-correlation with $\text{PC1}(t)$ determines peak lag $\tau_i$:
   $$\tau_i = \arg\max_\tau \int \text{PC1}(t) R_i(t + \tau) dt$$
   Phase angle $\theta_i = (\tau_i / T_{\text{cycle}}) \cdot 2\pi \pmod{2\pi}$.

---

### 6. Emergent Net Projectome & Mexican-Hat Metrics

Sorting synaptic matrix $W$ by phase $\theta_i$ or physical coordinate $z_i$ reveals the net spatial interaction profile:
$$\Pi(\Delta Z) = \frac{1}{N_{\Delta Z}} \sum_{|z_i - z_j - \Delta Z| \le \delta z} W_{ij}$$
Key quantitative metrics:
- **Peak Local Excitation**: $\Pi_{\max} = \max_{\Delta Z} \Pi(\Delta Z)$ at $|\Delta Z| \approx 0$.
- **Surround Inhibition Trough**: $\Pi_{\min} = \min_{\Delta Z} \Pi(\Delta Z)$ at $|\Delta Z| \in [2.0, 8.0]\text{ mm}$.
- **Mexican-Hat Index**:
  $$\text{MHI} = \frac{\Pi_{\max} - \Pi_{\min}}{\Pi_{\max} + |\Pi_{\min}|}$$

---

### 7. Decoupled Gain Modulation

To test whether cat spinal circuits support orthogonal control of stride frequency vs. burst amplitude:
- **Excitatory Gain Sweep ($g_{\text{exc}} \in [0.8, 1.5]$)**: Multiplies weights of long-range excitatory interneurons ($W_{\text{exc}} \leftarrow g_{\text{exc}} W_{\text{exc}}$).
- **Inhibitory Gain Sweep ($g_{\text{inh}} \in [0.8, 1.5]$)**: Multiplies weights of inhibitory interneurons ($W_{\text{inh}} \leftarrow g_{\text{inh}} W_{\text{inh}}$).
- Metrics: Oscillation frequency $f = 1/T_{\text{cycle}}$ and PCA orbit radius $R_{\text{orbit}} = \langle \sqrt{\text{PC1}(t)^2 + \text{PC2}(t)^2} \rangle$.
