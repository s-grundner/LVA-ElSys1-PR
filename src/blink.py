from umachine import Pin
import time
import umachine
umachine.freq(int(50e6)) # reduce power consumption

led_num = 1 # 1...9
seg1 = PIN(f'LED{led_num}', Pin.OUT)

while True:
    seg1.on()
    time.sleep(0.1)
    seg1.off()
    time.sleep(0.1)
