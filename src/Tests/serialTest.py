import serial,serial.tools.list_ports

serial_port="/dev/tty.usbserial-A5029QQH"     #  rainduino on the mac  
    

source = serial.Serial()

source.port=serial_port
source.baudrate=115200

# wait for opening the serial connection.
try:
    source.open()
except:
    print " Unable to open serial connection on ",serial_port
    raise

print " OPen OK"
while True:
    print source.readline()