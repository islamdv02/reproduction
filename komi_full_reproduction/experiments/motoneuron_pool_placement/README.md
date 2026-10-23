# Planned Motoneuron Pool Placement Experiments

## 1. Overview and Scientific Motivation
This directory is reserved for post-baseline experiments investigating how hindlimb motoneuron pool stereotaxy along the rostrocaudal (RC) axis influences motor pattern generation, phase relationships, and antagonistic coordination in the 3D Komi et al. spinal cord model.

In the baseline model (`komi-baseline-v1`), 18 motoneuron pools are assigned to stereotyped rostrocaudal segments (T13–S4) matching retrograde tracing from Hayashi et al. / BergLab:
- **Rostral flexor/extensor hip/knee pools:** *Quadratus Lumburum* (L1), *Vastus Lateralis* (L1–L2), *Vastus Medialis* (L1–L3), *Tibialis Anterior* (L2–L4)
- **Caudal ankle/knee pools:** *Biceps Femoris* (L3–L6), *Gastrocnemius* (L3–L5), *Soleus* (L4–L6), *Plantar Flexor* (L4–L6), *Semitendinosus* (L4–S1)

The baseline model demonstrates that rostral-to-caudal traveling waves produce natural phase delays between flexor and extensor pools:
- $\Delta\phi(\text{iL2}-\text{iL5}) \approx 192.4^\circ$ (antagonistic alternation)
- Antagonistic EMG reciprocal bursting: *Vastus Medialis* vs *Biceps Femoris*, *Tibialis Anterior* vs *Soleus*.

## 2. Planned Experimental Protocols

### Experiment 1: Systematic Rostrocaudal Segment Shifting
- **Objective:** Test whether segment-shifting specific motor pools (e.g. moving *Soleus* rostrally into L2–L3, or moving *Tibialis Anterior* caudally into L5–L6) disrupts antagonistic alternating bursts or inverts phase relationships.
- **Protocol:**
  1. Hold interneuronal connectome ($W_{\text{interneuron}}$) strictly fixed to baseline `komi-baseline-v1`.
  2. Modulate motoneuron soma RC coordinates and pool IDs (`N.MnID`) according to test permutations.
  3. Recompute premotor synaptic weights using the original author distance-dependent probability rules (`GenerateSynapticDistrib.m`).
  4. Simulate under identical baseline drive ($I_e = 30$ pA, 10,000 ms).
  5. Measure resulting EMG phase offsets, cycle frequency, and burst envelopes.

### Experiment 2: Longitudinal Pool Overlap & Dispersion
- **Objective:** Evaluate the effect of spatial dispersion (broad pool span vs tightly clustered pool) on EMG signal-to-noise ratio, burst duration, and recruitment synchrony.
- **Protocol:**
  1. Vary the spatial standard deviation ($\sigma_{\text{RC}}$) of motoneuron positions for antagonistic pairs (*VM* / *BF* and *TA* / *Sol*).
  2. Compare narrow compact motor columns ($\sigma = 200\ \mu\text{m}$) against expanded diffuse columns ($\sigma = 1500\ \mu\text{m}$).

### Experiment 3: Commissural Symmetry vs Asymmetry in Motor Pools
- **Objective:** Examine whether unilateral rostrocaudal pool displacement disrupts bilateral left-right alternating coordination ($\Delta\phi_{\text{L-R}} \approx 180^\circ$) or induces limb-asymmetric limping gaits.

## 3. Status and Baseline Policy
- **Current Status:** PLANNED ONLY — NOT YET EXECUTED.
- **Prerequisite:** The baseline model has been validated and frozen under Git tag `komi-baseline-v1` and commit `validated_komi_baseline`. No experiments in this directory will overwrite or modify the frozen baseline results.
