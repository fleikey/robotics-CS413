import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

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

def load_wheel_data(wheel_id):
    battery_file = os.path.join(DATA_DIR, f"wheel_{wheel_id}_battery.txt")
    if not os.path.exists(battery_file):
        print(f"Нет файла батареи для колеса {wheel_id}")
        return None

    battery_v = read_battery(battery_file)

    pattern = os.path.join(DATA_DIR, f"wheel_{wheel_id}_v_*.txt")
    files = glob.glob(pattern)
    if not files:
        print(f"Нет файлов данных для колеса {wheel_id}")
        return None

    results = []
    for fp in files:
        fname = os.path.basename(fp)
        try:
            v_str = fname.replace(f"wheel_{wheel_id}_v_", "").replace(".txt", "")
            voltage_pct = int(v_str)
        except ValueError:
            continue

        positions, times = read_data_file(fp)
        if len(positions) < 4:
            continue

        omega = compute_omega(positions, times)
        U_actual = (voltage_pct / 100.0) * battery_v
        coeff = U_actual / omega if omega != 0 else None

        results.append({
            'voltage_pct': voltage_pct,
            'U_actual': U_actual,
            'omega': omega,
            'coeff': coeff,
            'battery_v': battery_v,
            'positions': positions,
            'times': times
        })

    results.sort(key=lambda x: x['voltage_pct'])
    return results

def plot_wheel(wheel_id, results, axs):
    battery_v = results[0]['battery_v']
    voltages = [r['voltage_pct'] for r in results]
    omegas   = [r['omega'] for r in results]
    U_actual = [r['U_actual'] for r in results]
    coeffs   = [r['coeff'] for r in results if r['coeff'] is not None]
    coeff_vs = [r['voltage_pct'] for r in results if r['coeff'] is not None]

    ax1 = axs[0]
    ax1.scatter(voltages, omegas, color='#378ADD', s=40, zorder=3, label='данные')

    if len(voltages) > 2:
        coeffs_fit = np.polyfit(voltages, omegas, 1)
        x_fit = np.linspace(min(voltages), max(voltages), 200)
        y_fit = np.polyval(coeffs_fit, x_fit)
        ax1.plot(x_fit, y_fit, color='#E24B4A', linewidth=1.5,
                 linestyle='--', label=f'аппр.: k={coeffs_fit[0]:.2f}')

    ax1.axhline(0, color='gray', linewidth=0.8, linestyle=':')
    ax1.axvline(0, color='gray', linewidth=0.8, linestyle=':')
    ax1.set_xlabel('Напряжение ШИМ (%)', fontsize=10)
    ax1.set_ylabel('ω (°/с)', fontsize=10)
    ax1.set_title(f'Колесо {wheel_id} — ω vs U%  (акк. {battery_v:.2f} В)', fontsize=11)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2 = axs[1]
    valid_mask = [r['coeff'] is not None for r in results]
    cv = [r['voltage_pct'] for r in results if r['coeff'] is not None]
    cc = [r['coeff'] for r in results if r['coeff'] is not None]

    ax2.bar(cv, cc, color='#1D9E75', width=3.5, zorder=3)
    if cc:
        avg = np.mean(cc)
        ax2.axhline(avg, color='#E24B4A', linewidth=1.5,
                    linestyle='--', label=f'среднее={avg:.5f}')
        ax2.legend(fontsize=9)

    ax2.set_xlabel('Напряжение ШИМ (%)', fontsize=10)
    ax2.set_ylabel('U/ω (В·с/°)', fontsize=10)
    ax2.set_title(f'Колесо {wheel_id} — коэффициент U/ω', fontsize=11)
    ax2.grid(True, alpha=0.3)


def main():
    battery_files = glob.glob(os.path.join(DATA_DIR, "wheel_*_battery.txt"))
    wheel_ids = sorted(set(
        int(os.path.basename(f).split('_')[1])
        for f in battery_files
    ))

    if not wheel_ids:
        print(f"Не найдено данных в папке '{DATA_DIR}'")
        return

    print(f"Найдены колёса: {wheel_ids}")

    n = len(wheel_ids)
    fig, all_axs = plt.subplots(n, 2, figsize=(14, 5 * n))
    fig.suptitle('Характеристики моторов — U/ω', fontsize=14, fontweight='bold', y=1.01)

    if n == 1:
        all_axs = [all_axs]  # чтобы всегда был список строк

    for i, wid in enumerate(wheel_ids):
        results = load_wheel_data(wid)
        if results is None:
            continue
        plot_wheel(wid, results, all_axs[i])

    plt.tight_layout()
    out_path = "motor_graphs.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"График сохранён: {out_path}")
    plt.show()

    print("\n=== Средние коэффициенты U/ω (В·с/°) ===")
    for wid in wheel_ids:
        results = load_wheel_data(wid)
        if not results:
            continue
        coeffs = [r['coeff'] for r in results if r['coeff'] is not None]
        if coeffs:
            print(f"  Колесо {wid}: {np.mean(coeffs):.5f} В·с/°")

if __name__ == '__main__':
    main()