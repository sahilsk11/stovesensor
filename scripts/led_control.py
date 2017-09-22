import RPi.GPIO as GPIO

import time

import math



''' LED control library. Adapted from http://www.henryleach.com/2013/05/controlling-rgb-led-with-raspberry-pi.html

'''



class RGBled:
    def __init__(self, red=23, green=25, blue=7, hz=100):
        GPIO.setmode (GPIO.BCM)
        GPIO.setwarnings(False)
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
        # Just setup the PWM. Dont start it else it might interfere 

    def __del__(self):
        self.stop_pwm()

    def stop_pwm(self):
        self.blue_pwm.stop()
        self.green_pwm.stop()
        self.red_pwm.stop()

    def start_pwm(self, dc=0):
        # If PWM is started, LED will go off when it goes out of scope
        self.blue_pwm.start(dc)
        self.green_pwm.start(dc)
        self.red_pwm.start(dc)

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
            
    # Simple LED controls without using PWM

    def color_red(self, exclusive=True):
        if exclusive:
            self.off()
        GPIO.output (self.red, GPIO.HIGH)

    def color_green(self, exclusive=True):
        if exclusive:
            self.off()
        GPIO.output (self.green, GPIO.HIGH)
        
    def color_blue(self, exclusive=True):
        if exclusive:
            self.off()
        GPIO.output (self.blue, GPIO.HIGH)
        
    def off(self):
        GPIO.output (self.red, GPIO.LOW)
        GPIO.output (self.green, GPIO.LOW)
        GPIO.output (self.blue, GPIO.LOW)

if __name__ == "__main__":
    GPIO.setmode (GPIO.BCM)
    led = RGBled(23, 25, 7)
    led.color_red()

    time.sleep(2)
    led.color_green()

    time.sleep(2)
    led.color_blue()

    time.sleep(2)
    led.color_red(exclusive=False)
    
    time.sleep(2)
