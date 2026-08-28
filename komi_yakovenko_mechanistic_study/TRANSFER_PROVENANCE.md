# Scientific Provenance Trace
## Provenance of Parameters, Coordinates, and Equations in the Mechanistic Study

---

### 1. Provenance Categories
Every parameter and equation is assigned one of the five mandatory provenance classes:
1. `[YAK-DATA]`: Directly extracted from Yakovenko et al. (2002) anatomical or EMG data.
2. `[KOMI-METHOD]`: Computational equation, algorithm, or parameter transferred from Komi et al. (2026).
3. `[DERIVED]`: Emergent result produced by executing Model K-Y.
4. `[ASSUMPTION]`: Explicit modeling assumption introduced to bridge data gaps.
5. `[CONTROL]`: Benchmark control condition.

---

### 2. Parameter-by-Parameter Provenance Trace

| Parameter / Feature | Value | Provenance Class | Original Source & Grounding |
| :--- | :---: | :---: | :--- |
| **Spinal Length ($L_{\text{cord}}$)** | $28.8\text{ mm}$ ($30 \times 0.96\text{ mm}$) | `[YAK-DATA]` | Yakovenko et al. (2002), Table 1 & Anatomical Methods |
| **Hemicord Width ($w_{\text{cord}}$)** | $3.6\text{ mm}$ | `[YAK-DATA]` | Yakovenko et al. (2002), Anatomical Methods |
| **Dorsoventral Height ($h_{\text{cord}}$)** | $5.5\text{ mm}$ | `[YAK-DATA]` | Yakovenko et al. (2002), Anatomical Methods |
| **Total Motoneuron Count** | 4,034 motoneurons | `[YAK-DATA]` | VanderHorst & Holstege (1997), Yakovenko Table 1 |
| **Rostrocaudal Motoneuron Density** | 33% rostral / 67% caudal | `[YAK-DATA]` | Yakovenko et al. (2002), Table 1 |
| **27 Muscle Slices ($N_{m,s}$)** | 27 distinct 30-slice vectors | `[YAK-DATA]` | VanderHorst & Holstege (1997) Fig 28 |
| **Piecewise-Linear EMG Profiles** | 27 normalized waveforms | `[YAK-DATA]` | 26 In Vivo Literature EMG Studies cited in Yakovenko |
| **Ventral Horn Coordinate Range** | $Y \in [1.2, 4.2]\text{ mm}$ | `[ASSUMPTION]` | Ventral horn lamina VII–IX bounds in mammalian cord |
| **Commissural Fraction & E/I Ratio** | 15% of network, 60:40 E/I | `[ASSUMPTION]` | Mammalian spinal V0v/V0d commissural literature |
| **Leaky Time Constant ($\tau$)** | $20.0\text{ ms}$ | `[KOMI-METHOD]` | Komi et al. (2026), @Dynamics/Simulate.m |
| **Integration Step ($\Delta t$)** | $1.0\text{ ms}$ | `[KOMI-METHOD]` | Komi et al. (2026), @Dynamics/Simulate.m |
| **Tonic Somatic Drive ($I^{\text{tonic}}$)** | $15.0\text{ pA}$ | `[KOMI-METHOD]` | Komi et al. (2026), @Dynamics/Simulate.m |
| **Noise Std ($\sigma_\eta$)** | $0.5\text{ pA}$ | `[KOMI-METHOD]` | Komi et al. (2026), @Dynamics/Simulate.m |
| **Activation Non-Linearity ($f(I)$)** | $f_{\max} \tanh(\max(0, I-T)/f_{\max})$ | `[KOMI-METHOD]` | Komi et al. (2026), Compound Tanh |
| **Row-Wise E/I Balancing Rule** | $\sum W_{ij} = 0.0 \pm 10^{-15}$ | `[KOMI-METHOD]` | BergLab BalanceConnectivity.m |
| **Spectral Radius Scaling ($\rho$)** | $1.25$ | `[KOMI-METHOD]` | BergLab RescaleConnectivity.m |
| **Long-Range Excitatory Kernel** | $\sigma_z = 6.0\text{ mm}, \mu_z = +3.5\text{ mm}$ | `[KOMI-METHOD]` | Anisotropic descending projection kernel |
| **Local Inhibitory Kernel** | $\sigma_z = 2.5\text{ mm}, \mu_z = -1.2\text{ mm}$ | `[KOMI-METHOD]` | Local / rostral recurrent inhibition kernel |
| **Phase Unfolding Method** | Cross-correlation lag with PC1 | `[KOMI-METHOD]` | Komi et al. (2026) Figure 3 Analysis |
| **1D Projectome Convolution** | $\Pi(\Delta Z) = \langle W_{ij} \rangle_{\Delta Z}$ | `[KOMI-METHOD]` | Komi et al. (2026) Figure 4 Analysis |
