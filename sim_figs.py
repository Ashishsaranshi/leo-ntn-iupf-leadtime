"""Ephemeris-driven regeneration of Figs. 2-5 with the Iridium-780 series.

Reproduces the paper's pipeline: propagate TLEs with Skyfield, detect all
passes over a 7-day window at a Chennai gateway (13.08N, 80.27E, 10 deg mask),
compute RTT_fdr(t), margin M, the fixed point t*, and the batch / M/G/1
feasibility models.

NOTE: uses synthetic-but-representative TLEs (correct altitude/inclination,
current epoch). The paper argues the delay profile is governed by geometry,
not TLE epoch, so results are equivalent; to use downloaded TLEs instead,
replace make_tle() outputs with real element sets (e.g. from CelesTrak).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skyfield.api import EarthSatellite, load, wgs84

# ----------------------------- parameters ---------------------------------
RE = 6378.137          # km, equatorial radius (geometry eq. uses 6371 nominal)
GM = 398600.4418       # km^3/s^2
C  = 299792.458        # km/s
GW_LAT, GW_LON = 13.08, 80.27
MASK = 10.0            # deg
MIN_CULM = 12.0        # deg; passes culminating below this merely graze the mask
K = 4                  # PFCP round trips
TPROC = 0.020          # s (light load)
MU_BASE = 500.0        # /s
DAYS = 7.0

ORBITS = {
    "Starlink-550": dict(h=550.0,  inc=53.0,  color="tab:red"),
    "Iridium-780":  dict(h=780.0,  inc=86.4,  color="tab:green"),
    "OneWeb-1200":  dict(h=1200.0, inc=87.4,  color="tab:blue"),
}

# --------------------------- synthetic TLEs --------------------------------
def tle_checksum(line):
    s = 0
    for ch in line[:68]:
        if ch.isdigit(): s += int(ch)
        elif ch == "-":  s += 1
    return s % 10

def make_tle(name, h_km, inc_deg, raan=120.0, mean_anom=10.0):
    a = RE + h_km
    n = 86400.0 / (2*np.pi*np.sqrt(a**3/GM))     # rev/day
    l1 = "1 99999U 26001A   26182.50000000  .00000000  00000-0  00000-0 0  999"
    l2 = (f"2 99999 {inc_deg:8.4f} {raan:8.4f} 0001000 {90.0:8.4f} "
          f"{mean_anom:8.4f} {n:11.8f}    1")
    l1 = l1[:68] + str(tle_checksum(l1))
    l2 = l2[:68] + str(tle_checksum(l2))
    return l1, l2

import argparse, itertools
_ap = argparse.ArgumentParser()
_ap.add_argument("--starlink"); _ap.add_argument("--iridium"); _ap.add_argument("--oneweb")
_ap.add_argument("--start", default=None,
                 help="UTC start date YYYY-MM-DD for the propagation window; "
                      "default: the median TLE epoch of the loaded snapshot, so "
                      "results depend only on the TLE files, not the run date")
_ap.add_argument("--nsample", type=int, default=6,
                 help="satellites sampled per real TLE file")
ARGS, _ = _ap.parse_known_args()
TLE_FILES = {"Starlink-550": ARGS.starlink, "Iridium-780": ARGS.iridium,
             "OneWeb-1200": ARGS.oneweb}

ts = load.timescale()
gw = wgs84.latlon(GW_LAT, GW_LON)
from datetime import datetime, timezone
# Window start.  Anchored to the snapshot (median TLE epoch) unless --start is
# given, so the same TLE files always reproduce the same passes regardless of
# when the script is run.  _set_window() is called once the TLEs are loaded.
t0 = t1 = None

def _set_window(epoch_days):
    """epoch_days: list of TLE epochs as Julian dates (UTC)."""
    global t0, t1
    if ARGS.start:
        y, m, d = (int(v) for v in ARGS.start.split("-"))
    else:
        med = float(np.median(epoch_days))
        y, m, d = ts.tt_jd(med).utc.year, ts.tt_jd(med).utc.month, int(ts.tt_jd(med).utc.day)
    t0 = ts.utc(y, m, d)
    t1 = ts.utc(y, m, d + DAYS)
    print(f"  propagation window: {y:04d}-{m:02d}-{d:02d} + {DAYS:.0f} d "
          f"({'--start' if ARGS.start else 'median TLE epoch'})")

def rtt_of_range(d_km):     # s, round-trip
    return 2.0*d_km/C

def sat_altitude_km(sat):
    """Mean altitude implied by the TLE mean motion (km)."""
    n_rev_day = sat.model.no_kozai * 1440.0 / (2*np.pi)      # rev/day
    a = (GM / ((n_rev_day * 2*np.pi / 86400.0)**2))**(1/3)   # km
    return a - RE

_SAT_CACHE = {}

def load_real_sats(path, nsample, h_target=None, inc_target=None,
                   h_tol=25.0, inc_tol=2.0):
    """Load a CelesTrak TLE file (2- or 3-line format) and sample evenly.

    When h_target/inc_target are given, only satellites in that orbital shell
    are kept, so a multi-shell constellation file (e.g. Starlink, which spans
    ~350-570 km) yields the single shell the paper claims to model.
    """
    _key = (path, nsample, h_target, inc_target, h_tol, inc_tol)
    if _key in _SAT_CACHE:                 # already loaded; don't re-announce
        return _SAT_CACHE[_key]
    lines = [l.rstrip() for l in open(path) if l.strip()]
    sats = []
    for i, l in enumerate(lines):
        if l.startswith("1 ") and i + 1 < len(lines) and lines[i+1].startswith("2 "):
            name = lines[i-1].strip() if i > 0 and not lines[i-1].startswith(("1 ", "2 ")) else "SAT"
            try:
                s = EarthSatellite(l, lines[i+1], name, ts)
            except Exception as e:
                print(f"  ! skipping malformed TLE near line {i} of {path}: {e}")
                continue
            if h_target is not None:
                if abs(sat_altitude_km(s) - h_target) > h_tol:
                    continue
                if inc_target is not None and \
                   abs(np.degrees(s.model.inclo) - inc_target) > inc_tol:
                    continue
            sats.append(s)
    if h_target is not None:
        print(f"  {path}: {len(sats)} satellites in the "
              f"{h_target:.0f}+/-{h_tol:.0f} km / {inc_target:.0f}+/-{inc_tol:.0f} deg shell")
    if not sats:
        raise SystemExit(
            f"ERROR: no valid TLEs found in {path} "
            f"({len(lines)} lines). The file is probably a CelesTrak error or "
            f"rate-limit page - inspect it with 'head {path}'. Re-download "
            f"(wait ~2 h if rate-limited) or use the supplemental endpoint:\n"
            f"  https://celestrak.org/NORAD/elements/supplemental/sup-gp.php"
            f"?FILE=starlink&FORMAT=tle")
    step = max(1, len(sats)//nsample)
    out = sats[::step][:nsample]
    _SAT_CACHE[_key] = out
    return out

def collect_passes(h, inc, tle_file=None):
    """Return list of pass dicts with sampled (t, elev, rtt) and derived stats."""
    if tle_file:
        sat_list = load_real_sats(tle_file, ARGS.nsample,
                                  h_target=h, inc_target=inc)
    else:
        # synthetic fallback: spread planes so 7 days give diverse geometry
        sat_list = []
        for raan in (0.0, 60.0, 120.0):
            l1, l2 = make_tle("SYN", h, inc, raan=raan)
            sat_list.append(EarthSatellite(l1, l2, "SYN", ts))
    passes = []
    for sat in sat_list:
        times, events = sat.find_events(gw, t0, t1, altitude_degrees=MASK)
        rise = None; culm = None
        for t, ev in zip(times, events):
            if ev == 0: rise = t; culm = None
            elif ev == 1: culm = t
            elif ev == 2 and rise is not None and culm is not None:
                tt = ts.tt_jd(np.linspace(rise.tt, t.tt, 400))
                topo = (sat - gw).at(tt)
                alt, _, dist = topo.altaz()
                el = alt.degrees; d = dist.km
                sec = (tt.tt - culm.tt)*86400.0     # s relative to culmination
                i_c = int(np.argmax(el))
                # usable-pass criterion: ignore passes that merely graze the
                # mask (culmination below MIN_CULM) - they set almost at
                # culmination and are not realistic relocation scenarios.
                if float(el[i_c]) < MIN_CULM:
                    rise = None; culm = None
                    continue
                passes.append(dict(
                    sec=sec, el=el, rtt=rtt_of_range(d), d=d,
                    max_el=float(el[i_c]),
                    M=float((t.tt - culm.tt)*86400.0),
                    duration=float((t.tt - rise.tt)*86400.0),
                    rtt_edge=float(rtt_of_range(d[-1])),
                    rtt_floor=float(rtt_of_range(d[i_c])),
                ))
                rise = None; culm = None
    return passes

def fixed_point(p):
    """Latest safe trigger on the descending arc: t_dl - t = k RTT(t) + Tproc."""
    sec, rtt = p["sec"], p["rtt"]
    desc = sec >= 0
    s, r = sec[desc], rtt[desc]
    tdl = p["M"]
    g = (tdl - s) - (K*r + TPROC)           # residual margin minus delta_min
    idx = np.where(g <= 0)[0]
    if len(idx) == 0 or idx[0] == 0:
        return None
    i = idx[0]
    # linear interpolation for the crossing
    f = g[i-1] / (g[i-1] - g[i])
    t_star = s[i-1] + f*(s[i]-s[i-1])
    dmin_star = tdl - t_star
    return t_star, dmin_star

print("collecting passes ...")

# Determine the propagation window from the snapshot before any pass detection.
_epochs = []
for _name, _o in ORBITS.items():
    _f = TLE_FILES.get(_name)
    if _f:
        for _s in load_real_sats(_f, ARGS.nsample, h_target=_o["h"], inc_target=_o["inc"]):
            _epochs.append(_s.epoch.tt)
if not _epochs:                       # synthetic fallback: use today
    _n = datetime.now(timezone.utc)
    _epochs = [ts.utc(_n.year, _n.month, _n.day).tt]
_set_window(_epochs)

DATA = {name: collect_passes(o["h"], o["inc"], TLE_FILES.get(name))
        for name, o in ORBITS.items()}
for name in ORBITS:
    print(f"{name}: {'REAL TLEs: '+TLE_FILES[name] if TLE_FILES.get(name) else 'synthetic TLEs'}")
for name, ps in DATA.items():
    leads = [fixed_point(p)[1] for p in ps if fixed_point(p)]
    Ms = [p["M"] for p in ps]
    if not ps or not leads:
        raise SystemExit(f"ERROR: {name} produced no usable passes over the "
                         f"window - check its TLE file (see sizes with ls -la).")
    print(f"{name}: {len(ps)} passes, edge RTT ~{1e3*np.median([p['rtt_edge'] for p in ps]):.1f} ms, "
          f"lead {1e3*np.median(leads):.0f} ms, M {min(Ms):.0f}-{max(Ms):.0f} s")

# analytic slant-range curve (eq. 1) for panel 3a
def slant(h, el_deg, Re=6371.0):
    s = Re*np.sin(np.radians(el_deg))
    return -s + np.sqrt(s**2 + h**2 + 2*Re*h)

# batch / M-G-1 models -------------------------------------------------------
def dmin_batch(N, mu, rtt_edge):
    return K*rtt_edge + N/mu

def T_soj(rho, mu, cs2):
    return 1.0/mu + rho*(1+cs2)/(2*mu*(1-rho))

def dmin_mg1(N, mu, M, rtt_edge, cs2=1.0):
    rho = N/(mu*M)
    out = np.full_like(np.asarray(N, float), np.inf)
    ok = rho < 1
    out[ok] = K*rtt_edge + T_soj(rho[ok], mu, cs2)
    return out

def rho_star(mu, M, rtt_edge, cs2=1.0, Lp=1.0):
    tau = mu*(M - K*rtt_edge)
    return 2*(tau-1)/(Lp*(1+cs2) + 2*(tau-1))

# representative passes -------------------------------------------------------
def pick(ps, target_el):
    return min(ps, key=lambda p: abs(p["max_el"]-target_el))

p_rep  = pick(DATA["Starlink-550"], 78.0)     # Fig 2
p_graz = min(DATA["Starlink-550"], key=lambda p: p["M"])   # tightest margin
print(f"rep pass: max el {p_rep['max_el']:.0f} deg, dur {p_rep['duration']/60:.1f} min; "
      f"grazing M = {p_graz['M']:.1f} s")

# ---------------------------------------------------------------------------
# Plotting (clean styling: no suptitles, compact legends, constrained layout)
# ---------------------------------------------------------------------------
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6,
    "figure.dpi": 220, "lines.linewidth": 1.1, "axes.titlepad": 3,
})

def orbit_handles():
    return [Line2D([], [], color=o["color"], lw=1.4, label=n)
            for n, o in ORBITS.items()]

# ------------------------------ Fig 2 ---------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 1.95), constrained_layout=True)
a = ax[0]
a.plot(p_rep["sec"], 1e3*p_rep["rtt"]/2, color="tab:red")
a.set_xlabel("time relative to culmination [s]")
a.set_ylabel("one-way delay [ms]", color="tab:red")
a.tick_params(axis="y", labelcolor="tab:red")
a2 = a.twinx()
a2.plot(p_rep["sec"], p_rep["el"], "--", color="tab:blue", lw=0.9)
a2.set_ylabel("elevation [deg]", color="tab:blue")
a2.tick_params(axis="y", labelcolor="tab:blue")
a.set_title("(a) delay profile over the pass")
a.text(0.02, 0.96, f"max elev {p_rep['max_el']:.0f}\u00b0, "
       f"{p_rep['duration']/60:.1f} min", transform=a.transAxes,
       va="top", fontsize=6)
b = ax[1]
o = np.argsort(p_rep["el"])
b.plot(p_rep["el"][o], 1e3*p_rep["rtt"][o]/2, color="tab:green")
b.set_xlabel("elevation [deg]"); b.set_ylabel("one-way delay [ms]")
b.set_title("(b) delay vs elevation")
fig.savefig("feeder_delay_pass.png"); plt.close(fig)

# ------------------------------ Fig 3 ---------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(7.0, 3.80), constrained_layout=True)
a = ax[0, 0]
el = np.linspace(MASK, 90, 200)
for name, o in ORBITS.items():
    a.semilogy(el, 1e3*slant(o["h"], el)/C, color=o["color"])
a.set_xlabel("elevation [deg]"); a.set_ylabel("one-way delay [ms]")
a.set_title("(a) delay vs elevation: altitude trade")
a.legend(handles=orbit_handles(), loc="upper right")

b = ax[0, 1]
for name, o in ORBITS.items():
    ps = DATA[name]
    me = [p["max_el"] for p in ps]
    b.plot(me, [1e3*p["rtt_edge"] for p in ps], "o", ms=2.6, color=o["color"])
    b.plot(me, [1e3*p["rtt_floor"] for p in ps], "s", ms=2.6, mfc="none",
           mew=0.7, color=o["color"])
b.set_xlabel("pass max elevation [deg]"); b.set_ylabel("feeder RTT [ms]")
b.set_title("(b) edge RTT flat; floor rises when grazing")
style = [Line2D([], [], marker="o", ls="", color="k", ms=3, label="edge"),
         Line2D([], [], marker="s", ls="", color="k", ms=3, mfc="none",
                label="floor")]
b.legend(handles=orbit_handles()+style, ncol=2, fontsize=5.5,
         loc="center right")

c = ax[1, 0]
sec, tdl = p_rep["sec"], p_rep["M"]
desc = sec >= 0
c.semilogy(sec[desc], np.maximum(tdl - sec[desc], 1e-4), color="tab:orange",
           label="residual margin $t_{dl}-t$")
c.semilogy(sec[desc], K*p_rep["rtt"][desc] + TPROC, color="tab:purple",
           label="$\\delta_{\\mathrm{req}}(t)$")
tstar, lead = fixed_point(p_rep)
c.axvline(tstar, ls=":", color="k", lw=0.8)
c.annotate(f"$t^*$: {1e3*lead:.0f} ms before set",
           xy=(tstar, lead), xytext=(0.30*tdl, 3),
           arrowprops=dict(arrowstyle="->", lw=0.6), fontsize=6.5)
c.set_xlabel("time after culmination [s]"); c.set_ylabel("seconds [log]")
c.set_title("(c) fixed point on the descending arc")
c.legend(loc="lower left")

d = ax[1, 1]
for name, o in ORBITS.items():
    ps = DATA[name]
    me, req, avail = [], [], []
    for p in ps:
        fp = fixed_point(p)
        if fp:
            me.append(p["max_el"]); req.append(fp[1]); avail.append(p["M"])
    d.semilogy(me, req, "^", ms=2.6, color=o["color"])
    d.semilogy(me, avail, "v", ms=2.6, mfc="none", mew=0.7, color=o["color"])
d.set_xlabel("pass max elevation [deg]"); d.set_ylabel("time [s]")
d.set_title("(d) required lead vs available margin")
style = [Line2D([], [], marker="^", ls="", color="k", ms=3, label="required"),
         Line2D([], [], marker="v", ls="", color="k", ms=3, mfc="none",
                label="margin")]
d.legend(handles=orbit_handles()+style, ncol=2, fontsize=5.5,
         loc="center right")
fig.savefig("delta_min_analysis.png"); plt.close(fig)

# ------------------------------ Fig 4 ---------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(7.0, 3.80), constrained_layout=True)
Mg, rttg = p_graz["M"], p_graz["rtt_edge"]
a = ax[0, 0]
N = np.logspace(0, 6, 300)
for mu, lsty in ((100, "--"), (500, "-"), (5000, ":")):
    a.loglog(N, dmin_batch(N, mu, rttg), lsty, color="tab:red",
             label=f"$\\mu$={mu}/s")
a.axhline(Mg, color="k", lw=0.8)
a.text(8e5, Mg*0.55, f"grazing margin {Mg:.0f} s", fontsize=6,
       ha="right", va="top")
a.set_xlabel("sessions N"); a.set_ylabel("$\\delta_{\\mathrm{req}}^{batch}$ [s]")
a.set_title("(a) batch $\\delta_{\\mathrm{req}}$ meets the margin at $N_{\\max}$")
a.legend(loc="upper left")

b = ax[0, 1]
mus = np.logspace(np.log10(50), np.log10(5000), 120)
Ns  = np.logspace(0, 6, 120)
MU, NN = np.meshgrid(mus, Ns)
FRAC = np.minimum(1.0, MU*(Mg - K*rttg)/NN)
pc = b.pcolormesh(MU, NN, FRAC, cmap="RdYlGn", vmin=0, vmax=1, shading="auto")
b.set_xscale("log"); b.set_yscale("log")
b.set_xlabel("$\\mu$ [PFCP est./s]"); b.set_ylabel("sessions N")
b.set_title("(b) feasible fraction, grazing pass")
cb = fig.colorbar(pc, ax=b, shrink=0.92)
cb.set_label("continuity fraction", fontsize=6)
cb.ax.tick_params(labelsize=6)

c = ax[1, 0]
for name, o in ORBITS.items():
    ps = sorted(DATA[name], key=lambda p: p["max_el"])
    me = [p["max_el"] for p in ps]
    nmax = [MU_BASE*(p["M"] - K*p["rtt_edge"]) for p in ps]
    c.semilogy(me, nmax, "o-", ms=2.4, lw=0.8, color=o["color"])
c.set_xlabel("pass max elevation [deg]"); c.set_ylabel("$N_{\\max}$ [log]")
c.set_title(f"(c) capacity vs geometry ($\\mu$={MU_BASE:.0f}/s)")
c.legend(handles=orbit_handles(), loc="lower right")

d = ax[1, 1]
N = np.logspace(2, 7, 300)
for (name, mu, lsty) in (("Starlink-550", 2000, ":"), ("Starlink-550", 500, "-"),
                         ("OneWeb-1200", 500, "--")):
    p = min(DATA[name], key=lambda q: q["M"])
    nmax = mu*(p["M"] - K*p["rtt_edge"])
    d.semilogx(N, np.minimum(1, nmax/N), lsty, color=ORBITS[name]["color"],
               label=f"{name.split('-')[0]} graz., $\\mu$={mu}")
d.set_xlabel("sessions N"); d.set_ylabel("continuity fraction")
d.set_title("(d) continuity fraction under a storm")
d.legend(loc="lower left")
fig.savefig("load_feasibility.png"); plt.close(fig)

# ------------------------------ Fig 5 ---------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(7.0, 3.80), constrained_layout=True)
a = ax[0, 0]
rho = np.linspace(0.01, 0.999, 400)
for cs2, lsty in ((0, ":"), (1, "-"), (4, "--")):
    a.semilogy(rho, [T_soj(r, MU_BASE, cs2) for r in rho], lsty,
               label=f"$C_s^2$={cs2}")
a.axhline(Mg, color="k", lw=0.8)
a.text(0.97, Mg*0.35, f"grazing margin {Mg:.0f} s", fontsize=6,
       ha="right", va="top")
a.set_xlabel("utilization $\\rho$"); a.set_ylabel("sojourn [s, log]")
a.set_title(f"(a) M/G/1 sojourn ($\\mu$={MU_BASE:.0f}/s)")
a.legend(loc="upper left")

b = ax[0, 1]
N = np.logspace(0, np.log10(0.999*MU_BASE*Mg), 400)
b.loglog(N, dmin_batch(N, MU_BASE, rttg), color="tab:red", label="batch")
for cs2, lsty in ((1, "-"), (4, "--")):
    b.loglog(N, dmin_mg1(N, MU_BASE, Mg, rttg, cs2), lsty, color="tab:green",
             label=f"M/G/1, $C_s^2$={cs2}")
b.set_xlabel("sessions N"); b.set_ylabel("$\\delta_{\\mathrm{req}}$ [s]")
b.set_title("(b) spreading holds $\\delta_{\\mathrm{req}}$ at the ms floor")
b.legend(loc="upper left")

c = ax[1, 0]
for name, o in ORBITS.items():
    ps = sorted(DATA[name], key=lambda p: p["max_el"])
    me = [p["max_el"] for p in ps]
    c.plot(me, [rho_star(MU_BASE, p["M"], p["rtt_edge"]) for p in ps],
           "-", lw=1.0, color=o["color"])
    c.plot(me, [rho_star(MU_BASE, p["M"], p["rtt_edge"], Lp=np.log(100))
                for p in ps], "--", lw=1.0, color=o["color"])
c.set_xlabel("pass max elevation [deg]")
c.set_ylabel("critical utilization $\\rho^\\ast$")
c.set_ylim(0.995, 1.0006)
c.set_title("(c) $\\rho^\\ast$ vs geometry: mean and 99th pct")
style = [Line2D([], [], color="k", ls="-", label="mean, Eq. (9)"),
         Line2D([], [], color="k", ls="--", label="99th pct, Eq. (10)")]
c.legend(handles=orbit_handles()+style, ncol=2, fontsize=5.5,
         loc="lower right")

d = ax[1, 1]
mus = np.logspace(np.log10(300), np.log10(5000), 200)
N0 = 5000
d.loglog(mus, [dmin_batch(N0, m, rttg) for m in mus], color="tab:red",
         label="batch")
d.loglog(mus, [dmin_mg1(np.array([N0]), m, Mg, rttg, 1.0)[0] for m in mus],
         color="tab:green", label="M/G/1 spread")
d.set_xlabel("$\\mu$ [1/s]"); d.set_ylabel("$\\delta_{\\mathrm{req}}$ [s, log]")
d.set_title(f"(d) spreading collapses $\\delta_{{\\mathrm{{req}}}}$ (N={N0}, grazing)")
d.legend(loc="upper right")
fig.savefig("mg1_refinement.png"); plt.close(fig)

# --------------------------- headline numbers -------------------------------
print("\n=== headline numbers ===")
tstar, lead = fixed_point(p_rep)
print(f"rep 550 pass: culm {p_rep['max_el']:.0f} deg, dur {p_rep['duration']/60:.1f} min, "
      f"floor 1-way {1e3*p_rep['rtt_floor']/2:.1f} ms, edge 1-way {1e3*p_rep['rtt_edge']/2:.1f} ms "
      f"(RTT {1e3*p_rep['rtt_edge']:.1f} ms), slant {min(p_rep['d']):.0f}-{max(p_rep['d']):.0f} km")

# Effective altitude of the representative pass, inverted from Eq. (1) of the
# paper (spherical, Re = 6371 km).  Reported so the quoted per-pass slant
# ranges can be checked against the analytic formula.
def _slant_sph(h, eps_deg, Re=6371.0):
    s = Re*np.sin(np.radians(eps_deg))
    return -s + np.sqrt(s**2 + h**2 + 2*Re*h)

_lo, _hi, _target = 200.0, 1500.0, max(p_rep["d"])
for _ in range(200):                     # bisection; no SciPy dependency
    _mid = 0.5*(_lo+_hi)
    if _slant_sph(_mid, MASK) < _target: _lo = _mid
    else: _hi = _mid
print(f"  rep pass effective altitude (Eq.1, Re=6371): {0.5*(_lo+_hi):.0f} km")
for name in ORBITS:
    ps = DATA[name]
    leads = [fixed_point(p)[1] for p in ps if fixed_point(p)]
    Ms = sorted(p["M"] for p in ps)
    edges = [p["rtt_edge"] for p in ps]
    ratio = max(l/m for l, m in zip(
        [fixed_point(p)[1] for p in ps if fixed_point(p)],
        [p["M"] for p in ps if fixed_point(p)]))
    print(f"{name}: edge RTT {1e3*np.median(edges):.1f} ms, lead {1e3*min(leads):.0f}-"
          f"{1e3*max(leads):.0f} ms, M {Ms[0]:.0f}-{Ms[-1]:.0f} s, worst lead/M {100*ratio:.2f}%")
pg = p_graz

print(
    f"grazing 550: M={pg['M']:.1f}s  "
    f"Nmax(mu=100)={100*(pg['M']-K*pg['rtt_edge']):.0f}  "
    f"batch(5000,500)={dmin_batch(5000,500,pg['rtt_edge']):.2f}s  "
    f"mg1(5000,500)={dmin_mg1(np.array([5000.]), 500, pg['M'], pg['rtt_edge'])[0]:.4f}s"
)
      
best550 = max(DATA['Starlink-550'], key=lambda p: p['M'])
print(f"overhead 550: Nmax(mu=500) = {500*(best550['M']-K*best550['rtt_edge']):.0f}")
best1200 = max(DATA['OneWeb-1200'], key=lambda p: p['M'])
print(f"overhead 1200: Nmax(mu=500) = {500*(best1200['M']-K*best1200['rtt_edge']):.0f}")
     
