# Raspberry Pi Zero | PyPI: gpiozero
try: from gpiozero import LED
except ImportError: pass

# Orange Pi | PyPI: OPi.GPIO
try: import OPi.GPIO as GPIO
except ImportError: pass

from threading import Thread, Event
from math import copysign
from time import sleep


class BaseMotion(Thread):
    def __init__(self, params):
        super().__init__()
        self.speed = params['SPEED']
        self.slowspeed = params.get('SLOWSPEED', self.speed / 2)
        self.reverse = params.get('REVERSE', False)
        self.revolution = params['REVOLUTION']
        self.rotation_range = params.get('ROTATION_RANGE', 0)
        self.sleep_timeout = params.get('SLEEP_TIMEOUT')
        self.fire_pulse = params.get('FIRE_PULSE', 0)
        self.min_pwm = params.get('MIN_PWM', 0)
        self.max_pwm = params.get('MAX_PWM', 50)
        self.pwm_range = self.max_pwm - self.min_pwm

        self.enable_pin = lambda x: print('ENABLE PIN ->', 'ON' if x else 'OFF')
        self.step_pin = lambda x: print('STEP PIN ->', 'ON' if x else 'OFF')
        self.dir_pin = lambda x: print('DIR PIN ->', 'ON' if x else 'OFF')
        self.pwm_pin = lambda x: print('PWM PIN ->', x)
        self.fire_pin = lambda x: print('FIRE PIN ->', 'ON' if x else 'OFF')

        self.stopped = False
        self.armed = False
        self.slowmode = False
        self.sleep = Event()
        self.sleep.set()
        self.abs_rotation = 0
        self.rotation = 0
        self.angle = 0
        self.update = self.sleep.set

    def fire(self):
        if not self.armed: return
        self.fire_pin(True)
        sleep(self.fire_pulse)
        self.fire_pin(False)

    def stop(self):
        self.stopped = True
        self.sleep.set()
        self.join()

    def run(self):
        while not self.stopped:
            if not self.sleep.is_set():
                self.sleep.wait(self.sleep_timeout)
                if not self.sleep.is_set():
                    self.enable_pin(False)
                    continue

            self.enable_pin(True)
            self.step_pin(False)
            self.pwm_pin(self.min_pwm + self.angle * self.pwm_range)
            self.dir_pin(self.rotation > 0 ^ self.reverse)

            if abs(self.rotation) <= 1 / self.revolution:
                self.rotation = 0
                self.sleep.clear()
                continue

            delta = copysign(1 / self.revolution, self.rotation)
            if self.rotation_range and abs(self.abs_rotation - delta) >= self.rotation_range: continue
            self.rotation -= delta
            self.abs_rotation -= delta
            self.step_pin(True)
            speed = self.speed if not self.slowmode else self.slowspeed
            sleep(1 / speed)
