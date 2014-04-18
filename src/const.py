MAC_LEO,MAC_NANO=range(2)
HOST=MAC_LEO


#BAUD_RATE=115200
#SERIAL_PORT="/dev/tty.usbserial-A5029QQH"

if HOST == MAC_LEO:
    BAUD_RATE=9600
    SERIAL_PORT="/dev/tty.usbmodem1411"     #  RIGHT on mac air
elif HIST == MAC_NANO:
    # NANO
    BAUD_RATE=115200
    SERIAL_PORT="/dev/tty.usbserial-14P02242"

#  ---------------  SERIAL PORT FOR ECG -----------
# WINDOWS      does this work with the leonardo? Does not report the port in the list.
#serial_port='COM4'

# MAC
# serial_port="/dev/tty.usbmodem1421"   #  LEFT on mac air
#   serial_port="/dev/tty.usbserial-A5029QQH"     #  rainduino on the mac      
#   serial.port=serial_port

# ubuntu
#ser_port = "/dev/ttyACM0"          

#  serial.port=SERIAL_PORT
     

DT  = 1./200         #  ECG sample rate


TARGET_HRV=0.1           # target HRV in Hertz  0.1 is 6 breadths per minute
INTERPOLATOR_SRATE=3.2   # resampled HRV sample rate in Hertz


#  GUI STUFF
BPM_MIN_DISP=45
BPM_MAX_DISP=110


#  BPM stuff

DEFAULT_BPM=70.0         #  fall back BPM if we get stuck
MAX_BPM=120.0            # maximum possible physically HR
MIN_BPM=40.0             # minimum  "      ....
MAX_DELTA_BPM=50         #  Maximum change in one beat
MAX_DEVIATION_BPM=30     #  Maximum swing from median value
N_MEDIAN_BPM=20          #   NO of beats in Median filter to  ignore glitches 

FPS = 30             # pygame frames per second refresh rate.


# range of breath frequencies for Spectral Display
RESFREQ_MIN=2/60.0
RESFREQ_MID=6/60.0
RESFREQ_MAX=10/60.0

C_LOW=(0,0,200)
C_MID=(0,255,0)
C_HIGH=(150,0,0)

#  PEAK DETECION TUNABLE PARAMETERS
#     thresh1=DELAY( MovingAverage( min(ecg,MAX_MV_AV)*THRESH_SCALE ) )   

#THRESH_HALF_LIFE=0.2   #   time for moving average to decay to half it's value 
THRESH_HALF_LIFE=0.4   #   time for moving average to decay to half it's value 
THRESH_SCALE=2.0       #   scale the threshold value (decrease to make more sensitive)
MAX_MV_AV=3000         #   Clip MOving average at this value.
THRESH_DELAY=42        #   DELAY time