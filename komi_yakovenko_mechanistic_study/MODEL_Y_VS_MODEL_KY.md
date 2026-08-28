# Mathematical & Conceptual Comparison: Model Y vs. Model K-Y

## Direct Comparison of the Two Computational Models

---

### 1. Model Y (Yakovenko Feedforward Kinematic Reconstruction)

Model Y is a **static, algebraic, feedforward mapping** that reconstructs slice-wise motoneuron activity $A_Y(s, t)$ by scaling anatomical motoneuron pool counts by empirical literature EMG waveforms:

$$A_Y(s, t) = \sum_{m=1}^{27} N_{m,s} \cdot \left( \frac{\text{EMG}_m(t)}{100} \right) \cdot \gamma_m$$

where:
- $s \in \{1, \dots, 30\}$: Transverse spinal slice index ($L_4 \to S_1$, $0.96\text{ mm/slice}$).
- $t \in [0, 100\%]$: Normalized step cycle time ($30\%$ swing / $70\%$ stance).
- $N_{m,s}$: Number of motoneurons for muscle $m$ located in slice $s$ (VanderHorst & Holstege 1997).
- $\text{EMG}_m(t)$: Standardized piecewise-linear EMG profile for muscle $m$ ($0 - 100\%$).
- $\gamma_m$: Recruitment ceiling parameter ($\gamma_m = 1.0$ for $100\%$ graded, or $\gamma_{\text{ext}} = 0.40, \gamma_{\text{flex}} = 0.15$ for physiological walking).

#### Center-of-Activity Trajectory in Model Y:
$$r_{\text{cm}, Y}(t) = \frac{\sum_{s=1}^{30} s \cdot A_Y(s, t)}{\sum_{s=1}^{30} A_Y(s, t)}$$

---

### 2. Model K-Y (Komi-Style Recurrent Spatial Projectome on Cat Anatomy)

Model K-Y is a **continuous-time, recurrent, generative dynamical system** governed by nonlinear differential equations. It does not receive empirical EMG; instead, it generates motor activity from internal recurrent interactions:

$$\tau \frac{dR_i(t)}{dt} = -R_i(t) + f\left( \sum_{j=1}^N W_{ij} R_j(t) + I_i^{\text{tonic}} + \eta_i(t) \right)$$

where:
- $i, j \in \{1, \dots, N\}$: Premotor interneurons with 3D positions $\mathbf{r}_i = (x_i, y_i, z_i)$ in cat cord geometry ($Z \in [0, 28.8]\text{ mm}$).
- $W_{ij}$: 3D anisotropic synaptic matrix satisfying Dale's law and row-wise zero-sum E/I balance:
  $$\sum_{j=1}^N W_{ij} = 0.0 \pm 10^{-15} \quad (\text{for dual-input neurons})$$
- $\tau = 20.0\text{ ms}$: Leaky integration time constant.
- $I_i^{\text{tonic}} = 15.0\text{ pA}$: Uniform tonic unpatterned drive.
- $\eta_i(t) \sim \mathcal{N}(0, \sigma_{\eta}^2)$: White noise current ($\sigma_\eta = 0.5\text{ pA}$).
- $f(I) = f_{\max} \tanh\left( \frac{\max(0, I - T)}{f_{\max}} \right)$: Compound hyperbolic tangent activation function ($f_{\max} = 100\text{ Hz}, T = 0\text{ pA}$).

#### Emergent Slice Activity & Center-of-Activity in Model K-Y:
$$A_{KY}(s, t) = \frac{1}{|S_s|} \sum_{i \in S_s} R_i(t)$$
$$r_{\text{cm}, KY}(t) = \frac{\sum_{s=1}^{30} s \cdot A_{KY}(s, t)}{\sum_{s=1}^{30} A_{KY}(s, t)}$$

---

### 3. Key Differences in Model Structure

| Attribute | Model Y (Yakovenko 2002) | Model K-Y (Komi-on-Yakovenko) |
| :--- | :--- | :--- |
| **Mathematical Type** | Algebraic Linear Matrix Product | Nonlinear Recurrent Differential Equation |
| **Rhythm Generation** | External (Prescribed from EMG) | Internal (Spontaneous Rotational Limit Cycle) |
| **Wave Genesis** | Prescribed by EMG phase delays | Emergent from Asymmetric Descending Projections |
| **Synaptic Weights ($W$)** | None | Spatially Organized Anisotropic Matrix |
| **E/I Balancing** | None | Exact Row-Wise Zero-Sum Balance ($\sum W_{ij} = 0$) |
| **Predictive Power** | Descriptive only | Can predict lesion effects, gain control, projectome |
