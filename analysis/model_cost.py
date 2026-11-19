"""AI cost per site of the proposed daily agent on a self-hosted model vs APIs, and what it does to N1/N2/F1.

Run: python3 analysis/model_cost.py   (stdlib; self-check first, then the tables). Sources: docs/research/08.
V = verified figure, E = our estimate. Every € is per site unless said otherwise.
"""
from math import ceil

from kpis import LLM, P_IN, P_OUT, USD_EUR

WEEKS = 52
LIFE = 5  # years of hardware life (E)
KWH = 0.32  # €/kWh Italian household price H1 2026 (V, Euronews/Eurostat); also used for the server room (E)
TOK_IN, TOK_OUT = 7_973, 965  # tokens per site-week, measured: Qwen3.5-4B Q4 bench, 7 calls, thinking off (V)
# Report S5 (workbook): S_net, gross saving S, VORB (€/wk); O5 there = Devstral price at its token count
S5 = {"conservative": (1.1156, 1.3768, 0.0772), "upside": (1.7957, 2.0927, 0.7930)}
FLEETS = (100, 1_000, 10_000)
OPS_LOCAL = 7_000  # €/yr: 0.1 FTE MLOps (model pinning, re-validation on the replay gate, updates) (E)
OPS_API = 3_500  # €/yr: re-validate when the vendor retires the model (Devstral 2 did) (E)


def api(p_in, p_out):
    """€/site/wk of an API at $/M token prices."""
    return (TOK_IN * p_in + TOK_OUT * p_out) / 1e6 * USD_EUR


def central(n, node_eur, watts, sites_per_node):
    """€/site/wk of an on-prem inference pool: HA (≥ 2 nodes), capex over LIFE, power 24/7, ops shared."""
    nodes = max(2, ceil(n / sites_per_node) + 1)
    per_year = nodes * (node_eur / LIFE + watts * 8.76 * KWH) + OPS_LOCAL
    return per_year / n / WEEKS


def edge(box_eur, idle_w):
    """€/site/wk of a box at each site: capex over LIFE + idle power (one call/day is ~0.4 Wh, negligible)."""
    return (box_eur / LIFE + idle_w * 8.76 * KWH) / WEEKS


OPTIONS = {
    "Devstral 2 API (retired, the pilot's price)": lambda n: api(P_IN, P_OUT) + OPS_API / n / WEEKS,
    "EU API, Ministral 3 8B ($0.15/$0.15)": lambda n: api(0.15, 0.15) + OPS_API / n / WEEKS,
    # one node at the M1's measured 16 s/call serial does ~5k calls in a 22 h plan window; a 20 GB GPU node ≥ 5x (E)
    "Central on-prem, right-sized GPU node (€4k, 100 W)": lambda n: central(n, 4_000, 100, 25_000),
    "Central on-prem, L40S server (€18k, 300 W) upper bound": lambda n: central(n, 18_000, 300, 5_000),
    "Edge upsell: Orin Nano Super + case (€400, 6 W idle)": lambda n: edge(400, 6),  # $399 devkit (V) + case (E)
    "Edge upsell: industrial Orin NX 16GB (€2,000, 8 W idle)": lambda n: edge(2_000, 8),  # €1.5–3k (E)
}


def check():
    req, tin, tout, _ = LLM["C"]
    o5_c = (tin * P_IN + tout * P_OUT) / 1e6 * USD_EUR
    assert round(o5_c, 4) == 7.7086, o5_c  # pilot C's O5 in the workbook
    assert edge(0, 0) == 0 and central(10**9, 0, 0, 1) < 1e-6
    for n in FLEETS:  # sizing sanity: more sites never costs more per site
        assert central(n * 10, 4_000, 100, 25_000) <= central(n, 4_000, 100, 25_000)


def breakeven_fleet(f, s_net):
    """Smallest fleet at which N1 = S_net − O5 stays ≥ 90% of S_net (AI eats ≤ 10% of the gain)."""
    n = 10
    while f(n) > 0.1 * s_net and n < 10**7:
        n = ceil(n * 1.1)
    return n


def main():
    check()
    print(f"Tokens per site-week: {TOK_IN:,} in / {TOK_OUT:,} out (measured). Pilot C was "
          f"{LLM['C'][1] / 1e6:.1f} M in / {LLM['C'][2] / 1e6:.2f} M out.\n")
    print("| AI cost O5 (€/site/wk) | " + " | ".join(f"{n:,} sites" for n in FLEETS) + " | fleet for AI ≤ 10% of gain |")
    print("|---|" + "---|" * (len(FLEETS) + 1))
    for name, f in OPTIONS.items():
        be = breakeven_fleet(f, S5["conservative"][0])
        print(f"| {name} | " + " | ".join(f"{f(n):.4f}" for n in FLEETS) + f" | {be:,} |" if be < 10**7 else
              f"| {name} | " + " | ".join(f"{f(n):.4f}" for n in FLEETS) + " | never |")
    for mode, (s_net, s, vorb) in S5.items():
        print(f"\n**S5 {mode}** (S_net €{s_net}/wk before AI)\n")
        print("| Option | fleet | O5 | N1 = S_net − O5 | N2 = O5/S | F1 = VORB − O5 |")
        print("|---|---|---|---|---|---|")
        for name, f in OPTIONS.items():
            for n in (FLEETS if not name.startswith("Edge") else (1,)):
                o5 = f(n)
                print(f"| {name} | {n:,} | {o5:.4f} | {s_net - o5:+.3f} | {o5 / s:.4f} | {vorb - o5:+.3f} |")
    print("\nEdge upsell price floor (what the client must pay per site per year to cover the box): "
          + ", ".join(f"{k.split(': ')[1].split(' (')[0]} €{f(1) * WEEKS:.0f}/yr" for k, f in OPTIONS.items()
                      if k.startswith("Edge")))
    print(f"Break-even edge box price (N1 = 0, conservative, 6 W idle): "
          f"€{(S5['conservative'][0] * WEEKS - 6 * 8.76 * KWH) * LIFE:.0f}")


if __name__ == "__main__":
    main()
