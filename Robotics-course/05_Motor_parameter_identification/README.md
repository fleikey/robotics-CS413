## 1. Lecture

### Why identify a motor

Every controller in this course so far was tuned by hand: change `Kp`, watch the robot, change it again. That works until you need to *predict* what the robot will do — and from Week 6 onwards we need exactly that. Localization integrates wheel speeds into a pose, go-to-goal plans a velocity profile, and the simulator is only useful if its motors behave like ours. All of that rests on a model of the drive, and a model is only as good as its parameters.

**System identification** means: choose a model structure from physics, excite the real system with a known input, record its response, and fit the unknown parameters so the model reproduces the measurement. This week we do it for the TRIK RK370 DC motor.

### The model

A DC motor with a light load is well described by a first-order system in angular velocity. Neglecting the inductance (the electrical time constant is much shorter than the mechanical one):

```
T_m · dω/dt + ω = U / k_e
dθ/dt = ω
```

| Symbol | Meaning | Unit |
|---|---|---|
| `U` | voltage applied to the motor | V |
| `ω`, `θ` | shaft angular velocity and angle | rad/s, rad |
| `T_m` | electromechanical time constant — how fast the motor reaches its speed | s |
| `k_e` | back-EMF constant — how much voltage one rad/s of speed "costs" | V·s/rad |

For a step of voltage `U` applied at `t = 0` from rest:

```
ω(t) = ω_ss · (1 − e^(−t/T_m)),                 ω_ss = U / k_e
θ(t) = ω_ss · (t − T_m + T_m · e^(−t/T_m))
```

So one step response gives us two numbers: the **steady-state speed** `ω_ss` (the slope of `θ(t)` once it is a straight line) and the **time constant** `T_m` (how long the curve takes to bend into that line). Repeat for many voltages and you also get `k_e` as the slope of `ω_ss` against `U`.

### What the model leaves out

The model is linear. The motor is not, and the experiment is designed to show where:

- **Dead zone.** Below some PWM the static friction wins and the wheel does not turn at all. On our robots this is visible around ±5–15 %.
- **Battery sag.** TRIK sets *PWM percent*, not volts. The real voltage is `U = PWM/100 · U_battery`, and `U_battery` drops as the battery discharges. Record it for every run.
- **Load.** A wheel on the floor, a wheel in the air and a bare motor give different `T_m`. Say which one you measured.
- **Asymmetry and spread.** Forward and reverse are not identical, and no two motors are identical. That is why we measure each wheel and both directions.
- **Quantisation and timing.** The encoder resolution is 1°, and the loop period on the AM1808 is not perfectly constant — so record the *actual* time stamp of every sample, never assume it.

### Experiment design

1. Hold the robot so the wheel spins freely (or put it on a stand) — unless you deliberately measure under load.
2. For each PWM level from −100 % to +100 % in 5 % steps: reset the encoder, apply the step, sample `(time, angle)` as fast as the loop allows for ~2 s, switch off, let the motor stop.
3. Read the battery voltage at the start of the series.
4. **Log to memory, write to file afterwards.** File I/O inside the sampling loop stretches the period and adds jitter; a Python list does not.
5. Offline (Colab): convert to SI, fit `θ(t)` with `scipy.optimize.curve_fit`, collect `T_m` and `ω_ss` for every level, fit `ω_ss(U)`.

### Sketch — data collection on TRIK (Python)

Pure Python, no libraries beyond the standard ones that TRIK Studio ships. Check the ports against your robot.

```python
import time

WHEEL_ID     = 1        # 1..4 left to right, 5 = bare motor
MOTOR_PORT   = "M4"
ENCODER_PORT = "E4"
RUN_TIME     = 2.0      # s of recording per PWM level
DT           = 0.005    # s, target sampling period
REST_TIME    = 1.0      # s, let the motor stop between runs

LEVELS = list(range(-100, 0, 5)) + list(range(5, 105, 5))


def record_step(power):
    """Apply a PWM step and return [(t_ms, angle_deg), ...] sampled from rest."""
    motor   = brick.motor(MOTOR_PORT)
    encoder = brick.encoder(ENCODER_PORT)

    encoder.reset()
    time.sleep(0.5)                     # let the reset settle

    samples = []
    t0 = time.time()
    motor.setPower(power)               # the step: t = 0
    while True:
        t = time.time() - t0
        if t > RUN_TIME:
            break
        samples.append((int(t * 1000), encoder.read()))
        time.sleep(DT)
    motor.powerOff()
    return samples


def save(power, battery, samples):
    name = "wheel_%d_v_%d.txt" % (WHEEL_ID, power)
    with open(name, "w") as f:
        f.write("# wheel_id: %d\n" % WHEEL_ID)
        f.write("# pwm_percent: %d\n" % power)
        f.write("# battery_voltage: %s\n" % battery)
        f.write("# format: time_ms angle_deg\n")
        for t_ms, angle in samples:
            f.write("%d %s\n" % (t_ms, angle))


def main():
    battery = brick.battery().readVoltage()
    print("Wheel %d, battery %s V" % (WHEEL_ID, battery))

    for power in LEVELS:
        brick.display().addLabel("PWM %d %%" % power, 1, 1)
        brick.display().redraw()

        samples = record_step(power)
        save(power, battery, samples)   # file I/O only after the motor is off

        print("PWM %4d %%: %d samples, final angle %s deg"
              % (power, len(samples), samples[-1][1]))
        time.sleep(REST_TIME)

    brick.playTone(1000, 300)           # audible "done"
    brick.stop()


main()
```

Things to look at before you trust the files:

- **Sample spacing.** Print `len(samples)`. 2 s at 5 ms should give ~400 samples; if you get 40, your loop is not doing what you think.
- **Sign.** Positive PWM should give a growing angle. If not, the encoder and motor directions disagree on your robot — note it, do not "fix" the data by hand.
- **Saturation.** At high PWM the curve should still bend into a straight line within 2 s. If it does not, increase `RUN_TIME`.

### Sketch — fitting (Colab)

```python
t, theta = np.loadtxt("wheel_1_v_50.txt", comments="#", unpack=True)
t, theta = t / 1000, np.radians(theta)

def model(t, w_ss, T_m):
    return w_ss * (t - T_m + T_m * np.exp(-t / T_m))

(w_ss, T_m), _ = optimize.curve_fit(model, t, theta, p0=[8, 0.1])
```

The full worked example — including simulating the identified model with `odeint` and comparing it with the measurement — is in [`Motor_identification.ipynb`](Motor_identification.ipynb). Reference measurements and plotting scripts from our own robots are in [`src/`](src/).

### Links

- **ETH Zürich AMOD — Modeling (differential drive and DC motor):**
  <https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/Lectures/amod/AMOD_2020/20201019-02%20-%20ETHZ%20-%20Modeling.pdf>
- **Worked identification notebook:** [`Motor_identification.ipynb`](Motor_identification.ipynb)
- **TRIK help (motor, encoder, battery API):** <https://help.trikset.com/en>
- **SciPy `curve_fit`:** <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html>

---

## 2. Practical task — Lab 5

### Goal

**Record the rotation data of your robot's motors** and identify `T_m` and `k_e` for each of them.

Run the step-response experiment from the sketch above on **both drive wheels** of your robot, for every PWM level from −100 % to +100 % in 5 % steps, with the battery voltage logged. Then fit the model offline and run the identified motor in simulation next to your measurement.

Your parameters are reused in Week 6 (localization) and Week 7 (go-to-goal), and they are assessed as *Motor parameters identification* in Week 6 — measure carefully.

### Deliverables

Create a repo `CS413-Robotics/Lab5/<content>`:

1. **`motor_identification.qrs`** — the TRIK Studio Python program used to collect the data.
2. **`motor_data/`** — the raw files exactly as the robot wrote them (`wheel_<N>_v_<PWM>.txt`, one per level and wheel). Do not edit them.
3. **`report.md`** (or a Colab notebook) containing:
   - a table of `T_m` and `ω_ss` for every PWM level, for each wheel;
   - a plot of `ω_ss` against the actual voltage `U`, both wheels on the same axes, with the fitted `k_e` and the dead zone marked;
   - one step response with the measured `θ(t)` and the simulated model on the same axes;
   - **3–6 sentences** on where the linear model fails, how much the two wheels differ, and what that difference will do to your robot's odometry next week.
