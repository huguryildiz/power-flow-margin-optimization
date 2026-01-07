# Synthetic Flow Margin Optimization

This repository provides a **fully synthetic** mixed-integer linear programming (MILP) model
for **maximizing the minimum thermal margin** across a set of critical network elements (lines).

It also includes a small plotting utility that produces interview-friendly figures:
- Base vs Optimized **margins**
- Base vs Optimized **|flow| vs limit**
- Base vs Optimized **control actions** (taps and generator outputs)

---

## 1) Problem Description

A transmission operator monitors several **critical network elements (CNEs)** that must stay within thermal limits.
The operator can influence line flows using:

1) **Phase-shifting devices** with **discrete (integer) tap positions**, and  
2) **Generator redispatch**, where generator outputs can change within min/max limits.

The goal is to make the *whole system safer* by improving the **weakest** line.
Therefore, we maximize the **minimum thermal margin** over all monitored lines.

Thermal margin of line ℓ:
\[
\text{margin}_\ell = F^{max}_\ell - |F_\ell|
\]

---

## 2) Sets / Indices

- Lines: \(\mathcal{L}\) (CNEs), indexed by \(\ell\)
- Phase shifters: \(\mathcal{P}\), indexed by \(p\)
- Generators: \(\mathcal{G}\), indexed by \(g\)

---

## 3) Parameters

For each line \(\ell\in\mathcal{L}\):
- \(F^{max}_\ell\) : thermal limit (MW)
- \(F^{ref}_\ell\) : reference flow before control (MW)

For each phase shifter \(p\in\mathcal{P}\):
- \(t^{init}_p\) : initial tap position (integer)
- \(R_p\) : tap range, taps allowed in \([-R_p, +R_p]\) (integer)
- \(PSDF_{\ell,p}\) : flow sensitivity (MW per tap)

For each generator \(g\in\mathcal{G}\):
- \(G^{init}_g\) : initial output (MW)
- \(G^{min}_g, G^{max}_g\) : output limits (MW)
- \(PTDF_{\ell,g}\) : flow sensitivity (MW per +1 MW generation)

**Coupling constraints (operational links):**
- Some phase shifters must share the same tap position.

**Power balance (lossless approximation):**
\[
\sum_{g\in\mathcal{G}} (G_g - G^{init}_g) = 0
\]

---

## 4) Decision Variables

- \(t_p\in\mathbb{Z}\): tap position of phase shifter \(p\)
- \(G_g\in\mathbb{R}\): final generator output (MW)
- \(m\ge 0\): minimum margin across all lines (MW)

---

## 5) Flow Model (Linear Sensitivity Approximation)

Final flow on line \(\ell\):
\[
F_\ell =
F^{ref}_\ell
+ \sum_{p\in\mathcal{P}} PSDF_{\ell,p}(t_p - t^{init}_p)
+ \sum_{g\in\mathcal{G}} PTDF_{\ell,g}(G_g - G^{init}_g)
\]

---

## 6) Objective (Max–Min Margin)

\[
\max\; m
\]

---

## 7) Constraints

### 7.1 Tap bounds
\[
-R_p \le t_p \le R_p \quad \forall p\in\mathcal{P}
\]

### 7.2 Generator bounds
\[
G^{min}_g \le G_g \le G^{max}_g \quad \forall g\in\mathcal{G}
\]

### 7.3 Coupled taps (example)
\[
t_{P1} = t_{P2}, \quad t_{P3} = t_{P4}
\]

### 7.4 Power balance
\[
\sum_{g\in\mathcal{G}} (G_g - G^{init}_g) = 0
\]

### 7.5 Thermal safety via absolute-value linearization
We require:
\[
|F_\ell| \le F^{max}_\ell - m \quad \forall \ell\in\mathcal{L}
\]

Linearization:
\[
F_\ell \le F^{max}_\ell - m
\]
\[
-F_\ell \le F^{max}_\ell - m
\]

---

## 8) Run

```bash
python -m pip install -r requirements.txt
python solve_pulp.py
python plot_results.py
```

Plots are saved to `results/`.

---

## License
MIT
