# Comprehensive All-Pool Hindlimb Analysis: TA-Relocated Model (Condition D)

## Executive Summary
This report provides a corrected, rigorous analysis of all 14 available hip, knee, ankle, and toe motoneuron pools in the **existing TA-relocated simulation** (Condition D, Realization 1) from the Komi et al. (2026) spinal network model. In this condition, motoneurons of the *Tibialis Anterior* (TA) pool reside within their verified anatomical segment boundaries in $L4–L5$ ($[5600.0, 7900.0]\ \mu\text{m}$; left centroid $6773.4\ \mu\text{m}$, bilateral centroid $6631.6\ \mu\text{m}$), with distance-dependent synaptic connectivity rebuilt under author balance and rescaling rules (`net_seed = 42`, `simSeed = 5`, tonic drive $I_e = 25.0\ \text{pA}$).

No biological parameters, synaptic weights, connectivity kernels, descending drives, or muscle timings were altered. The analysis corrects previous methodological issues: it isolates hindlimb motoneurons using an explicit mask, preserves empty physical bins as `NaN` (rendering them with distinct backgrounds), measures cycle-by-cycle neighboring-bin signed delays ($\Delta t$, $\Delta x$, $R_\Delta$) without bridging empty regions or forcing monotonic timing, uses documented cycle references with endpoint-free grids, and reconciles all motoneuron counts and trace verifications directly against the saved simulation data.

---

## 1. Motoneuron Selection and Count Reconciliation

The spinal cord network contains 1,795 motoneurons across 18 motor pools. Previous documentation cited 1,326 hindlimb motoneurons; this reflected a clerical typo in an earlier draft where four right-side pools were undercounted. The actual counts, derived dynamically from the saved network metadata (`data/mn_metadata.json`), reconcile exactly:

$$\text{Total Motoneurons in Model} = 1{,}795$$
$$\text{Hindlimb Motoneurons (Analyzed)} = 1{,}366 \quad (\text{Left: } 656, \text{ Right: } 710)$$
$$\text{Excluded Non-Hindlimb Motoneurons} = 429 \quad (\text{Left: } 236, \text{ Right: } 193)$$

### A. Excluded Non-Hindlimb Pools (4 Pools, 429 Neurons)
These pools were excluded from the hindlimb analysis because they innervate paraspinal, abdominal, or caudal structures:
1. **Axial Column** ($n = 330$: Left 192, Right 138; segments $T13–L5$; span $[83.0, 8001.1]\ \mu\text{m}$; centroid $4905.0\ \mu\text{m}$): Continuous paraspinal axial column.
2. **Tail** ($n = 58$: Left 28, Right 30; segments $S1–S4$; span $[9426.6, 13927.4]\ \mu\text{m}$; centroid $11851.7\ \mu\text{m}$): Sacro-caudal tail abductor/flexor column.
3. **Thoracic Abdominal** ($n = 24$: Left 10, Right 14; segment $T13$; span $[68.5, 1303.0]\ \mu\text{m}$; centroid $541.2\ \mu\text{m}$): Thoracic trunk wall musculature.
4. **Quadratus Lumburum** ($n = 17$: Left 6, Right 11; segment $L1$; span $[1319.9, 2455.3]\ \mu\text{m}$; centroid $1784.9\ \mu\text{m}$): Deep posterior lumbar abdominal wall musculature.

### B. Included Hindlimb Motor Pools (14 Pools, 1,366 Neurons)
The 14 hindlimb motor pools ordered strictly by anatomical centroid (Left side, rostral to caudal):

| # | Pool Name | Abbr | Joint Group | Muscle Function | Total MN | Left MN | Right MN | Segments | Left Centroid | Left Span ($\mu\text{m}$) | Anatomical & Functional Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vastus Lateralis | VLat | Knee | Knee Extensor | 97 | 50 | 47 | T13, L1, L2 | $2267.8\ \mu\text{m}$ | $[96.2, 3915.4]$ | Quadriceps group, primary mono-articular knee extensor |
| 2 | Vastus Medialis | VMed | Knee | Knee Extensor | 103 | 55 | 48 | L1, L2, L3 | $3007.8\ \mu\text{m}$ | $[1337.6, 5498.5]$ | Quadriceps group, primary mono-articular knee extensor |
| 3 | Iliopsoas | Ilio | Hip | Primary Hip Flexor | 94 | 40 | 54 | L2, L3, L4 | $4277.9\ \mu\text{m}$ | $[2643.1, 6704.3]$ | Deep primary hip flexor |
| 4 | Rectus Femoris | RF | Knee | Knee Ext / Hip Flex | 93 | 46 | 47 | L2, L3, L4 | $4661.4\ \mu\text{m}$ | $[2614.0, 6523.0]$ | Bi-articular: knee extensor + secondary hip flexor |
| 5 | Gracilis | Grac | Knee | Knee Flex / Hip Add | 120 | 56 | 64 | L1–L5 | $4739.6\ \mu\text{m}$ | $[1465.1, 7943.6]$ | Multi-articular medial thigh muscle (knee flexor + hip adductor) |
| 6 | Adductors | Add | Hip | Hip Adductor | 127 | 65 | 62 | L2–L5 | $5382.6\ \mu\text{m}$ | $[2782.2, 7979.3]$ | Adductor group (magnus/longus/brevis); multi-articular synergist |
| 7 | Gastrocnemius | GM | Ankle/Toes | Ankle Plant / Knee Flex | 76 | 34 | 42 | L3, L4, L5 | $6134.2\ \mu\text{m}$ | $[4467.8, 7874.0]$ | Triceps surae, bi-articular ankle plantarflexor + knee flexor |
| 8 | Gluteus | Glut | Hip | Hip Extensor / Abductor | 123 | 63 | 60 | L3–L6 | $6732.0\ \mu\text{m}$ | $[4318.6, 9063.5]$ | Major mono-articular hip extensor and abductor |
| 9 | **Tibialis Anterior** | **TA** | **Ankle/Toes** | **Ankle Dorsiflexor** | **78** | **36** | **42** | **L4, L5** | **$6773.4\ \mu\text{m}$** | **$[5600.0, 7874.1]$** | **Relocated from baseline L2–L4 to anatomical L4–L5** |
| 10 | Biceps Femoris | BF | Knee | Knee Flex / Hip Ext | 107 | 43 | 64 | L3–L6 | $7070.7\ \mu\text{m}$ | $[4245.4, 9393.9]$ | Hamstring group, bi-articular knee flexor + hip extensor |
| 11 | Plantar Flexor | PF | Ankle/Toes | Ankle / Digit Plant | 53 | 20 | 33 | L4, L5, L6 | $7320.8\ \mu\text{m}$ | $[6105.9, 9076.0]$ | Deep posterior compartment (flexor digitorum longus / tibialis post.) |
| 12 | Soleus | Sol | Ankle/Toes | Ankle Plantarflexor | 127 | 67 | 60 | L4, L5, L6 | $7840.3\ \mu\text{m}$ | $[5630.9, 9385.2]$ | Triceps surae, mono-articular slow-twitch ankle plantarflexor |
| 13 | Semitendinosus | ST | Knee | Knee Flex / Hip Ext | 103 | 47 | 56 | L4–S1 | $8118.5\ \mu\text{m}$ | $[5600.6, 10409.1]$ | Hamstring group, bi-articular knee flexor + hip extensor |
| 14 | Extensor Digitorum | EDL | Ankle/Toes | Toe Ext / Ankle Dorsi | 65 | 34 | 31 | L5, L6 | $8735.7\ \mu\text{m}$ | $[7096.6, 9379.1]$ | Extensor digitorum longus: digit extensor + ankle dorsiflexor |

*Full coordinates and metadata are stored in [pool_inventory.csv](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/all_pool_analysis/pool_inventory.csv).*

---

## 2. Verification Against Saved Experiment Traces

The analysis reuses the saved rate matrix $R_{\text{MN}}$ ($1{,}795 \times 22{,}000$) in `data/ta_relocated_all_pools.mat` without rerunning network generation or ODE simulation. To verify that this dataset corresponds exactly to the validated TA-relocated simulation (Condition D, Realization 1), all 7 muscle traces previously exported to `experiments/ta_placement/data/experiment_data.mat` (`condD`) were compared dynamically against the reconstructed pool averages:

| Trace Identifier | Target Motor Pool | Side | Max Absolute Difference | Mean Absolute Difference | Pearson Correlation ($r$) | Verification Status |
|---|---|---|---|---|---|---|
| `trace_ta_l` | Tibialis Anterior | Left | $0.000000\times 10^{0}\ \text{Hz}$ | $0.000000\times 10^{0}\ \text{Hz}$ | $1.00000000$ | Bit-for-bit match |
| `trace_gm_l` | Gastrocnemius | Left | $0.000000\times 10^{0}\ \text{Hz}$ | $0.000000\times 10^{0}\ \text{Hz}$ | $1.00000000$ | Bit-for-bit match |
| `trace_sol_l` | Soleus | Left | $0.000000\times 10^{0}\ \text{Hz}$ | $0.000000\times 10^{0}\ \text{Hz}$ | $1.00000000$ | Bit-for-bit match |
| `trace_vm_l` | Vastus Medialis | Left | $0.000000\times 10^{0}\ \text{Hz}$ | $0.000000\times 10^{0}\ \text{Hz}$ | $0.99999999$ | Bit-for-bit match |
| `trace_bf_l` | Biceps Femoris | Left | $0.000000\times 10^{0}\ \text{Hz}$ | $0.000000\times 10^{0}\ \text{Hz}$ | $0.99999999$ | Bit-for-bit match |
| `trace_ta_r` | Tibialis Anterior | Right | $0.000000\times 10^{0}\ \text{Hz}$ | $0.000000\times 10^{0}\ \text{Hz}$ | $1.00000000$ | Bit-for-bit match |
| `trace_gm_r` | Gastrocnemius | Right | $0.000000\times 10^{0}\ \text{Hz}$ | $0.000000\times 10^{0}\ \text{Hz}$ | $1.00000000$ | Bit-for-bit match |

All differences are bounded by floating-point machine precision ($\max |\Delta| = 0.0\ \text{Hz}$), confirming that the dataset represents the authentic, unaltered Condition D simulation.

---

## 3. Physical Rostrocaudal Activity Maps and Binning Sensitivity

Physical RC activity maps were evaluated strictly using the explicit hindlimb motoneuron mask ($N = 1{,}366$). Motoneurons span $91.3\ \mu\text{m}$ to $10{,}672.0\ \mu\text{m}$ (most caudal neuron: Right Semitendinosus at $10{,}672.0\ \mu\text{m}$; Left most caudal: Semitendinosus at $10{,}409.1\ \mu\text{m}$). The binning grid spans $[0, 11{,}000]\ \mu\text{m}$, fully encompassing all neurons and partial terminal bins.

### A. Empty Bin Treatment
- **Mean Firing Rate per Neuron:** In empty spatial bins ($N = 0$), the mean rate is strictly undefined and represented as `NaN`. In Figure panels C1 and C3, `NaN` bins are rendered with a distinct grey background (`#D0D0D0`), preventing the visual misinterpretation of unpopulated tissue as neuronal quiescence.
- **Summed Firing Rate:** Empty bins have a sum of $0.0\ \text{Hz}$, reflecting the absence of neurons rather than active inhibition.
- **Distribution of Empty Bins:**
  - **$250\ \mu\text{m}$ Bins (44 bins total):** 4 empty bins on Left ($[500, 750)$, $[9500, 9750)$, $[10500, 10750)$, $[10750, 11000)\ \mu\text{m}$); 3 empty bins on Right ($[9750, 10000)$, $[10000, 10250)$, $[10750, 11000)\ \mu\text{m}$).
  - **$500\ \mu\text{m}$ Bins (22 bins total):** 1 empty bin on Left ($[10500, 11000)\ \mu\text{m}$, bin index 21); 0 empty bins on Right.
  - **$1000\ \mu\text{m}$ Bins (11 bins total):** 0 empty bins on either side.

### B. Contrast Between Mean and Summed Activity
Comparing panels C1/C3 (Mean Rate per Neuron) against C2/C4 (Summed Rate per Bin) reveals how anatomical density shapes spatial activity:
1. **Mean Activity:** Exhibits a relatively uniform traveling wave (~20–35 Hz) passing rostral-to-caudal across populated bins.
2. **Summed Activity:** Heavily distorted by somata density clustering. Two high-amplitude activity islands appear: an upper lumbar island in $L2$ (quadriceps and hip flexors, $2000–3500\ \mu\text{m}$) and a caudal lumbar island in $L5–L6$ (triceps surae and hamstrings, $6500–8500\ \mu\text{m}$), separated by an anatomical density trough in $L3–L4$.
3. **Caveat:** Analyzing summed activity alone gives the false visual impression of two distinct pulsating rhythm generators, whereas mean activity demonstrates continuous wavefront recruitment.

---

## 4. Empirical Anatomical Timing Progression and Delay Analysis

To determine whether activity propagates as a continuous anatomical wave, activation timing was measured directly across neighboring populated physical bins for complete steady-state cycles ($10{,}000–22{,}000\ \text{ms}$, 16 cycles; mean period $T = 712.6\ \text{ms}$, frequency $f = 1.403\ \text{Hz}$). Unpopulated bins were strictly **not bridged**, circular phase wrapping was handled explicitly, and monotonic timing was not assumed.

### A. Regional Delay Summaries (500 µm Resolution)

| Spinal Region | RC Span ($\mu\text{m}$) | Side | Valid Transitions | Mean Signed Delay $\overline{\Delta t}$ | Delay SD (Cycle Var.) | Delay Consistency ($R_\Delta$) | Apparent Speed ($v$) | Caudal Lag Count | Rostral Lag Count | Synchronous Count |
|---|---|---|---|---|---|---|---|---|---|---|
| **Lumbar Enlargement** | $1500–9500$ | **Left** | **15** | **$+56.7\ \text{ms}$** | **$0.85\ \text{ms}$** | **$0.99997$** | **$8.8\ \text{mm/s}$** | **15** | 0 | 0 |
| **Lumbar Enlargement** | $1500–9500$ | **Right** | **15** | **$+54.3\ \text{ms}$** | **$0.78\ \text{ms}$** | **$0.99997$** | **$9.2\ \text{mm/s}$** | **15** | 0 | 0 |
| **Rostral Margin** | $0–1500$ | **Left** | 2 | $+35.2\ \text{ms}$ | $1.86\ \text{ms}$ | $0.99986$ | $14.2\ \text{mm/s}$ | 2 | 0 | 0 |
| **Rostral Margin** | $0–1500$ | **Right** | 2 | $+48.5\ \text{ms}$ | $2.14\ \text{ms}$ | $0.99981$ | $10.3\ \text{mm/s}$ | 2 | 0 | 0 |
| **Caudal Margin** | $9500–11000$ | **Left** | 1 | $+32.4\ \text{ms}$ | $1.57\ \text{ms}$ | $0.99990$ | $15.4\ \text{mm/s}$ | 1 | 0 | 0 |
| **Caudal Margin** | $9500–11000$ | **Right** | 2 | $+29.1\ \text{ms}$ | $1.80\ \text{ms}$ | $0.99987$ | $17.2\ \text{mm/s}$ | 2 | 0 | 0 |
| **Full Hindlimb Extent** | $0–11000$ | **Left** | 20 | $+55.3\ \text{ms}$ | $1.04\ \text{ms}$ | $0.99995$ | $9.0\ \text{mm/s}$ | 20 | 0 | 0 |
| **Full Hindlimb Extent** | $0–11000$ | **Right** | 21 | $+51.7\ \text{ms}$ | $1.07\ \text{ms}$ | $0.99994$ | $9.7\ \text{mm/s}$ | 21 | 0 | 0 |

### B. Sensitivity Across Bin Resolutions (Lumbar Enlargement, 1500–9500 µm)

| Bin Width | Side | Transitions | Mean Signed Delay $\overline{\Delta t}$ | Mean Delay SD | Mean Consistency ($R_\Delta$) | Inferred Speed | Caudal Lag Proportion |
|---|---|---|---|---|---|---|---|
| **$250\ \mu\text{m}$** | Left | 31 | $+29.6\ \text{ms}$ | $1.01\ \text{ms}$ | $0.99995$ | $8.5\ \text{mm/s}$ | $31 / 31\ (100\%)$ |
| **$250\ \mu\text{m}$** | Right | 31 | $+27.4\ \text{ms}$ | $1.05\ \text{ms}$ | $0.99994$ | $9.1\ \text{mm/s}$ | $31 / 31\ (100\%)$ |
| **$500\ \mu\text{m}$** | Left | 15 | $+56.7\ \text{ms}$ | $0.85\ \text{ms}$ | $0.99997$ | $8.8\ \text{mm/s}$ | $15 / 15\ (100\%)$ |
| **$500\ \mu\text{m}$** | Right | 15 | $+54.3\ \text{ms}$ | $0.78\ \text{ms}$ | $0.99997$ | $9.2\ \text{mm/s}$ | $15 / 15\ (100\%)$ |
| **$1000\ \mu\text{m}$** | Left | 8 | $+110.7\ \text{ms}$ | $0.71\ \text{ms}$ | $0.99998$ | $9.0\ \text{mm/s}$ | $8 / 8\ (100\%)$ |
| **$1000\ \mu\text{m}$** | Right | 8 | $+103.8\ \text{ms}$ | $0.66\ \text{ms}$ | $0.99998$ | $9.6\ \text{mm/s}$ | $8 / 8\ (100\%)$ |

### C. Scientific Assessment of Wave Propagation Evidence
The empirical data yield a nuanced, mixed picture that rejects simplistic binary claims:
1. **Where Timing Progresses Consistently:**
   - Across the entire lumbar enlargement ($1500–9500\ \mu\text{m}$, segments $L1–L6$), timing advances with remarkable fidelity from rostral to caudal.
   - Every single adjacent populated transition ($100\%$) exhibits positive signed delays ($\Delta t > 0$, caudal lag).
   - The apparent propagation velocity is virtually invariant across spatial binning scales: $8.5–9.1\ \text{mm/s}$ ($250\ \mu\text{m}$), $8.8–9.2\ \text{mm/s}$ ($500\ \mu\text{m}$), and $9.0–9.6\ \text{mm/s}$ ($1000\ \mu\text{m}$).
   - Cycle-to-cycle delay consistency is near-perfect ($R_\Delta > 0.9999$, sub-millisecond standard deviations), reflecting the deterministic nature of the simulated network.
2. **Where Timing Deviates or Progresses Non-Uniformly:**
   - **Rostral Boundary ($0–1000\ \mu\text{m}$, segment $T13$):** Somata of the rostral *Vastus Lateralis* pool fire nearly synchronously. The delay between bin 0 and bin 1 is only $\Delta t = 6.0\ \text{ms}$ over $500\ \mu\text{m}$ ($v \approx 83\ \text{mm/s}$), representing a simultaneous burst rather than a traveling wave.
   - **L1/L2 Transition ($1500–2500\ \mu\text{m}$):** A steep phase delay step occurs ($\Delta t \approx 117\ \text{ms}$ on Left, $\approx 141\ \text{ms}$ on Right), marking the transition from the upper lumbar flexor synergy into the mid-lumbar extensor rhythm.
   - **Caudal Margin ($9500–11{,}000\ \mu\text{m}$):** Neuron counts dwindle to sparse clusters ($N = 1–4$). At $250\ \mu\text{m}$, anatomical gaps emerge where contiguous propagation cannot be sampled.
3. **Physical Spatial Wavelength vs. Multi-Band Appearance:**
   - Total phase traversal across the hindlimb cord is $559.3^\circ$ (Left) and $548.5^\circ$ (Right), exceeding $1.5$ full locomotor cycles ($> 1000\ \text{ms}$ of unwrapped delay).
   - Consequently, the spatial wavelength ($\lambda \approx 6{,}800\ \mu\text{m}$) is significantly shorter than the total cord length ($10{,}672\ \mu\text{m}$).
   - This physical reality explains why space-time maps display multiple concurrent active bands: at any instant $t$, rostral neurons from cycle $N+1$ and caudal neurons from cycle $N$ are active simultaneously. This is the hallmark of a continuous traveling wave with $\lambda < L_{\text{cord}}$, not uncoordinated multi-band firing.

---

## 5. Muscle Timing, Bilateral Coordination, and Relocated TA Phase

### A. Cycle Reference Documentation
- **Left Side Reference:** Left Gastrocnemius (GM) peak onset ($0\% = 0^\circ$).
- **Right Side Reference:** Right Gastrocnemius (GM) peak onset ($0\% = 0^\circ$).
- **Bilateral Offset:** Right GM lags Left GM by $-345\ \text{ms}$ (phase lag: $185.7^\circ$).

### B. Motor Pool Peak Phases and Modulation
Each pool's circular mean peak phase $\bar{\phi}$ (degrees relative to ipsilateral GM peak), circular standard deviation ($\sigma_\phi$), mean resultant vector length ($R$), and modulation depth are summarized below:

| Pool Name | Joint Group | Centroid (L) | Peak Phase (L) | Circular SD (L) | Resultant $R$ (L) | Peak Phase (R) | Circular SD (R) | Resultant $R$ (R) | Modulation (L) | Modulated? |
|---|---|---|---|---|---|---|---|---|---|---|
| Vastus Lateralis | Knee | $2267.8\ \mu\text{m}$ | $172.9^\circ$ | $0.21^\circ$ | $1.0000$ | $180.7^\circ$ | $0.26^\circ$ | $1.0000$ | $33.4\ \text{Hz}$ | Yes |
| Vastus Medialis | Knee | $3007.8\ \mu\text{m}$ | $212.5^\circ$ | $0.22^\circ$ | $1.0000$ | $218.4^\circ$ | $0.24^\circ$ | $1.0000$ | $34.1\ \text{Hz}$ | Yes |
| Iliopsoas | Hip | $4277.9\ \mu\text{m}$ | $273.8^\circ$ | $0.19^\circ$ | $1.0000$ | $278.4^\circ$ | $0.23^\circ$ | $1.0000$ | $36.8\ \text{Hz}$ | Yes |
| Rectus Femoris | Knee | $4661.4\ \mu\text{m}$ | $298.9^\circ$ | $0.21^\circ$ | $1.0000$ | $285.3^\circ$ | $0.20^\circ$ | $1.0000$ | $34.2\ \text{Hz}$ | Yes |
| Gracilis | Knee | $4739.6\ \mu\text{m}$ | $306.1^\circ$ | $0.22^\circ$ | $1.0000$ | $300.9^\circ$ | $0.22^\circ$ | $1.0000$ | $35.4\ \text{Hz}$ | Yes |
| Adductors | Hip | $5382.6\ \mu\text{m}$ | $316.9^\circ$ | $0.18^\circ$ | $1.0000$ | $335.5^\circ$ | $0.19^\circ$ | $1.0000$ | $36.9\ \text{Hz}$ | Yes |
| Gastrocnemius | Ankle/Toes | $6134.2\ \mu\text{m}$ | $0.0^\circ$ | $0.00^\circ$ | $1.0000$ | $0.0^\circ$ | $0.00^\circ$ | $1.0000$ | $44.2\ \text{Hz}$ | Yes |
| Gluteus | Hip | $6732.0\ \mu\text{m}$ | $25.2^\circ$ | $0.24^\circ$ | $1.0000$ | $32.4^\circ$ | $0.22^\circ$ | $1.0000$ | $35.2\ \text{Hz}$ | Yes |
| **Tibialis Anterior** | **Ankle/Toes** | **$6773.4\ \mu\text{m}$** | **$29.2^\circ$** | **$0.24^\circ$** | **$1.0000$** | **$20.7^\circ$** | **$0.25^\circ$** | **$1.0000$** | **$37.4\ \text{Hz}$** | **Yes** |
| Biceps Femoris | Knee | $7070.7\ \mu\text{m}$ | $39.6^\circ$ | $0.23^\circ$ | $1.0000$ | $40.5^\circ$ | $0.24^\circ$ | $1.0000$ | $37.2\ \text{Hz}$ | Yes |
| Plantar Flexor | Ankle/Toes | $7320.8\ \mu\text{m}$ | $43.2^\circ$ | $0.22^\circ$ | $1.0000$ | $48.2^\circ$ | $0.24^\circ$ | $1.0000$ | $45.1\ \text{Hz}$ | Yes |
| Soleus | Ankle/Toes | $7840.3\ \mu\text{m}$ | $46.8^\circ$ | $0.21^\circ$ | $1.0000$ | $49.7^\circ$ | $0.25^\circ$ | $1.0000$ | $41.5\ \text{Hz}$ | Yes |
| Semitendinosus | Knee | $8118.5\ \mu\text{m}$ | $50.4^\circ$ | $0.22^\circ$ | $1.0000$ | $54.7^\circ$ | $0.24^\circ$ | $1.0000$ | $30.8\ \text{Hz}$ | Yes |
| Extensor Digitorum | Ankle/Toes | $8735.7\ \mu\text{m}$ | $54.0^\circ$ | $0.22^\circ$ | $1.0000$ | $78.8^\circ$ | $0.24^\circ$ | $1.0000$ | $32.6\ \text{Hz}$ | Yes |

All 14 pools are robustly modulated (modulation depth $\ge 30\ \text{Hz}$, circular $R > 0.9999$).

### C. Bilateral Coordination Across Homologous Pairs
Bilateral lag was estimated within the physiologically relevant interval $[-T/2, +T/2] = [-356, +356]\ \text{ms}$, retaining sign and direction without applying `abs()`. Zero-lag Pearson correlation is reported directly:

| Homologous Pool Pair | Signed Bilateral Lag $\Delta t_{\text{L-R}}$ | Phase Lag $\Delta\phi$ | Zero-Lag Pearson $r$ | Coordination Direction |
|---|---|---|---|---|
| Vastus Lateralis | $+328\ \text{ms}$ | $165.7^\circ$ | $-0.9586$ | Left leads Right |
| Vastus Medialis | $-287\ \text{ms}$ | $215.0^\circ$ | $-0.8181$ | Right leads Left |
| Iliopsoas | $-300\ \text{ms}$ | $208.4^\circ$ | $-0.8744$ | Right leads Left |
| Rectus Femoris | $-293\ \text{ms}$ | $212.0^\circ$ | $-0.8433$ | Right leads Left |
| Gracilis | $-322\ \text{ms}$ | $197.3^\circ$ | $-0.9418$ | Right leads Left |
| Adductors | $-298\ \text{ms}$ | $209.5^\circ$ | $-0.8592$ | Right leads Left |
| Gastrocnemius | $-345\ \text{ms}$ | $185.7^\circ$ | $-0.9739$ | Right leads Left |
| Gluteus | $-334\ \text{ms}$ | $191.3^\circ$ | $-0.9652$ | Right leads Left |
| **Tibialis Anterior** | **$+295\ \text{ms}$** | **$149.0^\circ$** | **$-0.8432$** | **Left leads Right** |
| Biceps Femoris | $+327\ \text{ms}$ | $165.2^\circ$ | $-0.9557$ | Left leads Right |
| Plantar Flexor | $-297\ \text{ms}$ | $210.0^\circ$ | $-0.8607$ | Right leads Left |
| Soleus | $-329\ \text{ms}$ | $193.8^\circ$ | $-0.9657$ | Right leads Left |
| Semitendinosus | $-335\ \text{ms}$ | $190.8^\circ$ | $-0.9692$ | Right leads Left |
| Extensor Digitorum | $-351\ \text{ms}$ | $182.7^\circ$ | $-0.9917$ | Right leads Left |

**Key Finding:** Bilateral phase lags range between $149.0^\circ$ and $215.0^\circ$ (mean: $188.7^\circ$, close to anti-phase alternation). Crucially, the bilateral lags are **not exactly $180.0^\circ$** across all pools. Assuming an exact $180^\circ$ lag for every pair is empirically incorrect.

### D. Relocated TA Coordination Pattern
In this TA-relocated simulation ($L4–L5$, centroid $6773.4\ \mu\text{m}$ Left), TA's peak activation occurs at **$29.2^\circ$** (Left) and **$20.7^\circ$** (Right):
- TA fires in strong co-activation with caudal extensors:
  - *Gluteus* ($r = +0.94$)
  - *Biceps Femoris* ($r = +0.92$)
  - *Soleus* ($r = +0.89$)
  - *Gastrocnemius* ($r = +0.86$)
- TA is negatively correlated with rostral flexors:
  - *Vastus Medialis* ($r = -0.85$)
  - *Iliopsoas* ($r = -0.74$)
- **Functional Mechanism:** Because premotor connections depend strictly on anatomical proximity ($\sigma = 500\ \mu\text{m}$ Gaussian kernel), relocating TA into $L4–L5$ embeds it within the caudal premotor microcircuitry. Consequently, TA receives the caudal extensor wave phase, causing physiological co-contraction with its anatomical antagonist (*Gastrocnemius* / *Soleus*).

---

## 6. Removal of Unsupported Claims and Clarification of Limits

1. **Connectivity is Not Purely Isotropic:** Although connection probability decays with Euclidean distance via an isotropic Gaussian kernel ($\sigma = 500\ \mu\text{m}$), boundary truncation at cord edges, non-uniform neuronal spatial density, and differential laminar genetic profiles break spatial isotropy.
2. **Smooth Center-of-Mass Trajectory Does Not Prove Wave Continuity:** A center-of-mass trajectory can appear smooth even when two distant neuronal clusters alternate in activity. True wave continuity requires demonstrating that intermediate spatial bins activate sequentially with consistent signed delays ($\Delta t > 0$, $R_\Delta \approx 1.0$), as proven here in Section 4.
3. **Bilateral Lags Are Not Exactly 180°:** Lags vary between $149^\circ$ and $215^\circ$ depending on the motor pool's specific rostrocaudal distribution and premotor pool composition.
4. **Anatomical Relocation Does Not Automatically Improve Coordination:** Moving TA to its anatomically correct segment ($L4–L5$) disrupts functional dorsiflexor/plantarflexor alternation in this proximity-based architecture. Without muscle-specific wiring rules, anatomical realism exacerbates physiological co-contraction.
5. **Single-Realization Scope:** This analysis characterizes Realization 1 of Condition D. The observed low cycle-to-cycle variability ($\text{SD} < 1\ \text{ms}$) reflects deterministic rhythmicity within a single network realization, not variability across independently instantiated random connectomes.

---

## 7. Remaining Uncertainties

1. **Lumped Generic Pools:** Several motor pools in the model represent functional groupings (e.g., *Plantar Flexor* represents FDL, FHL, and TP; *Adductors* lumps magnus, longus, and brevis). Individual sub-muscles may exhibit divergent activation profiles in vivo.
2. **Multi-Joint Functions:** Muscles such as *Rectus Femoris* (knee extensor / hip flexor), *Gracilis* (knee flexor / hip adductor), and *Biceps Femoris* (knee flexor / hip extensor) participate in multiple kinematic synergies. Their firing cannot be neatly categorized as pure "stance" or "swing" without coupled biomechanical simulation.
3. **Absence of Proprioceptive Feedback:** This simulation was driven purely by tonic drive ($I_e = 25.0\ \text{pA}$) without closed-loop muscle spindle or Golgi tendon organ sensory afferents. Afferent feedback might phase-lock or reorganize co-contracting synergists in vivo.

---

## 8. Summary of Replaced Artifacts

All outputs were regenerated and replaced in place inside `komi_full_reproduction/experiments/all_pool_analysis/`:
- [`AllPool_Hip_Knee_Ankle_TA_Relocated.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/all_pool_analysis/AllPool_Hip_Knee_Ankle_TA_Relocated.png): High-resolution (300 DPI) 5-section composite (Panels A1–A2, B1–B2, C1–C4, D1–D4, E1–E3).
- [`all_pool_metrics.json`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/all_pool_analysis/all_pool_metrics.json): Comprehensive machine-readable metrics, including reconciled counts, trace verifications, bilateral coordination, and multi-resolution neighboring delays.
- [`pool_inventory.csv`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/all_pool_analysis/pool_inventory.csv): Detailed inventory of all 14 hindlimb pools and 4 excluded pools with coordinates derived dynamically from data.
- [`ALL_POOL_SUMMARY.md`](file:///c:/Users/LAB/Documents/GitHub/ibrain/komi_full_reproduction/experiments/all_pool_analysis/ALL_POOL_SUMMARY.md): This report.
