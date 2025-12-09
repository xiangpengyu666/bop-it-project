import time
import math
import random

import board
import busio
import digitalio
import pwmio

import adafruit_ssd1306
import adafruit_adxl34x



#   I2C initialization

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
accel = adafruit_adxl34x.ADXL345(i2c)


#   press / pull buttons

btn_press = digitalio.DigitalInOut(board.D2)
btn_press.direction = digitalio.Direction.INPUT
btn_press.pull = digitalio.Pull.UP

btn_pull = digitalio.DigitalInOut(board.D3)
btn_pull.direction = digitalio.Direction.INPUT
btn_pull.pull = digitalio.Pull.UP



#   Rotary input（Twist）

rot_a = digitalio.DigitalInOut(board.D6)
rot_a.direction = digitalio.Direction.INPUT
rot_a.pull = digitalio.Pull.UP

rot_b = digitalio.DigitalInOut(board.D7)
rot_b.direction = digitalio.Direction.INPUT
rot_b.pull = digitalio.Pull.UP



#   buzzer

buzzer = pwmio.PWMOut(board.D1, duty_cycle=0, frequency=2000, variable_frequency=True)


def beep(freq, dur):
    buzzer.frequency = freq
    buzzer.duty_cycle = 30000
    time.sleep(dur)
    buzzer.duty_cycle = 0
    time.sleep(0.005)



#   Four Sound Effects

# PRESS — upward rising tones
def sfx_press():
    for f in [600, 800, 1000, 1300, 1600, 2000, 2400]:
        beep(f, 0.08)
    for f in [2600, 2800, 3000]:
        beep(f, 0.05)


# PULL — descending tones
def sfx_pull():
    for f in [700, 600, 500, 400, 350, 300]:
        beep(f, 0.10)
    beep(200, 0.20)


# TWIST — quick alternating taps
def sfx_twist():
    taps = [900, 1200, 1000, 1400]
    for f in taps:
        beep(f, 0.10)
        time.sleep(0.06)


# SHAKE — high freq random noise
def sfx_shake():
    for _ in range(15):
        f = random.randint(2000, 4200)
        beep(f, 0.04)
    for f in [3000, 3800, 4200]:
        beep(f, 0.03)


def sfx_success():
    beep(1800, 0.06)
    beep(2200, 0.06)


def sfx_fail():
    beep(350, 0.20)
    beep(220, 0.18)


def sfx_start():
    beep(800, 0.06)
    beep(1200, 0.06)
    beep(1600, 0.08)



#   5×7 ASCII Font

font5x7 = [
[0,0,0,0,0],[0,0,95,0,0],[0,7,0,7,0],[20,127,20,127,20],[36,42,127,42,18],
[35,19,8,100,98],[54,73,86,32,80],[0,5,3,0,0],[0,28,34,65,0],[0,65,34,28,0],
[20,8,62,8,20],[8,8,62,8,8],[0,80,48,0,0],[8,8,8,8,8],[0,96,96,0,0],
[32,16,8,4,2],[62,81,73,69,62],[0,66,127,64,0],[66,97,81,73,70],
[33,65,69,75,49],[24,20,18,127,16],[39,69,69,69,57],[60,74,73,73,48],
[1,113,9,5,3],[54,73,73,73,54],[6,73,73,41,30],[0,54,54,0,0],
[0,86,54,0,0],[8,20,34,65,0],[20,20,20,20,20],[0,65,34,20,8],
[2,1,81,9,6],[50,73,121,65,62],[126,17,17,17,126],[127,73,73,73,54],
[62,65,65,65,34],[127,65,65,34,28],[127,73,73,73,65],[127,9,9,9,1],
[62,65,73,73,58],[127,8,8,8,127],[0,65,127,65,0],[32,64,65,63,1],
[127,8,20,34,65],[127,64,64,64,64],[127,2,12,2,127],[127,4,8,16,127],
[62,65,65,65,62],[127,9,9,9,6],[62,65,81,33,94],[127,9,25,41,70],
[38,73,73,73,50],[1,1,127,1,1],[63,64,64,64,63],[31,32,64,32,31],
[127,32,24,32,127],[99,20,8,20,99],[3,4,120,4,3],[97,81,73,69,67],
[0,127,65,65,0],[2,4,8,16,32],[0,65,65,127,0],[4,2,1,2,4],
[64,64,64,64,64],[0,3,5,0,0],[32,84,84,120,64],[127,40,68,68,56],
[56,68,68,68,40],[56,68,68,40,127],[56,84,84,84,24],[8,126,9,9,2],
[24,164,164,156,120],[127,8,4,4,120],[0,68,125,64,0],[32,64,68,61,0],
[127,16,40,68,0],[0,65,127,64,0],[124,4,120,4,120],[124,8,4,4,120],
[56,68,68,68,56],[252,36,36,36,24],[24,36,36,24,252],[124,8,4,4,8],
[72,84,84,84,36],[4,63,68,64,32],[60,64,64,32,124],[28,32,64,32,28],
[60,64,48,64,60],[68,40,16,40,68],[28,160,160,160,124],[68,100,84,76,68],
[0,8,54,65,0],[0,0,119,0,0],[0,65,54,8,0],[2,1,2,4,2]
]


def draw_char(ch, x, y):
    idx = ord(ch) - 32
    if 0 <= idx < len(font5x7):
        data = font5x7[idx]
        for col in range(5):
            line = data[col]
            for row in range(7):
                if line & (1 << row):
                    oled.pixel(x + col, y + row, 1)
    return x + 6


def draw_text(text, x, y):
    for ch in text:
        x = draw_char(ch, x, y)


def show_lines(lines, score=None):
    """all lines are centered."""
    oled.fill(0)
    y = 0
    for t in lines:
        t = t.upper()
        w = len(t) * 6
        x = max(0, (128 - w) // 2)
        draw_text(t, x, y)
        y += 12

    if score is not None:
        s = "SCORE:" + str(score)
        w = len(s) * 6
        x = max(0, (128 - w) // 2)
        draw_text(s, x, 52)

    oled.show()



#   Input State
last_press = True
last_pull = True
last_a = True
last_b = True
twist_cooldown = False



#   Shake Calibration
def accel_mag():
    x, y, z = accel.acceleration
    return math.sqrt(x * x + y * y + z * z)


print("Calibrating shake...")
samples = [accel_mag() for _ in range(20)]
baseline = sum(samples) / len(samples)
shake_th = 6.0

#   Input Polling

def poll_input():
    global last_press, last_pull, last_a, last_b, twist_cooldown

    # PRESS
    cur = btn_press.value
    if last_press and not cur:
        last_press = cur
        return "PRESS"
    last_press = cur

    # PULL
    cur = btn_pull.value
    if last_pull and not cur:
        last_pull = cur
        return "PULL"
    last_pull = cur

    # TWIST
    a = rot_a.value
    b = rot_b.value

    if not twist_cooldown and (a != last_a or b != last_b):
        twist_cooldown = True
        last_a = a
        last_b = b
        return "TWIST"

    if twist_cooldown and a == last_a and b == last_b:
        twist_cooldown = False

    last_a = a
    last_b = b

    # SHAKE
    if accel_mag() - baseline > shake_th:
        return "SHAKE"

    return None



#   Mode Selection

MODE_PRACTICE = 0
MODE_EASY = 1
MODE_HARD = 2

MODES = ["PRACTICE", "EASY", "HARD"]


def select_mode():
    """ Change the mode through twist - PRESS Confirms selection. """
    selected = 0
    while True:
        lines = ["BOP-IT", "SELECT MODE", ""]
        for idx, name in enumerate(MODES):
            prefix = "> " if idx == selected else "  "
            lines.append(prefix + name)
        show_lines(lines, score=None)

        act = poll_input()
        if act == "TWIST":
            selected = (selected + 1) % len(MODES)
            time.sleep(0.15)  # Prevent over-rotation
        elif act == "PRESS":
            sfx_success()
            return selected
        else:
            time.sleep(0.02)



#   Gaame Logic

ACTIONS = ["PRESS", "PULL", "TWIST", "SHAKE"]
SFX = {
    "PRESS": sfx_press,
    "PULL": sfx_pull,
    "TWIST": sfx_twist,
    "SHAKE": sfx_shake
}


def get_time_limit(score, mode):
    """Based on mode and score, return time limit for current round."""
    if mode == MODE_PRACTICE:
        return None

    if mode == MODE_EASY:
        base = 5.0
        min_t = 3.0
        k = 0.15   # Minus 0.15s per point
    else:  # MODE_HARD
        base = 3.5
        min_t = 2.0
        k = 0.12   # Minus 0.12s per point

    return max(min_t, base - score * k)


def play_round(score, mode):
    """
    One round of the game.
    """
    action = random.choice(ACTIONS)
    time_limit = get_time_limit(score, mode)

    show_lines([action, "DO IT!"], score)
    SFX[action]()

    start = time.monotonic()

    while True:
        # Time limit check
        if time_limit is not None:
            if time.monotonic() - start > time_limit:
                # Over time
                sfx_fail()
                return False, score

        act = poll_input()
        if act is None:
            time.sleep(0.01)
            continue

        if act == action:
            # Proper action
            sfx_success()
            return True, score + 1

        else:
            # Mistake
            sfx_fail()
            if mode == MODE_PRACTICE:
                # practice
                show_lines(["WRONG!", "TRY AGAIN"], score)
                time.sleep(0.7)
                show_lines([action, "DO IT!"], score)
                start = time.monotonic()  # reset timer
                continue
            else:
                # Non-Practice - fail
                return False, score


#   Main Loop

def main():
    while True:
        # Choose Mode
        mode = select_mode()
        score = 0

        # Mode Confirmation
        lines = ["MODE: " + MODES[mode], "PRESS TO START"]
        show_lines(lines, score)
        sfx_start()

        # Wait for PRESS / PULL
        while True:
            act = poll_input()
            if act in ("PRESS", "PULL"):
                break
            time.sleep(0.02)

        while True:
            success, score = play_round(score, mode)
            if not success and mode != MODE_PRACTICE:
                # Game Over
                show_lines(["GAME OVER", "SCORE " + str(score)], score)
                time.sleep(1.5)
                break

main()