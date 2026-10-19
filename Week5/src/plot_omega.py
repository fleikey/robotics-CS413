import os
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "..", "trik_data_bat.txt")
OUT_DIR = os.path.join(HERE, "..", "report_figs")
WHEELS = {1: ("Wheel 1 (left, E4)", 1), 2: ("Wheel 2 (right, E3)", 2)}   # wheel id -> (name, encoder column)
HI = 50                                   # |PWM| >= HI % is used to fit k_e
colors = ['#378ADD', '#1D9E75']

def read_runs(filepath):
    data = np.loadtxt(filepath)
    runs = []
    for pwm in np.unique(data[:, 0]):
        runs.append(data[data[:, 0] == pwm])
    return runs

def compute_omega(positions, times):
    n = len(positions)
    if n < 4:
        return 0.0
    start = int(n * 0.4)
    dp = positions[-1] - positions[start]
    dt = (times[-1] - times[start]) / 1000.0
    if dt == 0:
        return 0.0
    return dp / dt

def fit_k_e(U, omega):
    return np.sum(U * U) / np.sum(U * omega)

def dead_zone(U, omega):
    moved = omega != 0
    pos = np.flatnonzero(moved & (U > 0))[:2]     # two smallest positive voltages
    neg = np.flatnonzero(moved & (U < 0))[-2:]    # two smallest negative voltages
    edges = []
    for i, j in (pos, neg):
        edges.append(abs(U[i] - omega[i] * (U[j] - U[i]) / (omega[j] - omega[i])))
    return max(edges)

runs = read_runs(DATA_FILE)               # sorted by PWM
pct = np.array([run[0, 0] for run in runs])
U = np.array([run[0, 0] / 100.0 * run[:, 4].mean() for run in runs])   # actual voltage, V
hi = np.abs(pct) >= HI

plt.figure(figsize=(12, 6))
dead_zones = []
for n, wid in enumerate(sorted(WHEELS)):
    name, col = WHEELS[wid]
    omega = np.array([compute_omega(run[:, col], run[:, 3]) for run in runs])   # °/s

    k_deg = fit_k_e(U[hi], omega[hi])     # V·s/°
    k_e = k_deg * 180 / np.pi             # V·s/rad
    dz = dead_zone(U, omega)
    dead_zones.append(dz)

    plt.scatter(U, omega, color=colors[n], s=30, zorder=3)
    plt.plot(U, omega, color=colors[n], linewidth=1.2, alpha=0.7, label=name)
    plt.plot(U, U / k_deg, '--', color=colors[n], linewidth=1.3,
             label=f'{name}: ω = U/k_e, k_e = {k_e:.3f} V·s/rad')
    print(f"  Wheel {wid}: k_e = {k_e:.3f} V·s/rad ({k_deg:.5f} V·s/°), dead zone ≈ {dz:.2f} V")

U_step = np.min(np.abs(U[U != 0]))        # voltage of the smallest PWM step
plt.axvspan(-U_step, U_step, color='0.85', alpha=0.5, label=f'below first PWM step, |U| < {U_step:.2f} V')
plt.axvspan(-max(dead_zones), max(dead_zones), color='0.65', alpha=0.6,
            label=f'dead zone, |U| < {max(dead_zones):.2f} V (estimated)')

plt.axhline(0, color='gray', linewidth=0.8, linestyle=':')
plt.axvline(0, color='gray', linewidth=0.8, linestyle=':')
plt.xlabel('Motor voltage U = PWM/100 · U_bat (V)', fontsize=12)
plt.ylabel('Angular velocity ω (°/s)', fontsize=12)
plt.title(f'All wheels — ω vs U  (k_e fitted on |PWM| ≥ {HI} %)', fontsize=13)
plt.legend(fontsize=9, loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
os.makedirs(OUT_DIR, exist_ok=True)
out_path = os.path.join(OUT_DIR, "omega_all_wheels.png")
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"Saved: {out_path}")
