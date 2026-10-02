## 1. Lecture

### Where this course comes from

The lecture material of CS413 follows two open university courses. Both publish their full slide decks and exercise sheets, and working through them is the single most effective way to prepare for the exams.

- **University of Freiburg — Introduction to Mobile Robotics, SS23** (Burgard, Stachniss et al.)
  <http://ais.informatik.uni-freiburg.de/teaching/ss23/robotics/>
- **ETH Zürich — Autonomous Mobile Robots, Spring 2021** (Siegwart, Nieto et al.)
  <https://asl.ethz.ch/education/lectures/autonomous_mobile_robots/spring-2021.html>

> **Strongly recommended:** read the presentations before each session and solve the exercise sheets. They are graded nowhere, and they are what actually makes the midterm and final easy.

### Textbooks

- Corke, Peter. *Robotic Vision: Fundamental Algorithms in Python.* Springer Nature, 2023.
- Thrun, Sebastian, Wolfram Burgard, and Dieter Fox. *Probabilistic Robotics.* MIT Press, 2005.
- Reference: Ogata, Katsuhiko. *Modern Control Engineering.* Prentice Hall, 2010.

Books are not distributed through this repository. See `docs/reading-list.md` for links and library availability.

### Robot software testing is not the same as programming

A program that compiles and runs is not a working robot. On a mobile robot the code interacts with motors that slip, sensors that drift, batteries that sag, and a floor that is never quite flat. The same program will behave differently in the simulator and on the real machine — and that difference is information, not a nuisance.

This changes how you work:

- **You cannot step through a robot with a debugger.** The robot does not stop while you think. Your only window into the running program is what the robot can *show* you.
- **Therefore you instrument first, and code second.** Before writing the logic, decide how the robot will report what it believes is happening.
- **Test in simulation, then on hardware, then compare.** If the numbers disagree, the model is wrong somewhere — that gap is the subject of Weeks 5, 9 and 10.

The TRIK set gives you an IDE with an embedded simulator, so both halves of that loop live in one tool. Programming is available in two flavours out of the box:

- **Visual (block) programming** — fast to sketch behaviour, good for the first run.
- **Text programming** — JavaScript and Python, but *without* advanced libraries. There is no Math.js, no NumPy, no SciPy on the robot. Only the standard library and plain arithmetic. Heavy analysis belongs in an offline Colab notebook, not on the AM1808.

Your instrumentation toolbox for this course:

| Channel | Use it for | Typical call |
|---|---|---|
| Sound | Marking events you can hear from across the room — segment start, goal reached, error | `brick.playTone(freq, ms)` |
| LEDs | Fast state indication (searching / driving / stopped) | `brick.led().red()`, `.green()`, `.orange()` |
| Display | Live values: encoder counts, heading, current waypoint | `brick.display().addLabel(text, x, y)` + `.redraw()` |
| Console / stdout | Step-by-step trace while tethered to the IDE | `print(...)` |
| File logging | Post-run analysis, plots, comparing sim vs. real | `script.writeToFile(name, line)` |

Check the exact signatures for your firmware version in the TRIK help before relying on them.

### Links

- **Test and debug a robotics project** — the workflow this course expects:
  <https://roboticsknowledgebase.com/wiki/robotics-project-guide/test-and-debug/>
- **TRIK help (latest updates, API reference):** <https://help.trikset.com/en>
- **Awesome Mobile Robotics** — curated list of courses, datasets, libraries, papers:
  <https://github.com/mathiasmantelli/awesome-mobile-robotics>

---

## 2. Practical task — Lab 1

### Goal

Make the robot **move, beep, blink and write a log file** while driving a trajectory shaped like **the last two digits of your student ID** — first in the TRIK Studio simulator, then on the real robot.

Example: ID ending in `37` → the robot drives a path that draws the numeral `3`, pauses, then draws the numeral `7`.

### Deliverables

Create a repo `CS413 - Robotics/Lab1/<content>`:

1. **`trajectory_sim.qrs`** — the TRIK Studio program used for the simulator run.
2. **`trajectory_real.qrs`** — the program used on the real robot (may be identical; if not, the diff is part of your answer).
4. **`report.md`** (or a Colab notebook) containing:
   - **3–6 sentences** on where simulation and reality diverged, and your hypothesis for why.
5. **A short video** (phone is fine) of the real robot completing the trajectory, with audible beeps.
