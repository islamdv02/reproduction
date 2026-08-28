# Figure 3 Reproduction Plan
## EMG Patterns of 27 Hindlimb Muscles in the Locomotor Step Cycle

### 1. Scientific Purpose
Figure 3 collates standardized, piecewise-linear electromyographic (EMG) profiles for all 27 hindlimb muscles during forward level walking at moderate speeds ($\approx 0.6\text{ m/s}$, cycle period $\approx 700\text{ ms}$). The step cycle is normalized to 100 equal intervals with swing standardized to $30\%$ ($0\% - 30\%$) and stance standardized to $70\%$ ($30\% - 100\%$).

### 2. Biological Groups & Functional Behavior
- **Extensors (Left Column, 14 muscles)**: Active during stance and late swing ($E_1$ phase, ~60 ms before foot contact, $21\% - 30\%$). Peak activity occurs in early-to-mid stance ($40\% - 65\%$).
- **Flexors (Right Top, 7 muscles)**: Active exclusively during swing ($0\% - 30\%$) to flex the hip, knee, and ankle to propel the limb forward.
- **Retractors (Right Bottom, 5 muscles: BFp, FDL, Gracilis, ST, SMp)**: Exhibit biphasic bursts, with their primary activation at the stance-to-swing transition ($85\% - 100\%$ / $0\% - 10\%$) to provide the final extensor thrust and lift the foot upward and backward for ground clearance.

### 3. Implementation Details
- `src/emg_profiles.py`: Piecewise linear generator for 27 profiles, normalization to $100\%$ peak.
- `src/figure3_analysis.py`: Publication plotting script generating the multi-panel layout matching Figure 3 with references (1–26) annotated.
- `tests/test_figure3.py`: Verification of 100 bins, peak normalization, 30% swing duration, and profile bounds.

### 4. Validation Criteria
- All 27 profiles reach peak $100\%$ at least once.
- Swing burst for flexors within $0\% - 30\%$.
- Late swing ($E_1$) pre-activation for ankle extensors (MG, LG, Soleus) at $20\% - 30\%$.
- Retractor stance-swing burst at $85\% - 100\%$.
