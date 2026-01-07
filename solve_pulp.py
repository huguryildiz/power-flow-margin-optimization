"""
Solve the synthetic max–min flow margin MILP using PuLP (CBC by default).
Also exposes helper functions so plotting can reuse the same computations.
"""

from __future__ import annotations
from typing import Dict, Tuple, Any
import pulp

import data


def compute_flows_and_margins(taps: Dict[str, float], gens: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float], float]:
    flows: Dict[str, float] = {}
    margins: Dict[str, float] = {}

    for l in data.LINES:
        flow = data.F_ref[l]
        for p in data.PSTS:
            flow += data.PSDF[(l, p)] * (taps[p] - data.t_init[p])
        for g in data.GENS:
            flow += data.PTDF[(l, g)] * (gens[g] - data.G_init[g])
        flows[l] = flow
        margins[l] = data.F_max[l] - abs(flow)

    return flows, margins, min(margins.values())


def base_case() -> Dict[str, Any]:
    taps0 = {p: float(data.t_init[p]) for p in data.PSTS}
    gens0 = {g: float(data.G_init[g]) for g in data.GENS}
    flows0, margins0, min0 = compute_flows_and_margins(taps0, gens0)
    return {"taps": taps0, "gens": gens0, "flows": flows0, "margins": margins0, "min_margin": float(min0)}


def solve_with_pulp(msg: bool = False) -> Dict[str, Any]:
    prob = pulp.LpProblem("MaxMinFlowMargin_v3", pulp.LpMaximize)

    t = {p: pulp.LpVariable(f"tap_{p}", lowBound=-data.t_range[p], upBound=data.t_range[p], cat=pulp.LpInteger) for p in data.PSTS}
    G = {g: pulp.LpVariable(f"gen_{g}", lowBound=data.G_min[g], upBound=data.G_max[g], cat=pulp.LpContinuous) for g in data.GENS}
    m = pulp.LpVariable("min_margin", lowBound=0.0, cat=pulp.LpContinuous)

    prob += m

    for (a, b) in data.COUPLED_TAPS:
        prob += (t[a] == t[b]), f"Couple_{a}_{b}"

    prob += (pulp.lpSum([G[g] - data.G_init[g] for g in data.GENS]) == 0.0), "PowerBalance"

    for l in data.LINES:
        flow_expr = data.F_ref[l]
        for p in data.PSTS:
            flow_expr += data.PSDF[(l, p)] * (t[p] - data.t_init[p])
        for g in data.GENS:
            flow_expr += data.PTDF[(l, g)] * (G[g] - data.G_init[g])

        prob += (flow_expr <= data.F_max[l] - m), f"ThermalPos_{l}"
        prob += (-flow_expr <= data.F_max[l] - m), f"ThermalNeg_{l}"

    solver = pulp.PULP_CBC_CMD(msg=msg)
    status = prob.solve(solver)

    taps = {p: float(pulp.value(t[p])) for p in data.PSTS}
    gens = {g: float(pulp.value(G[g])) for g in data.GENS}
    flows, margins, min_margin = compute_flows_and_margins(taps, gens)

    return {
        "status": pulp.LpStatus[status],
        "objective_min_margin": float(pulp.value(m)),
        "taps": taps,
        "gens": gens,
        "flows": flows,
        "margins": margins,
        "min_margin_recomputed": float(min_margin),
    }


def main() -> None:
    b = base_case()
    print("=== BASE CASE (INITIAL) ===")
    print(f"Min margin = {b['min_margin']:.3f} MW")
    for l in data.LINES:
        print(f"{l}: flow={b['flows'][l]: .3f} MW, margin={b['margins'][l]: .3f} MW")

    print("\n=== OPTIMIZED (MILP) ===")
    r = solve_with_pulp(msg=False)
    print(f"Solver status         = {r['status']}")
    print(f"Objective min margin  = {r['objective_min_margin']:.3f} MW")
    print(f"Recomputed min margin = {r['min_margin_recomputed']:.3f} MW")

    print("\nFinal taps:")
    for p in data.PSTS:
        print(f"  {p}: {r['taps'][p]: .0f} (init {data.t_init[p]})")

    print("\nFinal generation outputs (MW):")
    for g in data.GENS:
        print(f"  {g}: {r['gens'][g]: .3f} (init {data.G_init[g]})")

    print("\nFinal line flows and margins:")
    for l in data.LINES:
        print(f"{l}: flow={r['flows'][l]: .3f} MW, margin={r['margins'][l]: .3f} MW")


if __name__ == "__main__":
    main()
