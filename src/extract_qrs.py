# TOP LEVEL
# parses raw ECG files and create QRS files

import threading,time,numpy,sys


from filters import *
from process import *
from IO import *
from const import *
import ecgsource
import classifier

# import voicebowl1

# SOURCE
#  FILE or LIVE to chnge from recored to using device.
data_files="data_good/JAN*"

# LIVE,LIVE_RECORD,FILE,FILE_LIVE=range(4)
  
# mode=ecgsource.EcgSource.LIVE
mode=ecgsource.EcgSource.FILE


# Clients must implement
# process(bpm,t,val)

pre_rr_samps=int(0.5/DT)
post_rr_samps=int(0.4/DT)

print pre_rr_samps+post_rr_samps

qrs_collector=classifier.QRSCollector(pre_rr=pre_rr_samps,post_rr=post_rr_samps,dir="data_qrs")

peaker=Peaker(client=None,dt=DT)
processor=Processor(peak_client=peaker,collector=qrs_collector,dt=DT)


class ReadClient:
    # Read ECG values and feed the processor
    def __init__(self,processor):
        self.processor=processor
        
    def process(self,val,replay,server):         
        self.processor.process(val)
        

read_client=ReadClient(processor)

ecg_src=ecgsource.EcgSource(read_client,mutex=None,mode=mode,data_files=data_files,new_file_client=qrs_collector)

ecg_src.run()
 
