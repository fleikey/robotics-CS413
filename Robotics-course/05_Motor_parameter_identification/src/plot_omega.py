import os
import glob
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = "motor_data"

def read_data_file(filepath):
    positions, times = [], []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) == 2:
                positions.append(int(parts[0]))
                times.append(int(parts[1]))
    return np.array(positions), np.array(times)

def read_battery(filepath):
    with open(filepath, 'r') as f:
        line = f.read().strip()
    return float(line.split(':')[1].strip())

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

battery_files = glob.glob(os.path.join(DATA_DIR, "wheel_*_battery.txt"))
wheel_ids = sorted(set(
    int(os.path.basename(f).split('_')[1])
    for f in battery_files
))

colors = ['#378ADD', '#1D9E75', '#E24B4A', '#D85A30', '#7F77DD']

all_wheel_data = {}
for wid in wheel_ids:
    battery_file = os.path.join(DATA_DIR, f"wheel_{wid}_battery.txt")
    battery_v = read_battery(battery_file)

    files = glob.glob(os.path.join(DATA_DIR, f"wheel_{wid}_v_*.txt"))
    points = []
    for fp in files:
        fname = os.path.basename(fp)
        try:
            v_str = fname.replace(f"wheel_{wid}_v_", "").replace(".txt", "")
            voltage_pct = int(v_str)
        except ValueError:
            continue
        positions, times = read_data_file(fp)
        if len(positions) < 4:
            continue
        omega = compute_omega(positions, times)
        U_actual = (voltage_pct / 100.0) * battery_v
        points.append((U_actual, omega))

    points.sort(key=lambda x: x[0])
    all_wheel_data[wid] = {
        'U': [p[0] for p in points],
        'omega': [p[1] for p in points],
        'battery_v': battery_v
    }

plt.figure(figsize=(12, 6))
for i, wid in enumerate(wheel_ids):
    d = all_wheel_data[wid]
    color = colors[i % len(colors)]
    plt.scatter(d['U'], d['omega'], color=color, s=30, zorder=3)
    plt.plot(d['U'], d['omega'], color=color, linewidth=1.2, alpha=0.7, label=f'Колесо {wid}')

plt.axhline(0, color='gray', linewidth=0.8, linestyle=':')
plt.axvline(0, color='gray', linewidth=0.8, linestyle=':')
plt.xlabel('Напряжение на моторе U (В)', fontsize=12)
plt.ylabel('Угловая скорость ω (°/с)', fontsize=12)
plt.title('Все колёса — зависимость ω от U', fontsize=13)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("omega_all_wheels.png", dpi=150, bbox_inches='tight')
print("Сохранено: omega_all_wheels.png")
plt.show()

