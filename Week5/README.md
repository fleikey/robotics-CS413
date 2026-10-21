# Week 5 – Motor parameter identification

Identification of the TRIK motor parameters $T_m$ and $k_e$ from a PWM sweep (−100 % … +100 %, step 5 %) on both wheels. The results are in **[report.md](report.md)**.

## Files

| File                               | Description                                                                                                                                                                                                                                                      |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Data_collection.qrs`              | For every PWM level it drives M3 and M4 for 2 s and logs both encoders, the time and the battery voltage.                                                                                                                                                        |
| `trik_data_bat.txt`                | The recorded data. One line per sample: `PWM_%  left_enc_deg(E4)  right_enc_deg(E3)  t_ms  battery_V`.                                                                                                                                                           |
| `identification.ipynb`             | Step-by-step analysis notebook: loads the data, fits $\theta(t) = \omega_{ss}(t - T_m + T_m e^{-t/T_m})$ to every run, computes $k_e$ and simulates the motor with `odeint`. Its last section writes `report_figs/table.md`, `report_figs/T_m.png` and `report_figs/step_response.png`. |
| `src/plot_omega.py`                | (wheel 1 = left E4, wheel 2 = right E3), plus the fitted $k_e$ lines and the dead zone → `report_figs/omega_all_wheels.png`.                                                                                                                                     |
| `report.md`                        | Results and Discussion.                                                                                                                                                                                                                                          |
| `report_figs/omega_all_wheels.png` | ω against applied voltage, both wheels, with the fitted $k_e$ lines and the dead zone shaded.                                                                                                                                                                    |
| `report_figs/T_m.png`              | $T_m$ for every run against applied voltage, both wheels, with linear fits.                                                                                                                                                                                      |
| `report_figs/step_response.png`    | Measured vs simulated $\theta(t)$ at PWM = 100 %.                                                                                                                                                                                                                |
| `report_figs/table.md`             | $T_m$ and $\omega_{ss}$ for every PWM level, both wheels (included in `report.md`).                                                                                                                                                                              |
## Results

| Wheel | $k_e$, V·s/rad | $T_m$ (median, \|PWM\| ≥ 50 %), s | dead zone, V |
|---|---:|---:|---:|
| Left (E4) | 0.701 | 0.214 | ≈ 0.27 |
| Right (E3) | 0.662 | 0.143 | ≈ 0.28 |

