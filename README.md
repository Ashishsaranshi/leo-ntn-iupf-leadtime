# Ephemeris-Driven Proactive I-UPF Relocation in Regenerative LEO-NTN

Evaluation artifact for the paper:

> A. Saranshi, "Ephemeris-Driven Proactive I-UPF Relocation in Regenerative
> LEO-NTN: A Minimum Lead-Time Criterion for Make-Before-Break Continuity."

This repository contains everything needed to regenerate Figs. 1–5 and every
number reported in the paper.

## Contents

| File | Purpose |
|---|---|
| `sim_figs.py` | Ephemeris propagation, lead-time/fixed-point computation, load models; generates Figs. 2–5 |
| `fig1.py` | Renders Fig. 1 (architecture + relocation timing budget) |
| `starlink.txt` | Starlink TLE snapshot (CelesTrak supplemental, retrieved 7 Sep 2026) |
| `iridium.txt` | Iridium-NEXT TLE snapshot (CelesTrak GP, retrieved 7 Sep 2026) |
| `oneweb.txt` | OneWeb TLE snapshot (CelesTrak GP, retrieved 7 Sep 2026) |

The TLE files are the **frozen snapshot used in the paper**. Do not re-download
them if you want to reproduce the published figures: shell membership in the
public element sets changes daily.

## Requirements

```
python3 -m pip install -r requirements.txt
```

Tested with Python 3.10, Skyfield 1.54 (results verified identical on 1.55),
SGP4 2.27, Matplotlib 3.10.9, NumPy 2.2.6.

## Reproducing the figures

```
python3 sim_figs.py --starlink starlink.txt --iridium iridium.txt --oneweb oneweb.txt
python3 fig1.py
```

This writes `feeder_delay_pass.png` (Fig. 2), `delta_min_analysis.png` (Fig. 3),
`load_feasibility.png` (Fig. 4), `mg1_refinement.png` (Fig. 5), and
`fig_architecture.png` (Fig. 1).

The propagation window is anchored to the **median TLE epoch of the snapshot**
(not the run date), so results are identical regardless of when the script is
run. Use `--start YYYY-MM-DD` to override.

Running `sim_figs.py` with no arguments falls back to synthetic TLEs at the
nominal altitudes; this reproduces the qualitative behaviour but not the exact
published numbers.

## Expected output

```
  starlink.txt: 106 satellites in the 550+/-25 km / 53+/-2 deg shell
  iridium.txt: 68 satellites in the 780+/-25 km / 86+/-2 deg shell
  oneweb.txt: 645 satellites in the 1200+/-25 km / 87+/-2 deg shell
  propagation window: 2026-09-08 + 7 d (median TLE epoch)
Starlink-550: 121 passes, edge RTT ~11.9 ms, lead 68 ms, M 99-244 s
Iridium-780:  118 passes, edge RTT ~15.5 ms, lead 82 ms, M 123-313 s
OneWeb-1200:  143 passes, edge RTT ~20.8 ms, lead 103 ms, M 153-441 s

=== headline numbers ===
rep 550 pass: culm 78 deg, dur 8.1 min, floor 1-way 1.8 ms,
              edge 1-way 6.0 ms (RTT 12.0 ms), slant 550-1792 km
  rep pass effective altitude (Eq.1, Re=6371): 540 km
Starlink-550: edge RTT 11.9 ms, lead 66-68 ms,  M 99-244 s,  worst lead/M 0.07%
Iridium-780:  edge RTT 15.5 ms, lead 82-82 ms,  M 123-313 s, worst lead/M 0.07%
OneWeb-1200:  edge RTT 20.8 ms, lead 103-104 ms, M 153-441 s, worst lead/M 0.07%
grazing 550: M=99.1s  Nmax(mu=100)=9902  batch(5000,500)=10.05s  mg1(5000,500)=0.0499s
overhead 550:  Nmax(mu=500) = 122190
overhead 1200: Nmax(mu=500) = 220638
```

These correspond to the values reported in the paper: required lead
66–68 / 82 / 103–104 ms at 550 / 780 / 1200 km, margins 99–244 / 123–313 /
153–441 s, worst-case lead/margin 0.07%, and the M/G/1 result
10.05 s -> 49.9 ms (201x) for N = 5000 at mu = 500/s on the tightest pass.

## Evaluation setup (as in the paper)

* Gateway: 13.08 N, 80.27 E; feeder elevation mask 10 deg.
* Shell filter: satellites within +/-25 km and +/-2 deg of each nominal orbit.
* Usable-pass criterion: passes culminating below 12 deg are discarded.
* Propagation: SGP4 via Skyfield; slant ranges are topocentric distances in
  Skyfield's WGS84 model. Eq. (1) in the paper (spherical, Re = 6371 km,
  c = 299792.458 km/s) is used only for the analytic curves of Fig. 3(a).
* Not modelled: atmospheric refraction, terrain masking, antenna slew.

## Data source and license

TLEs retrieved from CelesTrak (https://celestrak.org):
`supplemental/sup-gp.php?FILE=starlink`, `gp.php?GROUP=iridium-NEXT`,
`gp.php?GROUP=oneweb`. Element sets are redistributed under CelesTrak's terms
of use.

Code in this repository is released under the MIT License (see `LICENSE`).
 
