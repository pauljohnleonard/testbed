from pyo import *
import time
srate=44100.0
chunkSize=2048
s=Server(sr=srate,duplex=0,buffersize=chunkSize).boot().start()
file_name="../../samples/HARP_PENTA.aif"

period=4
dur=3
n=33
samps=[]

for i in range(n):
    samps.append(SfPlayer(file_name,offset=max(0,period*i),mul=1).stop())

mix=Mix(samps,voices=2).out()

def play(i):
    samps[i].play(dur=dur)

def test():
    for i  in range(len(samps)):
        play(i)
        time.sleep(1.0)
    
def pp(address, *args):
    ii=int(args[0])
    ii -= 50
    ii=min(max(0,ii),n-1)
    play(ii)
   
b = OscDataReceive(7110, "/heartrate", pp)

s.gui(locals())