# Week 5 – Motor parameter identification

Identification of the TRIK motor parameters $T_m$ and $k_e$ from a PWM sweep (−100 % … +100 %, step 5 %) on both wheels. The results are in **[report.md](report.md)**.

## Files

| File                            | Description                                                                                                                                                                                             |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Data_collection.qrs`           | TRIK Studio program that runs on the robot. For every PWM level it drives M3 and M4 for 2 s and logs both encoders, the time and the battery voltage. On the robot the log is saved as `trik_data.txt`. |
| `trik_data_bat.txt`             | The recorded data (the robot's `trik_data.txt`, renamed). One line per sample: `PWM_%  left_enc_deg(E4)  right_enc_deg(E3)  t_ms  battery_V`.                                                           |
| `identification.ipynb`          | Step-by-step analysis notebook: loads the data, fits $\theta(t) = \omega_{ss}(t - T_m + T_m e^{-t/T_m})$ to every run, computes $k_e$ and simulates the motor with `odeint`.                            |
| `make_report_figures.py`        | Script that makes all the figures and the table used in `report.md`.                                                                                                                                    |
| `report.md`                     | The report: table of $T_m$ and $\omega_{ss}$ for every PWM level, $\omega_{ss}(U)$ plot with $k_e$ and the dead zone, a measured vs simulated step response, and a discussion.                          |
| `report_figs/omega_vs_U.png`    | Steady-state speed against applied voltage, both wheels, with the fitted $k_e$ lines and the dead zone shaded.                                                                                          |
| `report_figs/step_response.png` | Measured vs simulated $\theta(t)$ at PWM = 100 %.                                                                                                                                                       |
| `report_figs/table.md`          | $T_m$ and $\omega_{ss}$ for every PWM level, both wheels (included in `report.md`).                                                                                                                     |
## Results

| Wheel | $k_e$, V·s/rad | $T_m$ (median, \|PWM\| ≥ 50 %), s | dead zone, V |
|---|---:|---:|---:|
| Left (E4) | 0.701 | 0.214 | ≈ 0.27 |
| Right (E3) | 0.662 | 0.143 | ≈ 0.28 |

