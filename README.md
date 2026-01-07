# 🔌 Power Flow Margin Optimization (Synthetic)

This repository implements a **Mixed-Integer Linear Programming (MILP)** model for **max–min thermal margin optimization** in a transmission network using **linear sensitivity factors**.

The project is designed to be:
- cleanly structured  
- easy to reproduce  
- suitable for GitHub portfolios  

It also includes plotting utilities to compare:
- Base vs Optimized **margins**
- Base vs Optimized **|flow| vs thermal limits**
- Base vs Optimized **control actions** (PST taps and generator outputs)

---

## 📁 Repository Structure

```text
power-flow-margin-optimization/
|
|-- solve_pulp.py              # Main optimization model (MILP, PuLP + CBC)
|-- plot_results.py            # Plot generation (base vs optimized comparisons)
|-- data.py                    # Fully synthetic dataset (lines, PSTs, generators, sensitivities)
|
|-- requirements.txt
|-- README.md
|
|-- results/                   # Generated plots (after running plot_results.py)
    |-- margins_base_vs_opt.png
    |-- absflow_vs_limit.png
    |-- controls_taps.png
    |-- controls_gens.png
```

---

## 🧾 Problem Description

A transmission operator monitors a set of **critical network elements (lines)** that must remain within their **thermal limits**.

The operator can influence line flows using:
- **Phase-Shifting Transformers (PSTs)** with **integer tap positions**
- **Generator redispatch** with minimum/maximum output bounds

The goal is to improve system security by maximizing the **worst (minimum) thermal margin** across all monitored lines.

> Thermal margin of a line ℓ (for all ℓ ∈ ℒ):  
> **margin_ℓ = F_ℓ^max − |F_ℓ|**

---

## 📊 Synthetic Input Data

All data in this repo is **synthetic** and fully editable in `data.py`.

### Line data
- **F_ℓ^max** : thermal limit of line ℓ (MW), ∀ ℓ ∈ ℒ  
- **F_ℓ^ref** : reference flow before control (MW), ∀ ℓ ∈ ℒ  

### PST data
- **t_p^init** : initial tap position of PST p (integer), ∀ p ∈ 𝓟  
- **R_p** : available tap range of PST p, taps allowed in [−R_p, +R_p], ∀ p ∈ 𝓟  
- **PSDF_{ℓ,p}** : MW change on line ℓ per +1 tap on PST p, ∀ ℓ ∈ ℒ, p ∈ 𝓟  

### Generator data
- **G_g^init** : initial output of generator g (MW), ∀ g ∈ 𝓖  
- **G_g^min , G_g^max** : output bounds of generator g (MW), ∀ g ∈ 𝓖  
- **PTDF_{ℓ,g}** : MW change on line ℓ per +1 MW redispatch of generator g, ∀ ℓ ∈ ℒ, g ∈ 𝓖  

---

## 🧮 Optimization Model

### Sets
- **ℒ** : set of monitored lines, indexed by ℓ  
- **𝓟** : set of PSTs, indexed by p  
- **𝓖** : set of generators, indexed by g  

---

### Decision Variables
- **t_p ∈ ℤ**  
  Tap position of PST p, ∀ p ∈ 𝓟  

- **G_g ∈ ℝ**  
  Output power of generator g (MW), ∀ g ∈ 𝓖  

- **m ≥ 0**  
  Minimum thermal margin across all lines (MW)  

---

## 🔁 Flow Model (Linear Sensitivity Approximation)

Final power flow on line ℓ is computed as:

```
F_ℓ = F_ℓ^ref
    + Σ_{p∈𝓟} PSDF_{ℓ,p} · (t_p − t_p^init)
    + Σ_{g∈𝓖} PTDF_{ℓ,g} · (G_g − G_g^init)      ∀ ℓ ∈ ℒ
```

---

## 🎯 Objective Function

Maximize the worst-case (minimum) margin across all lines:

```
maximize   m
```

---

## 📐 Constraints

### 1️⃣ PST Tap Bounds
```
−R_p ≤ t_p ≤ R_p            ∀ p ∈ 𝓟
```

### 2️⃣ Generator Output Bounds
```
G_g^min ≤ G_g ≤ G_g^max     ∀ g ∈ 𝓖
```

### 3️⃣ Power Balance (Lossless Approximation)
```
Σ_{g∈𝓖} (G_g − G_g^init) = 0
```

### 4️⃣ Thermal Safety (Absolute-Value Linearization)
For every monitored line:
```
|F_ℓ| ≤ F_ℓ^max − m         ∀ ℓ ∈ ℒ
```

This is enforced using two linear inequalities:
```
 F_ℓ ≤ F_ℓ^max − m          ∀ ℓ ∈ ℒ
−F_ℓ ≤ F_ℓ^max − m          ∀ ℓ ∈ ℒ
```

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python solve_pulp.py
python plot_results.py
```

---

## 📦 Requirements

```
pulp>=2.7
matplotlib>=3.7
```

---

## 👤 Author

**Huseyin Ugur Yildiz**
