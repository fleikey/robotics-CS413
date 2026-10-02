## 1. Lecture

### Why PID

Last week the robot drove open-loop: you told the motors a power level and hoped. It worked in the simulator and drifted on the floor, because nothing in the program ever checked whether the robot was actually doing what it was told.

A controller closes that loop. It compares what you asked for with what the sensors report, and corrects. PID is the algorithm that does this — the most widely used control algorithm in existence, and the standard answer to the basic problem of making a system **stable, accurate and fast** at the same time.

### The three terms

At every control cycle you compute the error between setpoint and measurement:

```
e(t) = setpoint − measurement
u(t) = Kp·e(t) + Ki·∫e(t)dt + Kd·de(t)/dt
```

| Term | Reacts to | Effect when increased | Failure mode |
|---|---|---|---|
| **P** — proportional | the error *now* | faster response, smaller error | oscillation; never fully removes steady-state error |
| **I** — integral | accumulated past error | kills steady-state error | overshoot, windup, sluggish recovery |
| **D** — derivative | rate of change of error | damping, less overshoot | amplifies sensor noise |

The whole craft of tuning is trading these three failure modes against each other. There is no setting that has none of them.

### What changes on a real robot

The textbook formula is continuous. Your robot runs a loop. That difference is where most student PID controllers fail:

- **Fixed sample time.** Compute `dt` and use it, or keep the loop period constant. A PID whose `dt` wobbles is not the controller you tuned.
- **Integral windup.** While the motor is saturated at ±100 power, the integral keeps growing and the robot overshoots badly when it finally moves. Clamp the accumulator.
- **Derivative on noise.** Encoder differences over one short cycle are noisy. Filter, or compute the derivative over several cycles.
- **Saturation.** Your output is motor power, and it is bounded. Clip it — and take the clipping into account before you update the integral.
- **No libraries.** Expression block with Python style code. A PID needs nothing more than four floats of state.

### Tuning methods

Guessing works, but slowly. The two classical recipes give you a starting point from a single experiment:

- **Ziegler–Nichols** — raise `Kp` with `Ki = Kd = 0` until the system oscillates steadily; read off the ultimate gain `Ku` and the oscillation period `Tu`, then take the coefficients from the table.
- **Cohen–Coon** — derived from an open-loop step response; better suited to systems with noticeable dead time.

Both methods, with the coefficient tables:
<https://eng.libretexts.org/Bookshelves/Industrial_and_Systems_Engineering/Chemical_Process_Dynamics_and_Controls_(Woolf)/09%3A_Proportional-Integral-Derivative_(PID)_Control/9.03%3A_PID_Tuning_via_Classical_Methods>

Treat the result as a first guess, not an answer. Classical tuning gets you into the right order of magnitude; the last factor of two is manual.

### Live demo

Interactive demonstration of how each coefficient changes the response — move the sliders before you touch the robot:
<https://thomasfermi.github.io/Algorithms-for-Automated-Driving/Control/PID.html>

### Links

- **TRIK help (motor and encoder API):** <https://help.trikset.com/en>
- **Awesome Mobile Robotics:** <https://github.com/mathiasmantelli/awesome-mobile-robotics>
- Reference: Ogata, Katsuhiko. *Modern Control Engineering.* Prentice Hall, 2010 — chapters on PID design and tuning.

---

## 2. Practical task — Lab 2

### Goal

Replace the open-loop motion of [Lab 1](../01_TRIK_studio_introduction/README.md) with **encoder-based PID control**, and drive the same trajectory — the last two digits of your student ID — in the simulator and on the real robot.

Concretely:

1. Write a PID controller that drives a motor to a **target encoder position** (and, if you go further, to a target speed).
2. Rebuild `forward(distance)` and `turn(angle)` on top of it, so distance and angle come from encoder counts rather than from timing.
3. Tune `Kp`, `Ki`, `Kd` — start with Ziegler–Nichols, finish by hand — and record what each change did.
4. Run the ID trajectory again. It should be visibly closer to the intended shape than last week.

### Deliverables

Create a repo `CS413 - Robotics/Lab2/<content>`:

1. **`pid_sim.qrs`** — the TRIK Studio program used for the simulator run.
2. **`pid_real.qrs`** — the program used on the real robot (if the coefficients differ from the simulator ones, that difference is part of your answer).
3. **`report.md`** (or a Colab notebook) containing:
   - the final `Kp`, `Ki`, `Kd` and how you arrived at them;
   - a step-response plot or table for at least three coefficient sets, one of them deliberately badly tuned;
   - **3–6 sentences** comparing the Lab 1 and Lab 2 trajectories — what got better, and what PID did *not* fix.
4. **A short video** (phone is fine) of the real robot completing the trajectory.
