# Neural Dynamics and Simulation Specification

This document details the mathematical formulation, differential rate equations, numerical integration schemes, activation functions, and parameters of the spinal cord neural projectome simulation, faithfully reproducing **Komi et al., Nature Communications, 2026** and the original MATLAB implementation in `00_SpinalNetworkModel/@Network/Simulate.m`.

---

## 1. Mathematical Formulation of Neural Dynamics

The network dynamics simulate the temporal evolution of membrane potentials $\mathbf{V}(t) = [V_1(t), \dots, V_N(t)]^T$ and firing rates $\mathbf{R}(t) = [R_1(t), \dots, R_N(t)]^T$ for $N$ interconnected neurons across discrete time steps $t \in \{1, 2, \dots, T\}$.

### A. Total Input Current
For each postsynaptic neuron $i$ at time step $t-1$, the total incoming current $I_{\text{tot}, i}(t-1)$ comprises three components:
$$I_{\text{tot}, i}(t-1) = I_{\text{rec}, i}(t-1) + I_{\text{noise}, i}(t-1) + I_{e, i}(t-1)$$

1. **Recurrent Synaptic Current $\mathbf{I}_{\text{rec}}$**:
   $$I_{\text{rec}, i}(t-1) = \sum_{j=1}^N W_{ij} R_j(t-1) \iff \mathbf{I}_{\text{rec}}(t-1) = W \mathbf{R}(t-1)$$
   where $W \in \mathbb{R}^{N \times N}$ is the synaptic connectivity matrix (constructed in Step 2).
2. **External Tonic Drive $\mathbf{I}_e$**:
   A constant tonic current representing descending reticulospinal drive and neurochemical excitation (default: $I_{e, i} = 25\text{--}30$).
3. **Additive Gaussian Noise $\mathbf{I}_{\text{noise}}$**:
   $$I_{\text{noise}, i}(t-1) \sim \mathcal{N}(0, \sigma_{\text{noise}}^2)$$
   where $\sigma_{\text{noise}} = 0.5$ (configurable).

*Source Code Reference*: `@Network/Simulate.m`, Lines 60–61.

---

### B. Membrane Potential Differential Equation
The membrane potential $V_i(t)$ obeys a leaky integrator differential equation:
$$\tau_{V, i} \frac{dV_i}{dt} = -V_i(t) + I_{\text{tot}, i}(t)$$

Using the Forward Euler numerical integration scheme with step size $\Delta t = 1.0\ \text{ms}$:
$$dV_i(t-1) = \frac{-V_i(t-1) + I_{\text{tot}, i}(t-1)}{\tau_{V, i}}$$
$$V_i(t) = V_i(t-1) + dV_i(t-1)$$

where $\tau_{V, i} = 50\ \text{ms}$ is the membrane time constant for all neurons.

*Source Code Reference*: `@Network/Simulate.m`, Lines 62–63.

---

### C. Spike-Frequency Adaptation (Optional, $Ad = 0$ or $1$)
When spike-frequency adaptation is enabled ($Ad = 1$):
$$\tau_{a, i} \frac{da_i}{dt} = C_a R_i(t-1) - a_i(t-1)$$
$$a_i(t) = a_i(t-1) + \frac{C_a R_i(t-1) - a_i(t-1)}{\tau_{a, i}}$$
where:
- $C_a = 1.25$
- $\tau_{a, i} = 3,000\ \text{ms}$ for adapting neurons (expressing $Kcnn$), and $10,000\ \text{ms}$ for non-adapting neurons.
In the baseline simulation (`InstantiateModel.m`), adaptation is disabled ($Ad = 0 \implies a_i(t) = 0$).

*Source Code Reference*: `@Network/Simulate.m`, Lines 64–67.

---

### D. Piecewise Hyperbolic Tangent Firing Rate Activation Function
The firing rate $R_i(t)$ is computed from the effective membrane potential $V_i(t) - a_i(t)$ via the piecewise hyperbolic tangent activation function (`tanh_f_V`):

$$\Delta V_i = V_i(t) - a_i(t) - \theta_i$$

$$f_i = \begin{cases} \theta_i \cdot \tanh\left(\frac{g_i \cdot \Delta V_i}{\theta_i}\right), & \text{if } \Delta V_i \le 0 \\ f_{\max, i} \cdot \tanh\left(\frac{g_i \cdot \Delta V_i}{f_{\max, i}}\right), & \text{if } \Delta V_i > 0 \end{cases}$$

$$R_i(t) = f_i + \theta_i$$

#### Mathematical Properties:
1. **At Threshold ($V_i - a_i = \theta_i$)**:
   $$\Delta V_i = 0 \implies f_i = 0 \implies R_i(t) = \theta_i$$
2. **Deep Hyperpolarization ($V_i \to -\infty$)**:
   $$\tanh \to -1 \implies f_i \to -\theta_i \implies R_i(t) \to 0 \quad (\text{firing rate is non-negative } R_i \ge 0)$$
3. **Strong Depolarization ($V_i \to +\infty$)**:
   $$\tanh \to +1 \implies f_i \to f_{\max, i} \implies R_i(t) \to \theta_i + f_{\max, i}$$
4. **Continuity**:
   The function and its first derivative $\frac{dR}{dV} = g_i$ are continuous across the threshold $\Delta V_i = 0$.

*Source Code Reference*: `@Network/Simulate.m`, Lines 68, 77–84.

---

## 2. Simulation Parameters and Initial Conditions

| Parameter | Symbol | Default Value | Units | Description | MATLAB Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Simulation duration | $T$ | $10,000$ | steps ($\text{ms}$) | Total simulation time steps | `InstantiateModel.m:31` |
| Time step | $\Delta t$ | $1.0$ | $\text{ms}$ | Numerical integration time step | `@Network/Simulate.m:59` |
| Membrane time constant | $\tau_V$ | $50.0$ | $\text{ms}$ | Leaky integrator decay constant | `@Network/Simulate.m:5` |
| Tonic external drive | $I_e$ | $30.0$ | a.u. | Uniform excitatory drive current | `InstantiateModel.m:33` |
| Noise amplitude | $\sigma_{\text{noise}}$ | $0.5$ | a.u. | Gaussian noise standard deviation | `@Network/Simulate.m:10` |
| Initial voltage mean | $V_{\text{init}}$ | $-70.0$ | $\text{mV}$ | Mean resting potential | `@Network/Simulate.m:13` |
| Initial voltage variance | $\sigma_{V_{\text{init}}}$ | $3.0$ | $\text{mV}$ | Normal distribution standard deviation | `@Network/Simulate.m:50` |
| Initial firing rates | $R_0$ | $0.0$ | $\text{Hz}$ | Initial rate at $t = 1$ | `@Network/Simulate.m:51` |
| Cell firing threshold | $\theta$ | $5.0$ | $\text{mV}$ | Threshold potential parameter | `NetworkParameters.m:33` |
| Cell gain | $g$ | $1.0$ | $\text{mV}^{-1}$ | Activation curve slope parameter | `NetworkParameters.m:31` |
| Maximum firing rate | $f_{\max}$ | $50.0$ | $\text{Hz}$ | Saturation firing rate parameter | `NetworkParameters.m:32` |
| Random seed | `seed` | $5$ | integer | RNG seed for noise and initial states | `@Network/Simulate.m:11` |

---

## 3. Algorithm: State Update Loop

```
1. Initialize RNG with seed
2. Initialize V(:, 1) ~ N(-70, 3^2)
3. Initialize R(1, :) = 0
4. Generate pre-allocated I_noise ~ N(0, sigma_noise^2)
5. For t = 2 to T:
     a. I_rec = W * R(t-1, :)'
     b. I_tot = I_rec + I_noise(:, t-1) + I_e(:, t-1)
     c. dV = (-V(:, t-1) + I_tot) / tau_V
     d. V(:, t) = V(:, t-1) + dV
     e. If Adaptation:
          da = (Ca * R(t-1, :)' - a(:, t-1)) / tau_a
          a(:, t) = a(:, t-1) + da
     f. R(t, :) = tanh_f_V(V(:, t) - a(:, t), threshold, gain, fmax)
6. Return Rates R and Voltage V
```
