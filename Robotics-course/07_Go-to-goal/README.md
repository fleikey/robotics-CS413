## 1. Lecture

### From "where am I?" to "get me there"

In Week 6 the robot learned to estimate its pose `(x, y, θ)` from odometry. This week it uses that estimate to **drive to a goal point** `(x_g, y_g)`. Chain several goals together and the robot can follow any shape you can describe with coordinates, including your student ID digits.

The controller is only as good as the pose estimate it is fed. Every odometry error from Week 6 shows up here as a missed waypoint.

### Go-to-goal controller

At every control step the robot computes where the goal is relative to itself:

| Quantity | Formula |
|---|---|
| Distance to goal | `ρ = √((x_g − x)² + (y_g − y)²)` |
| Bearing to goal | `θ_g = atan2(y_g − y, x_g − x)` |
| Heading error | `e_θ = wrap(θ_g − θ)` into `(−π, π]` |
| Linear velocity | `v = min(K_v · ρ, v_max)` |
| Angular velocity | `ω = K_θ · e_θ` |
| Wheel speeds | `v_R = v + ω·B/2`, `v_L = v − ω·B/2` |

When `ρ < ε` (the acceptance radius), the robot switches to the next waypoint.

**Always wrap the heading error.** Without `wrap()`, a goal slightly to the robot's right can make it spin almost a full circle the wrong way.

### Design choices that shape the trajectory

- **`K_θ` too low.** The robot swings wide arcs and overshoots corners.
- **`K_θ` too high.** The robot oscillates around the line to the goal.
- **Constant `v` instead of `K_v · ρ`.** The robot arrives fast, cannot turn in time, and cuts corners.
- **Large `ε`.** The robot switches to the next waypoint early, so sharp corners become rounded.
- **Turn-then-drive vs. drive-while-turning.** Stopping to rotate in place first gives sharper digits but slower runs.

### Reading

- Corke, Peter. *Robotics, Vision and Control (Python), 3rd ed.* Ch. 4 — Mobile Robot Vehicles, section "Moving to a Point".
- Egerstedt, Magnus. *Control of Mobile Robots* (Georgia Tech, Coursera / YouTube): go-to-goal behaviour lectures.
- Freiburg SS23 and ETH AMR slides on motion control (links in the Week 1 README).

---

## 2. Practical task — Lab 7

### Goal

Describe **the last two digits of your student ID** as a list of waypoint coordinates. Drive them with the go-to-goal controller, first in the TRIK Studio simulator, then on the real robot. Compare the planned path, the simulated trajectory and the real trajectory in Google Colab.

Example: ID ending in `17`, waypoints in cm:

```
digit 1: (0,0) → (0,40)
gap:     (0,40) → (20,40)
digit 7: (20,40) → (45,40) → (25,0)
```

### Log format

Both runs write a plain text file, one line per sample, **no header**, comma-separated:

```
x,y,time
```

- `x`, `y` — odometry position in **cm**
- `time` — in **ms** since program start

Name the files `odometry_data_sim.txt` and `odometry_data_real.txt`. Run the **same program** with the **same gains** in both cases.

### Colab analysis

```python
from google.colab import files      # file work module
import numpy as np                  # array work module
import matplotlib.pyplot as plt     # data visualization

uploaded = files.upload()           # select BOTH txt files

# Planned waypoints: copy them from your TRIK program
wp = np.array([[0, 0], [0, 40], [20, 40], [45, 40], [25, 0]])

x_s, y_s, t_s = np.loadtxt('odometry_data_sim.txt',  delimiter=',', unpack=True)
x_r, y_r, t_r = np.loadtxt('odometry_data_real.txt', delimiter=',', unpack=True)

# 1. Planned path vs simulated vs real
plt.figure(figsize=(6, 6))
plt.plot(wp[:, 0], wp[:, 1], 'k:o', label='planned waypoints')
plt.plot(x_s, y_s, '--', label='model (simulator)')
plt.plot(x_r, y_r,       label='real robot (odometry)')
plt.axis('equal'); plt.grid(True); plt.legend()
plt.xlabel('x, cm'); plt.ylabel('y, cm')
plt.title('Go-to-goal: planned vs model vs real')
plt.show()

# 2. How close did each run get to each waypoint?
def waypoint_miss(x, y, wp):
    return np.array([np.min(np.hypot(x - px, y - py)) for px, py in wp])

miss_s = waypoint_miss(x_s, y_s, wp)
miss_r = waypoint_miss(x_r, y_r, wp)
for i, (ms, mr) in enumerate(zip(miss_s, miss_r)):
    print(f'Waypoint {i} {tuple(wp[i])}: sim {ms:5.1f} cm | real {mr:5.1f} cm')

# 3. Run time
print(f'Run time: sim {(t_s[-1]-t_s[0])/1000:.1f} s | real {(t_r[-1]-t_r[0])/1000:.1f} s')
```

> The real-robot miss distances come from the robot's own odometry, so they show how well the **controller** worked, not where the robot **actually** went.

### Deliverables

Create a repo `CS413-Robotics/Lab7/<content>`:

1. **`go_to_goal_sim.qrs`** and **`go_to_goal_real.qrs`**: the programs with your waypoint list, gains `K_v`, `K_θ` and acceptance radius `ε`.
2. **`odometry_data_sim.txt`** and **`odometry_data_real.txt`**: the raw logs.
3. **Colab notebook (`.ipynb`)** containing the trajectory plot, the waypoint-miss table and the run times.
4. **Measured end point.** Measure the real robot's final position with a tape and compare it to the last waypoint and to the last line of `odometry_data_real.txt`.
5. **3–6 sentences** answering two questions. Which corners were cut or overshot, and which gain or `ε` caused it? Is the remaining real-vs-model gap a **control** problem or a **localization** problem?
