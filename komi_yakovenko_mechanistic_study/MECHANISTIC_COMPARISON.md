# Mechanistic Comparison Report
## Detailed Quantitative Comparison Between Model Y and Model K-Y

---

### 1. Multi-Seed Monte Carlo Quantitative Benchmarking

Results across $N=5$ independent random seeds ($n=5$ runs):

| Metric | Model Y Reference (Yakovenko 2002) | Model K-Y Simulation (Komi Framework on Cat) | Mean ± SD ($n=5$) | Min | Max |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Trajectory Correlation ($r$)** | $1.000$ (Self) | Emergent Recurrent Drive | **$0.664 \pm 0.183$** | $0.406$ | $0.836$ |
| **Trajectory RMSE (Levels)** | $0.00\text{ levels}$ | Emergent Recurrent Drive | **$14.62 \pm 0.20\text{ levels}$** | $14.33$ | $14.80$ |
| **Normalized RMSE (NRMSE)** | $0.000$ | Emergent Recurrent Drive | **$0.370 \pm 0.005$** | $0.363$ | $0.375$ |
| **Phase Alignment Lag** | $0\%$ (Prescribed) | Unforced Limit Cycle | **$18.6\% \pm 17.1\%$** | $4.0\%$ | $43.0\%$ |
| **Emergent Wave Velocity ($v_{\text{wave}}$)** | $414.5\text{ mm/s}$ (Peak Migration) | Recurrent Traveling Wave | **$130.2 \pm 100.1\text{ mm/s}$** | $41.5\text{ mm/s}$ | $249.9\text{ mm/s}$ |
| **Mexican-Hat Index ($\text{MHI}$)** | $0.00$ (No Connectome) | Anisotropic Projection Matrix | **$1.000 \pm 0.000$** | $1.000$ | $1.000$ |
| **Projectome Asymmetry (Caudal Skew)** | $0.00$ (No Connectome) | Asymmetric Descending Biases | **$1.000 \pm 0.000$** | $1.000$ | $1.000$ |
| **PCA Planar Variance Explained** | $100\%$ (Prescribed) | SVD on $(N \times T)$ Rate Matrix | **$68.0\% \pm 22.1\%$** | $34.6\%$ | $96.4\%$ |
| **Dominant Locomotor Frequency ($f$)** | $1.43\text{ Hz}$ (Fixed $700\text{ ms}$) | Unforced Spontaneous Rhythm | **$1.36 \pm 0.75\text{ Hz}$** | $0.69\text{ Hz}$ | $2.58\text{ Hz}$ |
| **Bilateral Phase Difference ($\Delta\Phi$)** | $180.0^\circ$ (Fixed Alternation) | Commissural Interneuron Coupling | **$134.7^\circ \pm 55.7^\circ$** | $36.2^\circ$ | $168.4^\circ$ |

---

### 2. Dissection of the Three Wave Phenomena

1. **Wave A (Center-of-Activity Migration $r_{\text{cm}}(t)$)**:
   - *Model Y*: Displacement $= 11.37\text{ mm}$ ($39.5\text{ levels}$), peak migration velocity $= 414.5\text{ mm/s}$, mean velocity $= 31.0\text{ mm/s}$.
   - *Model K-Y*: Displacement $= 10.82\text{ mm}$ ($37.6\text{ levels}$), peak migration velocity $= 385.2\text{ mm/s}$.
2. **Wave B (Stance-to-Swing Shift)**:
   - *Model Y*: $76\%$ of cycle spent in caudal cord ($L_7-S_1$), jumping $36.7\text{ levels}$ at lift-off.
   - *Model K-Y*: Spontaneous accumulation of firing in caudal $L_7$ retractor/extensor populations followed by rapid rostral recruitment.
3. **Wave C (Emergent Continuous Neurogenic Traveling Wave)**:
   - *Model K-Y Only*: A genuine neurogenic phase wave propagating along $L_4 \to S_1$ at $v_{\text{wave}} \approx 130.2\text{ mm/s}$ with $\text{MHI} = 1.00$.

---

### 3. Key Findings from the 8 Controlled Experiments

1. **Spatial Structure is Mandatory**: Removing spatial organization (Control 1: $\text{MHI} \to 0$) or shuffling coordinates (Control 2: $\text{MHI} \to 0$) completely destroys the projectome and traveling wave.
2. **E/I Balancing is Mandatory**: Without row-wise zero-sum balancing (Control 5), rotational limit cycles fail to stabilize and bilateral coordination collapses ($\text{Alternation Index} = 0.08$).
3. **Directional Asymmetry Drives Unidirectional Waves**: Removing descending projection bias (Control 4: $\mu_z = 0$) slows wave velocity and disrupts unilateral rostrocaudal propagation.
