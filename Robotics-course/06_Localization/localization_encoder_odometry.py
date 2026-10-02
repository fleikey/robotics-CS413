import time
import math

class Program():
    def execMain(self):
        baseSpeed = 50
        k = 1.1
        maxCorrection = 35

        r = 0.0375
        W = 0.194
        pi = 3.141592653589793

        leftBase = brick.sensor("A1").read()
        rightBase = brick.sensor("A2").read()

        x = 0.0
        y = 0.0
        theta = 0.0

        oldL = brick.encoder("E3").read()
        oldR = brick.encoder("E4").read()

        startTime = time.time()

        f = open("data.txt", "w")
        f.write("time,x,y,theta,encoder3,encoder4,d_encL,d_encR,A1,A2,err,u,motorL,motorR\n")

        try:
            while True:
                A1 = brick.sensor("A1").read()
                A2 = brick.sensor("A2").read()

                encL = brick.encoder("E3").read()
                encR = brick.encoder("E4").read()

                d_encL = encL - oldL
                d_encR = encR - oldR

                oldL = encL
                oldR = encR

                L = 2 * pi * r * d_encL / 360.0
                R = 2 * pi * r * d_encR / 360.0

                dtheta = (L - R) / W
                dS = (L + R) / 2.0

                x = x + dS * math.cos(theta)
                y = y + dS * math.sin(theta)
                theta = theta + dtheta

                err = (A2 - rightBase) - (A1 - leftBase)
                u = k * err

                if u > maxCorrection:
                    u = maxCorrection
                if u < -maxCorrection:
                    u = -maxCorrection

                motorL = int(baseSpeed + u)
                motorR = int(baseSpeed - u)

                if motorL > 100:
                    motorL = 100
                if motorL < -100:
                    motorL = -100

                if motorR > 100:
                    motorR = 100
                if motorR < -100:
                    motorR = -100

                brick.motor("M3").setPower(motorL)
                brick.motor("M4").setPower(motorR)

                now = time.time() - startTime

                f.write(
                    str(now) + "," +
                    str(x) + "," +
                    str(y) + "," +
                    str(theta) + "," +
                    str(encL) + "," +
                    str(encR) + "," +
                    str(d_encL) + "," +
                    str(d_encR) + "," +
                    str(A1) + "," +
                    str(A2) + "," +
                    str(err) + "," +
                    str(u) + "," +
                    str(motorL) + "," +
                    str(motorR) + "\n"
                )

                f.flush()
                script.wait(30)

        finally:
            brick.motor("M3").setPower(0)
            brick.motor("M4").setPower(0)
            f.close()


def main():
    program = Program()
    program.execMain()

if __name__ == '__main__':
    main()