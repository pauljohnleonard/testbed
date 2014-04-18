# PLug in to send  heart beat events using OSC

# TO test this run test_OSC_server first

import sys
import OSC
import atexit
import numpy
import time

# addr=("127.0.0.1",7110)
       
addr=("192.168.0.8",7110)

class OSCSonify:
    
    def __init__(self):
        
        self.osc_client=OSC.OSCClient()
        
        try:
            self.osc_client.connect(addr)
            time.sleep(.1)
            msg=OSC.OSCMessage("/hello",0)
            
            self.osc_client.send(msg)
            msg=OSC.OSCMessage("/hello",0)
            time.sleep(.1)
            
            self.osc_client.send(msg)
        
            msg=OSC.OSCMessage("/hello",0)
            time.sleep(.1)
        
            self.osc_client.send(msg)
            print " CONNECT OK"
            
        except:
            print "Failed to connet "
            raise 
            
        
          
    def process(self,bpm,t,val):
        print bpm,t
        msg=OSC.OSCMessage("/heartrate",bpm)
        self.osc_client.send(msg)
        
    def quit(self):
        print " OSC sonify QUITTING "
        msg=OSC.OSCMessage("/quit")
        self.osc_client.send(msg)
        self.osc_client.close()
 

if __name__ == "__main__":
        # define a message-handler function for the server to call.
    import random
    
    sonify=OSCSonify()
    
    
    t=0
    val=0
    for _ in range(50):
        bpm=50+random.random()*40        
        sonify.process(bpm,t,val)
        time.sleep(.5)
        
    sonify.quit()
    time.sleep(0.5)
   