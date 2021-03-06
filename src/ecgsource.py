import threading
import serial,serial.tools.list_ports
import time
from const import  *

""" 
Make a stream from a whole directory of files 
"""
 
class MultiFileStream:
    
    def __init__(self,data_files,file_name_client,dt=0):
    
        import glob
        self.client=file_name_client
        self.dt=dt
        self.fn_iter=glob.glob(data_files).__iter__()
        self.fin=None
        self.next_file()
        
    def next_file(self):
        
        print " NEXT FILE  . . ."
        if self.fin:
            self.fin.close()
     
        try:
            self.file_name=self.fn_iter.next()
            print self.file_name
            if self.client:
                self.client.notify(self.file_name)
     
        except StopIteration:
            print " No more data files"
            self.fin=None
            self.file_name=None
            raise
            
    
        if self.file_name:
            print " opening", self.file_name
            self.fin=open(self.file_name,"r")
            
            if not self.fin:
                print "oops could not open"
        else:   
            self.fin=None
        
    def readline(self):
        
        if self.dt > 0:
            time.sleep(self.dt)
            
        if self.fin == None:
            return None
        
        while True:
            line=self.fin.readline()
            if line:
                return line
            
            self.next_file()
            
            if not self.fin:
                return None
            
            
     
       
            

class EcgSource (threading.Thread):
    
    
    LIVE,LIVE_RECORD,FILE,FILE_LIVE=range(4)
    
    def __init__(self,processor,mutex,mode,data_files=None,new_file_client=None,tag=None):
        
        threading.Thread.__init__(self)
#         self.mode=mode
        self.fout=None
        self.mutex=mutex
        self.processor=processor
        # MUTEX for gui and data processing synschronization
  
        #  mode 0 - OFFLINE scans all test_data  recordings
        #       1- online using USB to grab realtime data from arduino + SCG shild
    
        self.Record=False
        
        serial.tools.list_ports.main()
        
         
        self.fout=None
        self.Replay=False
        self.file_mode=False
        
        #self.controlller=controller
        
        #  Set up ECG input dpending on mode
        if mode == EcgSource.FILE or mode == EcgSource.FILE_LIVE:
            
            class Client:
                
                def notify(self,name):
                    global caption
                    caption=name
            
            if mode == EcgSource.FILE_LIVE:
                dt=DT/2
                self.Replay=False
          
            else:
                dt=0
                self.Replay=True
               
            if new_file_client==None:
                new_file_client=Client()
                          
            source=MultiFileStream(data_files,new_file_client,dt)
            
            self.file_mode=True
            
            
        elif mode == EcgSource.LIVE or mode == EcgSource.LIVE_RECORD:
        
            if mode == EcgSource.LIVE_RECORD:
                file_name="data/"+tag+"_"+time.strftime("%b%d_%H_%M_%S")+".txt"
                self.fout=open(file_name,"w")    
                
        
            source = serial.Serial()
            
            source.port=SERIAL_PORT
            source.baudrate=BAUD_RATE
            
            # wait for opening the serial connection.
            try:
                source.open()
            except:
                print " Unable to open serial connection on ",SERIAL_PORT
                raise
        
            print " Using USB serial input ",SERIAL_PORT
        
        self.source=source
       
    # Read ECG values and feed the processor
    def run(self):
       
       
     
        # Maximium value for raw ECG stream    
        fullScale=1024
        
        # dc should be half fullScale
        ref=fullScale/2.0    
            
        
        count=0
        valLast=0    #  just used to do a crude down sampling 400Hz --> 200Hz
        self.stopped=False
        
        while not self.stopped:
            
            try:
                response=self.source.readline()
            except StopIteration:
                return
#             print response
            
            if response=="":
                continue
            
            if self.fout:
                self.fout.write(response)
                
            try:
                raw=float(response)
            except:
                print "error",response
                continue
    
            # map onto a -1  to +1 range            
            val=(raw-ref)/fullScale  
            
            # crude down sampler  400 Hz --> 200 Hz
            if (count % 2) == 0:
                val=(val+valLast)*0.5
                count += 1
            else:
                valLast=val
                count +=1
                continue
       
            self.processor.process(val,self.Replay,self)
            
        print " THREAD QUITTING "
            
    def quit(self):
        
        print " ASK ECG TRHEAD TO QUIT "
        
        self.stopped=True
        
        
        # join thread to avoid hanging pythons
        self.join()
        
        print " ECG THREAD QUIT "
        
        if self.fout:
            self.fout.close()
  
    def get_caption(self):
        if self.file_mode:
            return self.source.file_name
        else:
            return " LIVE "
        
if __name__ == "__main__":

    class Client:
        
        def process(self,val,replay,client):
            print val
                
    ecg_src=EcgSource(Client(),threading.Lock(),mode=EcgSource.LIVE)
    
    ecg_src.run()
    
     
         