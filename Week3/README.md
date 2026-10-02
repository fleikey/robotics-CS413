V_shaped_unaware.qrs is the correct running version.

In V_shaped_aware.qrs I tried to take into account binary flags(wether either of the sensors are sensing dark, known by the darkness threshold)

The most efficient vesion is just the PD control with lonlinear, decreasing the speed as error increases, controller. 
