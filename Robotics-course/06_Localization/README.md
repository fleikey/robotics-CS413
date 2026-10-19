## 1. Lecture

### What localization means for a wheeled robot

Localization answers one question: **where is the robot right now?** — its position `(x, y)` and heading `φ` in a fixed world frame.

This week we use the simplest answer available on every wheeled robot: **odometry (dead reckoning)**. The robot never sees the world; it only counts how far each wheel has turned and integrates those increments into a pose. Everything later in the course — gyroscope fusion (Week 10), complementary filtering (Week 11), Kalman filtering (Week 12) — exists to fix what goes wrong here.

### Differential-drive odometry

For a robot with wheel radius `R` and track width `B` (distance between wheels), over one sampling step:

| Quantity | Formula |
|---|---|
| Left / right wheel travel | `dL = r · Δθ_L`, `dR = r · Δθ_R` (Δφ in **radians**) |
| Centre travel | `d = (dL + dR) / 2` |
| Heading change | `φ = (θ_R − θ_L) / B` |
| Position update | `x ← x + d · cos(φ)`, `y ← y + d · sin(φ)` |

TRIK encoders report **degrees** — convert before using the formulas. Measure `r` and `B` on your own robot; do not trust nominal values.

### Why the model and the robot disagree

Odometry is the robot's **belief**, not the truth. The errors are systematic and they accumulate:

- **Wheel slip** — the encoder turns, the robot does not move (or moves less).
- **Wrong `R` or `B`** — a 2 % error in `B` turns every 90° corner into a 88° or 92° corner, and the error grows with every turn.
- **Unequal wheels / motors** — the robot drifts even when commanded straight (recall your Week 5 motor parameters).
- **Heading error dominates** — a small error in `φ` early on becomes a large error in `(x, y)` later.

The simulator has none of these effects, which is exactly why comparing the two is useful.

### Reading

- Thrun, Burgard, Fox. *Probabilistic Robotics.* Ch. 5 — Robot Motion (odometry motion model).
- Siegwart, Nourbakhsh, Scaramuzza. *Introduction to Autonomous Mobile Robots.* Ch. 5 — Mobile Robot Localization.
- Freiburg SS23 and ETH AMR slides on motion models and localization (links in the Week 1 README).

---

## 2. Practical task — Lab 6

### Goal

Drive the trajectory of **the last two digits of your student ID** (as in Lab 1), log the robot's odometry **in the simulator and on the real robot**, and compare the two trajectories in Google Colab.

### Log format

Both runs must write a plain text file, one line per sample, **no header**, comma-separated:

```
x,y,time
0.00,0.00,0
1.27,0.03,50
...
```

- `x`, `y` — odometry position in **m**
- `time` — in **ms** since program start

Name the files `odometry_data_sim.txt` (simulator) and `odometry_data_real.txt` (real robot). Run the **same program** in both cases.

### Colab analysis

```python
from google.colab import files      # file work module
import numpy as np                  # array work module
import matplotlib.pyplot as plt     # data visualization

uploaded = files.upload()           # select BOTH txt files

x_s, y_s, t_s = np.loadtxt('odometry_data_sim.txt',  delimiter=',', unpack=True)
x_r, y_r, t_r = np.loadtxt('odometry_data_real.txt', delimiter=',', unpack=True)

# 1. Trajectories on one plot
plt.figure(figsize=(6, 6))
plt.plot(x_s, y_s, '--', label='model (simulator)')
plt.plot(x_r, y_r,       label='real robot (odometry)')
plt.plot(0, 0, 'ko', label='start')
plt.axis('equal'); plt.grid(True); plt.legend()
plt.xlabel('x, m'); plt.ylabel('y, m')
plt.title('Model vs real trajectory')
plt.show()

# 2. Error over time (simulator resampled onto the real-robot timestamps)
t_s, t_r = t_s - t_s[0], t_r - t_r[0]
xs_i = np.interp(t_r, t_s, x_s)
ys_i = np.interp(t_r, t_s, y_s)
err = np.hypot(x_r - xs_i, y_r - ys_i)

plt.plot(t_r / 1000, err)
plt.xlabel('time, s'); plt.ylabel('position error, m'); plt.grid(True)
plt.title('Model vs real position error')
plt.show()

print(f'Final odometry error (sim vs real): {err[-1]:.1f} m')
print(f'Max error: {err.max():.1f} m')
```

> If `loadtxt` fails, open the file and check for a header line, trailing commas, or `;` instead of `,`.

### Deliverables

Create a repo `CS413-Robotics/Lab6/<content>`:

1. **`trajectory_sim.qrs`** and **`trajectory_real.qrs`** — the programs used, with odometry logging.
2. **`odometry_data_sim.txt`** and **`odometry_data_real.txt`** — the raw logs.
3. **Colab notebook (`.ipynb`)** with both plots and the printed errors.
4. **Measured end point** — after the real run, measure the robot's actual final position with a tape and compare it to the last line of `odometry_data_real.txt`.
5. **3–6 sentences**: where does the real trajectory diverge from the model, which error source from the lecture explains it, and does the robot *know* it is wrong?# Localization
Nice presentation of the differential drive robot localization from ETH and Duckietown Project https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/Lectures/amod/AMOD_2020/20201019-02%20-%20ETHZ%20-%20Modeling.pdf
