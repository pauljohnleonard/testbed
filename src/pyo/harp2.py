from pyo import *
import time
srate=44100.0
chunkSize=2048
s=Server(sr=srate,duplex=0,buffersize=chunkSize).boot().start()
file_name="../../samples/HARP_PENTA.aif"

period=4
dur=3.9
n=33
trigs=[]
envs=[]


for i in range(n):
    start=period*i
    stop=start+4.0 
    table=SndTable(file_name,start=start,stop=stop)
    trig=Trig().stop()
    trigs.append(trig)
    env=TrigEnv(trig,table,dur=dur)
    envs.append(env)

mix=Mix(envs,voices=2).out()

def play(i):
    trigs[i].play()

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