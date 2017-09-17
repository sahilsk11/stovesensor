import RPi.GPIO as GPIO
import time
import math


class RGBled:
    def __init__(self, red=23, green=25, blue=7, hz=100):
        GPIO.setmode (GPIO.BCM)
        self.led = RGBled(23, 25, 7)
        self.red = red
        self.green = green
        self.blue = blue
        self.hz = hz

        GPIO.setup (red, GPIO.OUT)
        GPIO.setup (green, GPIO.OUT)
        GPIO.setup (blue, GPIO.OUT)

        GPIO.output (red, GPIO.LOW)
        GPIO.output (green, GPIO.LOW)
        GPIO.output (blue, GPIO.LOW)

        self.red_pwm   = GPIO.PWM (red,   hz)
        self.green_pwm = GPIO.PWM (green, hz)
        self.blue_pwm  = GPIO.PWM (blue,  hz)

        # Start PWM with duty cycle 0 (off)
        self.blue_pwm.start(0)
        self.green_pwm.start(0)
        self.red_pwm.start(0)

    def __del__(self):
        self.blue_pwm.stop()
        self.green_pwm.stop()
        self.red_pwm.stop()


    def change_colors(self, dc_r, dc_g, dc_b, delay=0):
        '''Change the duty cycle of each LED's PWM to values specified
            If a value is None, the DC will remain unchanged
        '''

        if dc_r != None : self.red_pwm.ChangeDutyCycle(dc_r)
        if dc_g != None : self.green_pwm.ChangeDutyCycle(dc_g)
        if dc_b != None : self.blue_pwm.ChangeDutyCycle(dc_b)

        time.sleep (delay)

    def cycle_colors(self, delay=0.01):
        '''Cycle through different color combinations'''
        for i in range(100):
            self.change_colors(None, 100-i, i, delay=delay)

        for i in range(100):
            self.change_colors(i, None, 100-i, delay=delay)

        for i in range(100):
            self.change_colors(100-i, i/2, None, delay=delay)


    def PosSinWave(self, amplitude, angle, frequency):
        ''' Adapted from http://www.henryleach.com/2013/05/controlling-rgb-led-with-raspberry-pi.html
        '''
        #angle in degrees
        #creates a positive sin wave between 0 and amplitude*2
        return amplitude + (amplitude * math.sin(math.radians(angle)*frequency) )
        
    def change_colors_sin(self):
        try:
            while 1:
                for i in range(0, 720, 5):
                    self.change_colors( self.PosSinWave(50, i, 0.5),
                                        self.PosSinWave(50, i, 1),
                                        self.PosSinWave(50, i, 2),
                                        delay = 0.1 )
        except KeyboardInterrupt:
            pass
            
    def color_red(self):
        self.led.change_colors(100,0,0)
        
    def color_blue(self):
        self.led.change_colors(0,0,70)

if __name__ == "__main__":
    GPIO.setmode (GPIO.BCM)

    led = RGBled(23, 25, 7)
    led.change_colors(100,0,0)
    time.sleep(4)

    led.change_colors(0,50,0)
    time.sleep(4)

    led.change_colors(0,0,70)
    time.sleep(4)

    print "Sin Wave"
    led.change_colors_sin()
    GPIO.cleanup()
