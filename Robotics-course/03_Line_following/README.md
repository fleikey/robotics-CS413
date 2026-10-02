## 1. Lecture

### The problem

Line following is the first task in this course where the robot has to react to the world rather than to its own motors. Last week the PID closed the loop around the wheel encoders. This week it closes the loop around an external sensor: the robot sees how far the line is from its centre and steers to cancel that offset.

It looks trivial and it isn't. The robot has lag — it can only steer by turning its body, so every correction arrives late. Push too hard and it oscillates across the line; too gently and it drifts off on the first curve. That trade-off between speed and stability is the whole lesson, and it is exactly what next week's competition rewards.

### From sensor to error

The controller needs a single signed number: how far, and which side, the line is.

- **One sensor — edge following.** The robot follows the boundary between black and white; the reading itself is the error. Simple, but it only works on one side of the line.
- **Two sensors — difference.** `e = left − right`. Zero when centred, signed by direction. This is the standard setup for this lab.
- **Sensor array or camera.** A weighted position estimate across several sensors. Smoother, more expensive to compute.

**Calibrate before you tune.** Raw reflectance values depend on the room lighting, the floor and each individual sensor. Record the minimum (black) and maximum (white) for each sensor and normalise to 0–100 before computing the error. A controller tuned on uncalibrated values breaks when someone opens the curtains.

### The control law

```
u          = Kp·e + Ki·∫e dt + Kd·de/dt
left_power  = base_speed + u
right_power = base_speed − u
```

The controller output is a *difference* between the wheels, added to a constant forward speed.

| Controller | Behaviour on the line |
|---|---|
| **P** | Follows, but oscillates; the faster you drive, the worse it gets |
| **PD** | The usual answer — D damps the oscillation caused by the steering lag |
| **PI / PID** | The integral rarely helps: on a curve the error is legitimately non-zero, so I winds up and the robot overshoots the exit |
| **Nonlinear** | Bang-bang, deadband, squared error, or slowing `base_speed` when the error is large — often faster than any linear tuning |

Two couplings to keep in mind:

- **Base speed and gains are not independent.** Double the speed and your tuned gains no longer work. Faster driving needs more `Kd`.
- **Sample time still matters.** Keep the loop period fixed, as last week.

### Tuning

Ziegler–Nichols works particularly well here, because you can *see* the ultimate gain: with `Ki = Kd = 0`, raise `Kp` until the robot oscillates steadily across the line, measure the period, and take the coefficients from the table. Method and tables:
<https://eng.libretexts.org/Bookshelves/Industrial_and_Systems_Engineering/Chemical_Process_Dynamics_and_Controls_(Woolf)/09%3A_Proportional-Integral-Derivative_(PID)_Control/9.03%3A_PID_Tuning_via_Classical_Methods>

Then tune by hand. In the lecture we compare three sets of PD gains on the same track — underdamped, well tuned, overdamped — so you know what each looks like before you meet it on your own robot.

The live PID demo from last week is worth revisiting with the steering problem in mind:
<https://thomasfermi.github.io/Algorithms-for-Automated-Driving/Control/PID.html>

### Sketch

```js
function norm(raw, black, white) { return (raw - black) * 100 / (white - black); }

var prevError = 0, integral = 0;
while (running) {
    var error = norm(brick.sensor("A1").read(), BLACK_L, WHITE_L)
              - norm(brick.sensor("A2").read(), BLACK_R, WHITE_R);
    integral += error * dt;
    var u = Kp*error + Ki*integral + Kd*(error - prevError)/dt;
    brick.motor("M3").setPower(BASE + u);
    brick.motor("M4").setPower(BASE - u);
    prevError = error;
    script.wait(dt * 1000);
}
```

Check the sensor and motor ports against your robot — if it steers away from the line, flip the sign of `u`.

### Links

- **TRIK help (sensor API):** <https://help.trikset.com/en>
- **Awesome Mobile Robotics:** <https://github.com/mathiasmantelli/awesome-mobile-robotics>

---

## 2. Practical task — Lab 3

### Goal

Make the robot follow the line on the course track with **five controllers — P, PI, PD, PID and one nonlinear controller of your choice** — in the simulator and on the real robot, and compare them.

Use the same track, the same base speed and the same calibration for all five, so the only thing that changes is the controller. Log the error at every cycle.

Keep your best controller: next week is the competition, and the fastest nonlinear controller wins.

### Deliverables

Create a repo `CS413 - Robotics/Lab3/<content>`:

1. **`line_sim.qrs`** — the TRIK Studio program used for the simulator runs.
2. **`line_real.qrs`** — the program used on the real robot.
3. **`report.md`** (or a Colab notebook) containing:
   - the gains for each of the five controllers and your sensor calibration values;
   - the error over time for all five controllers, plotted on the same axes;
   - a table with lap time, RMS error and number of line losses for each controller;
   - **3–6 sentences** on which controller won and why, and what happened when you increased the base speed.
4. **A short video** (phone is fine) of the real robot completing the track with your best controller.
