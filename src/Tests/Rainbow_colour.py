import serial,serial.tools.list_ports
import time
import pygame


serial.tools.list_ports.main()

serial_port="/dev/tty.usbserial-A5029QQH"     #  rainduino on the mac  
    
serial_port="/dev/tty.usbserial-A7036HII"

source = serial.Serial()
source.port=serial_port
source.baudrate=31250

# wait for opening the serial connection.
try:
    source.open()
except:
    print " Unable to open serial connection on ",serial_port
    raise

print " Open OK"

COLOUR=1
FILL=2

col=pygame.Color(0)


cols=(b'\1\xFF\0\0\2',b'\1\0\xFF\0\2',b'\1\0\0\xFF\2')

colcmd=bytearray(b'\1\xFF\0\0\2')

print cols

cnt=0
max_cnt=100;

while True:

    hue=(360*cnt)/max_cnt;
    col.hsva=(hue,100,100,100)
    
    colcmd[1]=col.r
    colcmd[2]=col.b
    colcmd[3]=col.g
        
    source.write(colcmd)
    cnt = (cnt+1)%max_cnt
    time.sleep(0.05)