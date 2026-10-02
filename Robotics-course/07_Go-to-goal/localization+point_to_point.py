import time
import math

class Program():
    def execMain(self):
        r = 0.0375
        W = 0.194
        pi = 3.141592653589793

        kDist = 45
        kAngle = 55

        maxPower = 60
        minPower = 18

        targetLimit = 0.05

        points = [
            [1.0, 0.0],
            [1.0, 1.0]
        ]

        x = 0.0
        y = 0.0
        theta = 0.0

        oldL = brick.encoder("E3").read()
        oldR = brick.encoder("E4").read()

        startTime = time.time()

        f = open("data.txt", "w")
        f.write("time,targetX,targetY,x,y,theta,E3,E4,dE3,dE4,L,R,dS,dtheta,motorL,motorR,distance,angleError\n")

        def limit(value, low, high):
            if value < low:
                return low
            if value > high:
                return high
            return value

        def wrap_angle(a):
            while a > pi:
                a = a - 2 * pi
            while a < -pi:
                a = a + 2 * pi
            return a

        try:
            for p in points:
                targetX = p[0]
                targetY = p[1]

                while True:
                    encL = brick.encoder("E3").read()
                    encR = brick.encoder("E4").read()

                    dE3 = encL - oldL
                    dE4 = encR - oldR

                    oldL = encL
                    oldR = encR

                    L = 2 * pi * r * dE3 / 360.0
                    R = 2 * pi * r * dE4 / 360.0

                    dS = (L + R) / 2.0
                    dtheta = (R - L) / W

                    x = x + dS * math.cos(theta + dtheta / 2.0)
                    y = y + dS * math.sin(theta + dtheta / 2.0)
                    theta = wrap_angle(theta + dtheta)

                    dx = targetX - x
                    dy = targetY - y

                    distance = math.sqrt(dx * dx + dy * dy)
                    targetAngle = math.atan2(dy, dx)
                    angleError = wrap_angle(targetAngle - theta)

                    if distance < targetLimit:
                        brick.motor("M3").setPower(0)
                        brick.motor("M4").setPower(0)
                        script.wait(500)
                        break

                    forward = kDist * distance
                    forward = limit(forward, minPower, maxPower)

                    turn = kAngle * angleError
                    turn = limit(turn, -35, 35)

                    if abs(angleError) > 1.0:
                        forward = 0

                    motorL = int(forward - turn)
                    motorR = int(forward + turn)

                    motorL = limit(motorL, -maxPower, maxPower)
                    motorR = limit(motorR, -maxPower, maxPower)

                    brick.motor("M3").setPower(motorL)
                    brick.motor("M4").setPower(motorR)

                    now = time.time() - startTime

                    f.write(
                        str(now) + "," +
                        str(targetX) + "," +
                        str(targetY) + "," +
                        str(x) + "," +
                        str(y) + "," +
                        str(theta) + "," +
                        str(encL) + "," +
                        str(encR) + "," +
                        str(dE3) + "," +
                        str(dE4) + "," +
                        str(L) + "," +
                        str(R) + "," +
                        str(dS) + "," +
                        str(dtheta) + "," +
                        str(motorL) + "," +
                        str(motorR) + "," +
                        str(distance) + "," +
                        str(angleError) + "\n"
                    )

                    f.flush()
                    script.wait(1)

        finally:
            brick.motor("M3").setPower(0)
            brick.motor("M4").setPower(0)
            f.close()


def main():
    program = Program()
    program.execMain()

if __name__ == '__main__':
    main()