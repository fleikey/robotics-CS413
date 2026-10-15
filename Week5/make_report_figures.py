"""Builds the figures and the per-PWM table for report.md from trik_data_bat.txt.

Run:  python make_report_figures.py   (needs numpy, scipy, matplotlib)
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from scipy.integrate import odeint

DATA_FILE = 'trik_data_bat.txt'          # columns: power %, encL deg (E4), encR deg (E3), time ms, battery V
OUT_DIR = 'report_figs'
HI = 50                                  # |PWM| >= HI % is the range used to fit k_e
STEP_POWER = 100                         # run shown as the step response
r_wheel, W = 0.0375, 0.194               # wheel radius and track width from the Week 4 odometry code, m

os.makedirs(OUT_DIR, exist_ok=True)

# ---------- load and split into runs ----------
power_all, encL_all, encR_all, time_all, bat_all = np.loadtxt(DATA_FILE).T
starts = np.r_[0, np.flatnonzero(np.diff(power_all) != 0) + 1, len(power_all)]
runs = []
for a, b in zip(starts[:-1], starts[1:]):
    runs.append({'power': power_all[a],
                 'time': (time_all[a:b] - time_all[a]) / 1000,          # s
                 'L': np.deg2rad(encL_all[a:b]),                        # rad
                 'R': np.deg2rad(encR_all[a:b]),                        # rad
                 'U': power_all[a] / 100 * bat_all[a:b].mean()})        # V

# ---------- fit theta(t) = w_ss (t - T_m + T_m e^{-t/T_m}) to every run ----------
def model(t, speed, T_m):
    return speed * t - speed * T_m + speed * T_m * np.exp(-t / T_m)

def fit_run(t, ang):
    popt, _ = optimize.curve_fit(model, t, ang, p0=[ang[-1] / t[-1], 0.2],
                                 bounds=([-np.inf, 1e-3], [np.inf, 5]))
    return popt

pct = np.array([r['power'] for r in runs])
U = np.array([r['U'] for r in runs])
fit = {}
for wh in ('L', 'R'):
    w, tm = np.full(len(runs), np.nan), np.full(len(runs), np.nan)
    for i, r in enumerate(runs):
        if abs(r[wh][-1]) < 1:                                           # did not move
            continue
        w[i], tm[i] = fit_run(r['time'], r[wh])
    fit[wh] = {'w': w, 'Tm': tm}

# ---------- k_e (line through origin on |PWM| >= HI) and dead zone ----------
hi = np.abs(pct) >= HI
summary = {}
for wh in ('L', 'R'):
    w = fit[wh]['w']
    k_e = np.sum(U[hi] ** 2) / np.sum(U[hi] * w[hi])                    # least squares for w = U / k_e
    k_e_fwd = np.sum(U[hi & (pct > 0)] ** 2) / np.sum(U[hi & (pct > 0)] * w[hi & (pct > 0)])
    k_e_rev = np.sum(U[hi & (pct < 0)] ** 2) / np.sum(U[hi & (pct < 0)] * w[hi & (pct < 0)])
    # dead zone: extrapolate the two lowest moving points on each side to w = 0
    dz = []
    for sgn in (1, -1):
        idx = [i for i in np.argsort(np.abs(U)) if np.sign(U[i]) == sgn and not np.isnan(w[i])][:2]
        (u1, w1), (u2, w2) = [(U[i], w[i]) for i in idx]
        dz.append(abs(u1 - w1 * (u2 - u1) / (w2 - w1)))
    summary[wh] = {'k_e': k_e, 'k_e_fwd': k_e_fwd, 'k_e_rev': k_e_rev,
                   'Tm': np.nanmedian(fit[wh]['Tm'][hi]), 'dz': max(dz)}

U_step = U[pct == 5][0]                                                  # smallest moving PWM step
dz = max(summary['L']['dz'], summary['R']['dz'])

# ---------- figure 1: w_ss vs U ----------
colors = {'L': '#2a6fdb', 'R': '#e0533d'}
fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
ax.axvspan(-dz, dz, color='0.75', alpha=0.6, label=f'dead zone, |U| < {dz:.2f} V (estimated)')
ax.axvspan(-U_step, U_step, color='0.85', alpha=0.4, label=f'below first PWM step, |U| < {U_step:.2f} V')
Ul = np.linspace(-11.5, 11.5, 2)
for wh in ('L', 'R'):
    s = summary[wh]
    ax.plot(U, fit[wh]['w'], 'o', color=colors[wh], ms=5, label=f'wheel {wh}, fitted $\\omega_{{ss}}$')
    ax.plot(Ul, Ul / s['k_e'], '--', color=colors[wh], lw=1.3,
            label=f'wheel {wh}: $\\omega = U/k_e$, $k_e$ = {s["k_e"]:.3f} V·s/rad')
ax.axhline(0, color='gray', lw=0.6); ax.axvline(0, color='gray', lw=0.6)
ax.set_xlabel('applied voltage U = PWM/100 · U_bat, V'); ax.set_ylabel('$\\omega_{ss}$, rad/s')
ax.set_title(f'Steady-state speed vs voltage ($k_e$ fitted on |PWM| ≥ {HI} %)')
ax.grid(alpha=0.3); ax.legend(fontsize=8, loc='upper left')
fig.tight_layout(); fig.savefig(f'{OUT_DIR}/omega_vs_U.png')

# ---------- figure 2: step response, measured vs simulated ----------
run = next(r for r in runs if r['power'] == STEP_POWER)
t_sim = np.linspace(0, run['time'][-1], 300)
fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
for wh in ('L', 'R'):
    s = summary[wh]
    motor = lambda x, t, k_e=s['k_e'], T_m=s['Tm']: [-x[0] / T_m + run['U'] / (T_m * k_e), x[0]]
    sim = odeint(motor, [0, 0], t_sim)[:, 1]
    ax.plot(run['time'], run[wh], 'o', color=colors[wh], ms=5, label=f'wheel {wh}, measured')
    ax.plot(t_sim, sim, '-', color=colors[wh], lw=1.5,
            label=f'wheel {wh}, model ($k_e$={s["k_e"]:.3f}, $T_m$={s["Tm"]:.3f} s)')
    s['step_err'] = np.max(np.abs(np.interp(run['time'], t_sim, sim) - run[wh]))
ax.set_xlabel('t, s'); ax.set_ylabel('θ, rad')
ax.set_title(f'Step response at PWM = {STEP_POWER} % (U = {run["U"]:.2f} V)')
ax.grid(alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(f'{OUT_DIR}/step_response.png')

# ---------- table ----------
fmt = lambda x, f: '–' if np.isnan(x) else format(x, f)
lines = ['| PWM, % | U, V | L: ω_ss, rad/s | L: T_m, s | R: ω_ss, rad/s | R: T_m, s |',
         '|---:|---:|---:|---:|---:|---:|']
for i in range(len(runs)):
    lines.append(f'| {pct[i]:.0f} | {U[i]:.2f} | {fmt(fit["L"]["w"][i], ".2f")} | {fmt(fit["L"]["Tm"][i], ".3f")}'
                 f' | {fmt(fit["R"]["w"][i], ".2f")} | {fmt(fit["R"]["Tm"][i], ".3f")} |')
open(f'{OUT_DIR}/table.md', 'w').write('\n'.join(lines) + '\n')

# ---------- numbers for the text ----------
for wh, s in summary.items():
    print(f'{wh}: k_e={s["k_e"]:.3f} (fwd {s["k_e_fwd"]:.3f}, rev {s["k_e_rev"]:.3f}) V*s/rad, '
          f'T_m={s["Tm"]:.3f} s, dead zone {s["dz"]:.2f} V, step max err {s["step_err"]:.2f} rad')
for p in (100, 50, -50, -100):
    i = np.flatnonzero(pct == p)[0]
    wL, wR = fit['L']['w'][i], fit['R']['w'][i]
    yaw = r_wheel * (wR - wL) / W
    print(f'PWM {p:4d}: wL={wL:6.2f} wR={wR:6.2f} diff={100 * (wL - wR) / ((wL + wR) / 2):+5.1f} %  '
          f'yaw rate={np.degrees(yaw):+5.1f} deg/s  v={r_wheel * (wL + wR) / 2:.3f} m/s')
lin_err = [(pct[i], 100 * (fit['L']['w'][i] - U[i] / summary['L']['k_e']) / fit['L']['w'][i])
           for i in range(len(runs)) if pct[i] in (10, 20, 30, -10, -20, -30)]
print('linear model error at low PWM (L):', [(int(p), round(e)) for p, e in lin_err])
