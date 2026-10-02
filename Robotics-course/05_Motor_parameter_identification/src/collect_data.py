import sys
import time
import os

class Program():
    __interpretation_started_timestamp__ = time.time() * 1000

    WHEEL_ID = 5
    MOTOR_PORT = "M4"
    ENCODER_PORT = "E4"
    RUN_TIME = 2.0 

    def execMain(self):
        if not os.path.exists("motor_data"):
            os.makedirs("motor_data")

        print("Старт серии экспериментов для колеса: " + str(self.WHEEL_ID))

        battery_voltage = brick.battery().readVoltage()
        battery_level_file = "motor_data/wheel_" + str(self.WHEEL_ID) + "_battery.txt"
        with open(battery_level_file, 'w') as bf:
            bf.write("battery_voltage_mv: " + str(battery_voltage) + "\n")
        print("Заряд аккумулятора: " + str(battery_voltage) + " мВ")

        voltages = list(range(-100, -4, 5)) + list(range(5, 105, 5))

        for voltage in voltages:
            filename = (
                "motor_data/wheel_" + str(self.WHEEL_ID) +
                "_v_" + str(voltage) + ".txt"
            )
            print("Тестирование: " + str(voltage) + "% -> " + filename)

            brick.encoder(self.ENCODER_PORT).reset()
            time.sleep(0.5)

            start_time = time.time()

            brick.motor(self.MOTOR_PORT).setPower(voltage)

            with open(filename, 'w') as fh:
                fh.write("# wheel_id: " + str(self.WHEEL_ID) + "\n")
                fh.write("# voltage_percent: " + str(voltage) + "\n")
                fh.write("# battery_voltage_mv: " + str(battery_voltage) + "\n")
                fh.write("# format: position_deg time_ms\n")
                fh.write("0 0\n") 

                while True:
                    current_time = time.time() - start_time
                    if current_time > self.RUN_TIME:
                        break

                    position = brick.encoder(self.ENCODER_PORT).read()
                    fh.write(
                        str(position) + " " +
                        str(int(current_time * 1000)) + "\n"
                    )

                    time.sleep(0.005)

            brick.motor(self.MOTOR_PORT).powerOff()
            time.sleep(1.0) 

        print("Эксперименты для колеса " + str(self.WHEEL_ID) + " завершены.")
        brick.stop()
        return


def main():
    program = Program()
    program.execMain()

if __name__ == '__main__':
    main()