# evpy
 Efficiency, thermal, and sizing models for brushless DC motor powertrains used in drones and robots.

This are models I've developed over the past few years of graduate research at Texas A&M University. I want them to see the light of day rather sit unread in a journal paper.

I welcome your feedback!

## Posted models:
- **Efficiency models** to predict losses for:
  - brushless DC (BLDC) motor
  - motor controller (also known as electronic speed controller or ESC)
  - Generic lithium-polymer ("Lipo") battery.

## TO-be posted:
- **theory manual** for the efficiency models (my open-source journal paper deriving the efficiency models)
- **Thermal models + theory manual** = predict convective heat transfer coefficient for outrunner BLDC motor.
- **Sizing models + theory manual** = predict optimal size and electrical constants for outrunner BLDC motor.

## SALIENT FILES:
- **evpy.py** = all the models/code
- **ex_mot_ctrl_eff.py** = example file for using motor and controller efficiency function.
- **ex_batt_mdl.py** = example file for using the battery efficiency function.
- **ex_intg_mdl.py** = example file for a combined motor+ctrl+battery model. Uses experimental flight data.
