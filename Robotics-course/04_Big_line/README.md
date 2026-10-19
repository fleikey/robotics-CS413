## 1. Lecture

### The problem

Last week the goal was to follow the line *well*. This week the goal is to follow it *fast*. Every robot drives the same track, and the fastest clean lap wins.

The rule that changes everything: **at every moment, one wheel runs at 100% PWM.** There is no `base_speed` to lower any more. The robot is always driving as fast as its outer wheel allows, and the controller can only steer by slowing the inner wheel. All the stability margin you had last week by choosing a comfortable base speed is gone, so the controller has to earn it.

### The control law at full speed

Last week the controller output `u` was added to one wheel and subtracted from the other. At 100% there is no room to add, so the mixing changes:

```
u = controller(e)

if u ≥ 0:  left = 100,      right = 100 − u
else:      left = 100 + u,  right = 100
```

- `u = 0` → both wheels at 100%, straight line at top speed.
- `u = 100` → inner wheel stopped, pivot around it.
- `u = 200` → inner wheel at −100%, spin in place. Clamp `|u| ≤ 200`.

Steering is now *braking*: every correction costs speed. A controller that corrects too often is slow even if it never loses the line.

### What changes at full speed

- **Lag grows with speed.** The robot travels further between a reading and the moment the correction takes effect. Gains tuned at 50% last week will oscillate or overshoot here — expect to retune from scratch, and expect to need more `Kd`.
- **The loop period matters more.** At top speed a 20 ms wait is a few centimetres of blind driving. Keep the period fixed, but as short as your loop allows.
- **Losing the line is the real enemy.** On a sharp curve the line will leave both sensors. A robot that remembers *which side* it was last seen on and turns hard that way recovers; one that does not, drives off the track.
- **Battery voltage is part of the plant.** 100% PWM on a full battery and on a half-empty one are different speeds. Tune and race on a charged battery.

### Ideas worth trying

Last week's nonlinear controller is your starting point. Things that tend to win:

- **Gain scheduling** — small gains when the error is small (fewer needless corrections on straights), large gains when it is large.
- **Deadband** — ignore small errors entirely, so the robot drives straight at 100% on both wheels.
- **Line-loss recovery** — when both sensors read white, keep turning towards the last known side at maximum `u`.
- **Sensor placement** — mounting the sensors further ahead of the wheel axle gives the controller earlier warning (lookahead), at the cost of more sensitivity to small heading errors.

### Sketch

The sketch is in Python so the logic is easy to read. **Your race program must be built in the TRIK Studio visual (block) language**: translate each line into blocks, using variables, a loop, and "if" blocks.

```python
def norm(raw, black, white):
    return (raw - black) * 100 / (white - black)

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

prev_error = 0
last_side = 0

while True:
    l = norm(brick.sensor("A1").read(), BLACK_L, WHITE_L)
    r = norm(brick.sensor("A2").read(), BLACK_R, WHITE_R)
    error = l - r

    if l > WHITE_LEVEL and r > WHITE_LEVEL:      # line lost
        u = 200 * last_side                      # turn hard towards where it was
    else:
        u = Kp * error + Kd * (error - prev_error) / dt
        last_side = 1 if error > 0 else -1
        prev_error = error

    u = clamp(u, -200, 200)

    if u >= 0:
        brick.motor("M3").setPower(100)
        brick.motor("M4").setPower(100 - u)
    else:
        brick.motor("M3").setPower(100 + u)
        brick.motor("M4").setPower(100)

    script.wait(dt * 1000)
```

As last week, check the ports and signs against your robot. `WHITE_LEVEL` is a threshold on the normalised reading; choose it from your calibration.

### Links

- **TRIK help (sensor API):** <https://help.trikset.com/en>
- **Live PID demo:** <https://thomasfermi.github.io/Algorithms-for-Automated-Driving/Control/PID.html>
- **Awesome Mobile Robotics:** <https://github.com/mathiasmantelli/awesome-mobile-robotics>

---

## 2. Practical task — Lab 4: Line-following competition

### Goal

Complete one lap of the course track on the **real robot** in the shortest possible time.

**Rules**

- At every control cycle **one wheel must be at 100% PWM**; the controller may only slow the other wheel. Programs are checked before the race.
- The program must be written in the **TRIK Studio visual (block) language**. Text-based JavaScript or Python programs are not accepted for the race.
- Any controller is allowed — linear, nonlinear or a combination.
- Robots use the standard kit and two line sensors. Sensor mounting position may be changed; no extra sensors.
- Each team gets **3 attempts**; the best time counts.
- An attempt counts only if the robot completes the full lap without leaving the track. Short line losses with recovery are fine; driving off the track ends the attempt.
- Calibrate on the competition track on race day — the lighting will not be the same as in your lab.

**The winner gets +4 additional points.**

### Deliverables

Create a repo `CS413-Robotics/Lab4/<content>`:

1. **`line_race.qrs`** — the visual (block) TRIK Studio program you race with.
2. **`report.md`** (or a Colab notebook) containing:
   - your controller (equations or pseudocode), gains and sensor calibration values;
   - the error over time for your best practice lap;
   - your best practice lap time and your official race time;
   - **3–6 sentences** on what you changed from your Lab 3 controller to run at full speed, and what limited your lap time.
3. **A short video** (phone is fine) of your best lap on the real robot.
