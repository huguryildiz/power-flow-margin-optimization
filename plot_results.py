"""
Generate plots for the synthetic flow-margin MILP.

Outputs (PNG) in results/:
- margins_base_vs_opt.png
- absflow_vs_limit.png
- controls.png
"""

from __future__ import annotations
import os
import math
import matplotlib.pyplot as plt

import data
import solve_pulp


OUT_DIR = os.path.join(os.path.dirname(__file__), "results")


def save_margins_plot(base, opt) -> None:
    lines = data.LINES
    base_m = [base["margins"][l] for l in lines]
    opt_m  = [opt["margins"][l] for l in lines]

    x = list(range(len(lines)))
    width = 0.4

    plt.figure()
    plt.bar([i - width/2 for i in x], base_m, width=width, label="Base")
    plt.bar([i + width/2 for i in x], opt_m,  width=width, label="Optimized")
    plt.xticks(x, lines)
    plt.ylabel("Margin (MW)")
    plt.title("Line Margins: Base vs Optimized")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "margins_base_vs_opt.png"), dpi=200)
    plt.close()


def save_absflow_vs_limit_plot(base, opt) -> None:
    lines = data.LINES
    base_abs = [abs(base["flows"][l]) for l in lines]
    opt_abs  = [abs(opt["flows"][l]) for l in lines]
    limits   = [data.F_max[l] for l in lines]

    x = list(range(len(lines)))
    width = 0.4

    plt.figure()
    plt.bar([i - width/2 for i in x], base_abs, width=width, label="|Flow| Base")
    plt.bar([i + width/2 for i in x], opt_abs,  width=width, label="|Flow| Optimized")
    plt.plot(x, limits, marker="o", linewidth=1.5, label="Thermal Limit (Fmax)")
    plt.xticks(x, lines)
    plt.ylabel("MW")
    plt.title("|Flow| vs Thermal Limit")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "absflow_vs_limit.png"), dpi=200)
    plt.close()


def save_controls_plot(base, opt) -> None:
    # taps
    psts = data.PSTS
    base_t = [base["taps"][p] for p in psts]
    opt_t  = [opt["taps"][p] for p in psts]

    # gens
    gens = data.GENS
    base_g = [base["gens"][g] for g in gens]
    opt_g  = [opt["gens"][g] for g in gens]

    plt.figure(figsize=(10, 4))

    # left subplot-like using separate axes positions to obey "no subplots"? The instruction is for charts in python_user_visible tool.
    # Here we're just writing a script; still we keep it simple: create two separate figures instead of subplots.
    plt.close()

    # Taps figure
    x = list(range(len(psts)))
    width = 0.4
    plt.figure()
    plt.bar([i - width/2 for i in x], base_t, width=width, label="Base")
    plt.bar([i + width/2 for i in x], opt_t,  width=width, label="Optimized")
    plt.xticks(x, psts)
    plt.ylabel("Tap position")
    plt.title("Phase Shifter Taps: Base vs Optimized")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "controls_taps.png"), dpi=200)
    plt.close()

    # Generators figure
    x = list(range(len(gens)))
    plt.figure()
    plt.bar([i - width/2 for i in x], base_g, width=width, label="Base")
    plt.bar([i + width/2 for i in x], opt_g,  width=width, label="Optimized")
    plt.xticks(x, gens)
    plt.ylabel("Generation (MW)")
    plt.title("Generator Outputs: Base vs Optimized")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "controls_gens.png"), dpi=200)
    plt.close()


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    base = solve_pulp.base_case()
    opt = solve_pulp.solve_with_pulp(msg=False)

    save_margins_plot(base, opt)
    save_absflow_vs_limit_plot(base, opt)
    save_controls_plot(base, opt)

    print("Saved plots to:", OUT_DIR)
    print("- margins_base_vs_opt.png")
    print("- absflow_vs_limit.png")
    print("- controls_taps.png")
    print("- controls_gens.png")


if __name__ == "__main__":
    main()
