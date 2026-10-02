import time

base = 18
turn = 20
cornerTurn = 24

threshold = 35
maxPower = 50

lastSide = 1
lost = 0

sensorA1 = 0
sensorA2 = 0
modeWatch = 0
lostCountWatch = 0
leftBlackWatch = 0
rightBlackWatch = 0
searchRotation = 0


def clamp(x, a, b):
    if x < a:
        return a
    if x > b:
        return b
    return x


def motors(l, r):
    brick.motor("M3").setPower(clamp(l, -maxPower, maxPower))
    brick.motor("M4").setPower(clamp(r, -maxPower, maxPower))


def black(x):
    return x < threshold


def main():
    global lastSide, lost
    global sensorA1, sensorA2
    global modeWatch, lostCountWatch
    global leftBlackWatch, rightBlackWatch, searchRotation

    while True:
        sensorA1 = brick.sensor("A1").read()
        sensorA2 = brick.sensor("A2").read()

        leftBlack = black(sensorA1)
        rightBlack = black(sensorA2)

        leftBlackWatch = 1 if leftBlack else 0
        rightBlackWatch = 1 if rightBlack else 0

        if leftBlack and rightBlack:
            modeWatch = 1
            lost = 0
            motors(cornerTurn, -cornerTurn)

        elif leftBlack and not rightBlack:
            modeWatch = 2
            lost = 0
            lastSide = -1
            motors(turn, -4)

        elif rightBlack and not leftBlack:
            modeWatch = 3
            lost = 0
            lastSide = 1
            motors(-4, turn)

        else:
            lost += 1
            lostCountWatch = lost

            if lost < 3:
                modeWatch = 4
                motors(base, base)
            else:
                modeWatch = 5

                if lastSide == -1:
                    searchRotation = -1
                    motors(cornerTurn, -cornerTurn)
                else:
                    searchRotation = 1
                    motors(-cornerTurn, cornerTurn)

        script.wait(35)


main()