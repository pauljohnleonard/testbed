# Interface to rainduino 8x8 LED display

import serial

class Visify:
    
       def __init__(self):
            
            serial_port="/dev/tty.usbserial-A5029QQH"     #  rainduino on the mac  
                
            serial_port="/dev/tty.usbserial-A7036HII"
            
            self.dev = serial.Serial()
            self.dev.port=serial_port
            self.dev.baudrate=19200
            
            # wait for opening the serial connection.
            try:
                self.dev.open()
            except:
                print " Unable to open serial connection on ",serial_port
                raise
          
       def process(self,bpm,t,val):
           print bpm,t
           
       def set_colour(self,r,g,b):
            colcmd=bytearray(b'\1\xFF\0\0\2')
        
            colcmd[1]=r
            colcmd[2]=b
            colcmd[3]=g
                
            self.dev.write(colcmd)
            
            
if __name__ == '__main__':
    
    import time,pygame

    cnt=0
    max_cnt=100;
    v=Visify()
    while True:
        
        hue=(360*cnt)/max_cnt;
        col=pygame.Color(0)
        col.hsva=(hue,100,100,100)
        v.set_colour(col.r, col.g, col.b)
        
        cnt = (cnt+1)%max_cnt
        time.sleep(0.05)

          
           
 