import time
pi = 3.141592653589793
baseSpeed = 28
maxCorrection = 35
kP = 0.65
kCubic = 0.0008
# Dynamic black detection from starting black value.
# Increase if it does not detect black. Decrease if it thinks white is black.
blackMargin = 35
# If it searches too early on straight line, increase to 12 or 14.
# If it reacts too late at V/angle, decrease to 8.
lostLimit = 10

rotateFast = 28
rotateSlow = -14

arcFast = 30
arcSlow = -8

catchSlow = 8
catchFast = 18
catchForward = 16

# Encoder threshold for angle classification
# larger rotation => 90, smaller => 45
angle90EncoderThreshold = 120

# If search continues too long, stop instead of looping forever
maxTotalSearchCount = 160

logFileName = "line_data.csv"


def limit(x, minVal, maxVal):
    if x > maxVal:
        return maxVal
    if x < minVal:
        return minVal
    return x


def abs_val(x):
    if x < 0:
        return -x
    return x


def stop_motors():
    brick.motor(M3).setPower(0)
    brick.motor(M4).setPower(0)


def stop_button_pressed():
    # Press Enter/OK on TRIK controller to stop safely.
    try:
        return brick.keys().wasPressed(KeysEnum.Enter)
    except:
        try:
            return brick.keys().isPressed(KeysEnum.Enter)
        except:
            return False


def read_encoder_m3():
    try:
        return brick.encoder(E3).read()
    except:
        try:
            return brick.motor(M3).read()
        except:
            return 0


def read_encoder_m4():
    try:
        return brick.encoder(E4).read()
    except:
        try:
            return brick.motor(M4).read()
        except:
            return 0


def main():
    # Put BOTH sensors on black line before pressing Run.
    leftBase = brick.sensor(A1).read()
    rightBase = brick.sensor(A2).read()

    lostCount = 0
    searchCount = 0
    totalSearchCount = 0
    catchCount = 0

    lastTurn = 1
    searchSide = 1

    mode = 0
    # mode 0 = normal P + cubic following
    # mode 1 = short 90-degree rotate search
    # mode 2 = 45-degree arc search
    # mode 3 = opposite-side rotate search
    # mode 4 = opposite-side arc search
    # mode 5 = catch black gently
    # mode 9 = failed search / stopped

    searchStartEncM3 = 0
    searchStartEncM4 = 0

    startTime = time.time()
    lineCounter = 0

    f = open(logFileName, "w")
    f.write(
        "time,left,right,leftBase,rightBase,leftBlack,rightBlack,"
        "err,u,m3Power,m4Power,encM3,encM4,"
        "mode,lostCount,searchCount,totalSearchCount,lastTurn,searchSide,"
        "searchRotation,detectedAngle,detectedSide\n"
    )

    try:
        while True:
            if stop_button_pressed():
                break

            now = time.time() - startTime

            left = brick.sensor(A1).read()
            right = brick.sensor(A2).read()

            encM3 = read_encoder_m3()
            encM4 = read_encoder_m4()

            if left < leftBase + blackMargin:
                leftBlack = 1
            else:
                leftBlack = 0

            if right < rightBase + blackMargin:
                rightBlack = 1
            else:
                rightBlack = 0

            err = (right - rightBase) - (left - leftBase)

            u = 0
            m3Power = 0
            m4Power = 0

            searchDeltaM3 = encM3 - searchStartEncM3
            searchDeltaM4 = encM4 - searchStartEncM4
            searchRotation = abs_val(searchDeltaM3 - searchDeltaM4)

            detectedAngle = 0
            detectedSide = 0

            # If black is found during search, classify angle and catch gently.
            if mode == 1 or mode == 2 or mode == 3 or mode == 4:
                if leftBlack == 1 or rightBlack == 1:
                    detectedSide = searchSide

                    if searchRotation > angle90EncoderThreshold:
                        detectedAngle = 90
                    else:
                        detectedAngle = 45

                    mode = 5
                    catchCount = 0

            # Remember side only in normal following.
            if mode == 0:
                if leftBlack == 1:
                    if rightBlack == 0:
                        lastTurn = -1

                if rightBlack == 1:
                    if leftBlack == 0:
                        lastTurn = 1

                u = kP * err + kCubic * err * err * err
                u = limit(u, -maxCorrection, maxCorrection)

                if u > 5:
                    lastTurn = 1
                if u < -5:
                    lastTurn = -1

                m3Power = baseSpeed + u
                m4Power = baseSpeed - u

                brick.motor(M3).setPower(m3Power)
                brick.motor(M4).setPower(m4Power)

                if leftBlack == 0:
                    if rightBlack == 0:
                        lostCount = lostCount + 1
                    else:
                        lostCount = 0
                else:
                    lostCount = 0

                if lostCount > lostLimit:
                    searchSide = -1

                    searchCount = 0
                    totalSearchCount = 0
                    lostCount = 0

                    searchStartEncM3 = encM3
                    searchStartEncM4 = encM4

                    mode = 1

            elif mode == 1:
                searchCount = searchCount + 1
                totalSearchCount = totalSearchCount + 1

                if searchSide == 1:
                    m3Power = rotateFast
                    m4Power = rotateSlow
                else:
                    m3Power = rotateSlow
                    m4Power = rotateFast

                brick.motor(M3).setPower(m3Power)
                brick.motor(M4).setPower(m4Power)
                if searchCount > 2:
                    searchCount = 0
                    mode = 2
            elif mode == 2:
                searchCount = searchCount + 1
                totalSearchCount = totalSearchCount + 1

                if searchSide == 1:
                    m3Power = arcFast
                    m4Power = arcSlow
                else:
                    m3Power = arcSlow
                    m4Power = arcFast

                brick.motor(M3).setPower(m3Power)
                brick.motor(M4).setPower(m4Power)

                if searchCount > 40:
                    searchSide = -searchSide
                    searchCount = 0
                    mode = 3
            elif mode == 3:
                searchCount = searchCount + 1
                totalSearchCount = totalSearchCount + 1

                if searchSide == 1:
                    m3Power = rotateFast
                    m4Power = rotateSlow
                else:
                    m3Power = rotateSlow
                    m4Power = rotateFast

                brick.motor(M3).setPower(m3Power)
                brick.motor(M4).setPower(m4Power)

                if searchCount > 10:
                    searchCount = 0
                    mode = 4

            elif mode == 4:
                searchCount = searchCount + 1
                totalSearchCount = totalSearchCount + 1

                if searchSide == 1:
                    m3Power = arcFast
                    m4Power = arcSlow
                else:
                    m3Power = arcSlow
                    m4Power = arcFast

                brick.motor(M3).setPower(m3Power)
                brick.motor(M4).setPower(m4Power)

                if searchCount > 40:
                    searchSide = -lastTurn
                    searchCount = 0
                    mode = 1

            elif mode == 5:
                catchCount = catchCount + 1

                if leftBlack == 1:
                    if rightBlack == 0:
                        m3Power = catchSlow
                        m4Power = catchFast
                        lastTurn = -1
                    else:
                        m3Power = catchForward
                        m4Power = catchForward
                else:
                    if rightBlack == 1:
                        m3Power = catchFast
                        m4Power = catchSlow
                        lastTurn = 1
                    else:
                        searchCount = 0
                        mode = 2
                        m3Power = 0
                        m4Power = 0

                brick.motor(M3).setPower(m3Power)
                brick.motor(M4).setPower(m4Power)

                if catchCount > 8:
                    mode = 0
                    catchCount = 0
                    searchCount = 0
                    totalSearchCount = 0
                    lostCount = 0

            if totalSearchCount > maxTotalSearchCount:
                mode = 9
                m3Power = 0
                m4Power = 0
                stop_motors()

            f.write(
                str(now) + "," +
                str(left) + "," +
                str(right) + "," +
                str(leftBase) + "," +
                str(rightBase) + "," +
                str(leftBlack) + "," +
                str(rightBlack) + "," +
                str(err) + "," +
                str(u) + "," +
                str(m3Power) + "," +
                str(m4Power) + "," +
                str(encM3) + "," +
                str(encM4) + "," +
                str(mode) + "," +
                str(lostCount) + "," +
                str(searchCount) + "," +
                str(totalSearchCount) + "," +
                str(lastTurn) + "," +
                str(searchSide) + "," +
                str(searchRotation) + "," +
                str(detectedAngle) + "," +
                str(detectedSide) + "\n"
            )

            lineCounter = lineCounter + 1
            if lineCounter > 20:
                f.flush()
                lineCounter = 0

            if mode == 9:
                break

            script.wait(25)

    finally:
        stop_motors()
        f.flush()
        f.close()


main()