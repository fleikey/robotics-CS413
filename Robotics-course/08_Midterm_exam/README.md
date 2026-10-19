# Midterm Exam — Student Guidelines

**CS413 Robotics · Fall 2026 · Week 8 · Covers Weeks 1–7**

## Format

- **90 minutes, 100 points** (20 % of the course grade)
- **Section 1:** multiple choice — 30 points. Mark **E** if no option is correct.
- **Section 2:** written answers and calculations — 70 points
- **Allowed:** non-programmable calculator, pen, ruler. No notes, books or devices.
- Write the **formula first, then the numbers, then the result with units**. A number without a method gets at most half the points.
- Angles in radians unless stated. Short code may be asked; pseudocode is accepted.

## Topics

| # | Topic | You must be able to | Read |
|---|---|---|---|
| 1 | Cutting-edge problems of robotics | Explain the sim-to-real gap and one open problem, linked to your labs | [Awesome Mobile Robotics](https://github.com/mathiasmantelli/awesome-mobile-robotics) |
| 2 | Testing the robot | Write a program that moves, beeps, blinks, prints to console and writes a log file without breaking loop timing | [Week 1](../01_TRIK_studio_introduction/README.md), [Test and debug](https://roboticsknowledgebase.com/wiki/robotics-project-guide/test-and-debug/) |
| 3 | Software vs hardware problem | Diagnose a symptom: simulator check, isolate, swap, measure | Week 1 |
| 4 | PID formula | Write the continuous and discrete PID law; explain each term | [Week 2](../02_PID_controller/README.md), [PID demo](https://thomasfermi.github.io/Algorithms-for-Automated-Driving/Control/PID.html) |
| 5 | Numerical integral and derivative | Compute rectangle (left/right), trapezoidal and Simpson integrals; backward and central differences | Week 2 notebook; Susskind, Interlude 2 |
| 6 | PID tuning | Apply Ziegler–Nichols; explain manual tuning and its limits | [Tuning tables](https://eng.libretexts.org/Bookshelves/Industrial_and_Systems_Engineering/Chemical_Process_Dynamics_and_Controls_(Woolf)/09%3A_Proportional-Integral-Derivative_(PID)_Control/9.03%3A_PID_Tuning_via_Classical_Methods) |
| 7 | Choosing P / PI / PD / PID | Pick and justify an architecture for a task; read a step response | Weeks 2–3 |
| 8 | Anti-windup | Explain windup; write clamping, conditional integration or back-calculation | Week 2 |
| 9 | Sensor calibration | Normalise readings to 0–100 from black/white values | [Week 3](../03_Line_following/README.md), [Line following](https://robotresearchlab.com/2019/02/12/how-to-program-a-line-following-robot/) |
| 10 | $T_m$ from scratch | Derive $T_m = JR/(k_mk_e)$ from the electrical and mechanical equations | [Week 5](../05_Motor_parameter_identification/README.md) |
| 11 | First-order DC motor | Use $T_m\dot\omega + \omega = U/k_e$, its step responses $\omega(t)$, $\theta(t)$ and state-space form | [Motor notebook](https://github.com/NewUU-engineering/Robotics-course/blob/main/05_Motor_parameter_identification/Motor_identification.ipynb); Susskind, Lectures 2–3 |
| 12 | Second-order DC motor | Write $L\,di/dt + Ri + k_e\omega = U$, $J\dot\omega = k_mi$; combine; explain when $L$ can be neglected | Week 5; Ogata |
| 13 | Data fit | Explain the inputs and outputs of `curve_fit` (`model`, `xdata`, `ydata`, `p0`, `popt`, `pcov`) and unit conversion | [curve_fit docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html) |
| 14 | Motor nonlinearities | Explain dead zone, battery sag, load, asymmetry, saturation; estimate the dead-zone voltage | Week 5 |
| 15 | Localization formulas | Compute $\varphi$, path, $x$, $y$ from encoders; wrap angles three ways (`while`, `atan2`, modulo) | [Week 6](../06_Localization/), [ETH modelling](https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/Lectures/amod/AMOD_2020/20201019-02%20-%20ETHZ%20-%20Modeling.pdf); Corke, Ch. 2, 6 |
| 16 | Odometry error sources | Classify systematic vs random errors; compute heading drift from a wheel mismatch | Corke, Ch. 6; Thrun, Ch. 5 |
| 17 | Inverse kinematics | Convert $(v, \omega)$ to wheel speeds and back; state the unicycle model | Corke, Ch. 4 |
| 18 | Go-to-goal PID controller | Compute distance, bearing, wrapped heading error and wheel commands with limits | [Week 7](../07_Go-to-goal/); Corke, Ch. 4 |
| 19 | Go-to-goal Lyapunov controller | Apply $U = K_v\cos\alpha\tanh d \mp K_\alpha\alpha$; explain why $V = \tfrac12d^2 + \tfrac12\alpha^2$ decreases | [Go-to-goal notebook](https://github.com/NewUU-engineering/Robotics-course/blob/main/07_Go-to-goal/Go-to-goal_modeling.ipynb); Susskind, Lecture 5 |
| 20 | Sampling time and jitter | Use measured time stamps; explain why file I/O in the loop adds jitter and what it does to the D-term | Week 5 |

## References

- **Syllabus:** CS413 Syllabus_311, Fall 2026 — weekly required reading
- **Repository:** <https://github.com/NewUU-engineering/Robotics-course>
- **Corke, P.** *Robotics, Vision and Control: Fundamental Algorithms in Python*, 3rd ed. Springer, 2023. <https://doi.org/10.1007/978-3-031-06469-2> — Ch. 2, 4, 6
- **Susskind, L., Hrabovsky, G.** *The Theoretical Minimum.* Basic Books, 2013 — Interludes 1–2, Lectures 2–3, 5. Videos: <https://theoreticalminimum.com/courses/classical-mechanics/2011/fall>
- **Ogata, K.** *Modern Control Engineering.* Prentice Hall, 2010 — PID, first- and second-order systems
- **Thrun, S., Burgard, W., Fox, D.** *Probabilistic Robotics.* MIT Press, 2005 — Ch. 5
- Open courses: [Freiburg — Introduction to Mobile Robotics SS23](http://ais.informatik.uni-freiburg.de/teaching/ss23/robotics/) · [ETH — Autonomous Mobile Robots 2021](https://asl.ethz.ch/education/lectures/autonomous_mobile_robots/spring-2021.html)

Books are not distributed through the repository; see `docs/reading-list.md`.
