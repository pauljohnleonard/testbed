from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt


app = QtGui.QApplication([])
view = pg.GraphicsView()

l = pg.GraphicsLayout(border=(100,100,100))
view.setCentralItem(l)
view.show()
view.setWindowTitle('ECG -- display')
view.resize(1100,800)



# 120 samples at 200 Hz  =    60/(120/200) = 100 bpm
nSampL=20
nSampR=140
nSamps=nSampR-nSampL


names=QtGui.QFileDialog.getOpenFileNames(directory='../data_qrs')
name=names[0]
view.setWindowTitle(name)

def read_data(file_name):
    global nSamps
    fin=open(file_name,"r")
    
    qrs_array=[]
    qrs=None
    
    while True:
        line=fin.readline()
        if not line:
            break
        
        toks=line.split()
        
        for tok in toks:
#             print "TOK",tok
            if tok[0] == "[":
                cnt=0
                qrs=np.zeros(nSamps)
#                 print " CEEATE ARRAY",qrs,nSamps
                qrs_array.append(qrs)
                    
            elif tok[0] == "]":
                continue
            
            else:
                if cnt >= nSampL and cnt < nSampR :
                    qrs[cnt-nSampL]=float(tok)
            cnt+=1
            
    fin.close()
    return qrs_array


    
def normalize_list(qrs_list,order):

    for qrs in qrs_list:
        qrs /= np.linalg.norm(qrs,order)
        
    
def filt_list(qrs_list,thresh):
    """
    remove outliers from the list of qrs samples
    """
    
    q_av=np.average(qrs_list,axis=0)
    
    d_q=np.absolute(qrs_list-q_av)
    
    d_q_max=np.amax(d_q,axis=1)
    
    qrs_ok=[]
    qrs_reject=[]
    
    for d_q,qrs in zip(d_q_max,qrs_list):
        if d_q > thresh:
            qrs_reject.append(qrs)
        else:
            qrs_ok.append(qrs)
        
    
    qrs_average=np.average(qrs_ok,axis=0)
    
    return qrs_ok,qrs_reject,(qrs_average,)
    
    
    
    

qrs_data=[]

norm=[np.inf,.1]
norm=[0.5,.00008]

qq_all=[]
qq_all_names=[]   
for name in names:
    print " reading ", name
    qrs_list=read_data(name)
#    qrs_data.append((name,qrs_list))
    name=(name.split("/")[-1]).split(".")[0]
    
    if len(names) == 1:
        qq=np.copy(qrs_list)       
        normalize_list(qq,norm[0])
        qrs_data.append(("noramalized",qq))
       
        np.copy(qq)       
        qq_ok,qq_reject,qq_aver=filt_list(qq,norm[1])
        qrs_data.append(("OK",qq_ok))
        qrs_data.append(("REJECT",qq_reject))
        qrs_data.append(("AVER",qq_aver))
    
    else:
        normalize_list(qrs_list,norm[0])    
        qq_ok,qq_reject,qq_aver=filt_list(qrs_list,norm[1])        
        #qrs_data.append((name,qq_aver))
        qq_all.append(qq_aver[0])
        qq_all_names.append(name)
        # qrs_data.append(("REJECT",qq_reject))
        
if len(names)>1:
    qrs_data.append(("ALL",qq_all))

t=np.zeros(nSamps)
for i in range(nSamps):
     t[i]=(i-42)/.2

ppref=None

for i,data in enumerate(qrs_data):
    
    qrs_array=data[1]
    
    l.nextRow()
    l2 = l.addLayout(colspan=1, border=(10,0,0))
    l2.setContentsMargins(0, 0, 0, 10)
    
    pp = l2.addPlot(title=(data[0].split("/")[-1]).split(".")[0])
    if len(names)>0:
        pp.addLegend()
        
    n=len(qrs_array)
    for i,qrs in enumerate(qrs_array):
        if len(qq_all_names) > 0:
            pp.plot(t,qrs,pen=pg.intColor(i,n),name=qq_all_names[i])
        else:
            pp.plot(t,qrs,pen=pg.intColor(i,n))
        
    pp.showGrid(x=True,y=True,alpha=.9)
    if ppref == None:
        ppref=pp
    else:
        pp.setXLink(ppref)  

## Start Qt event loop unless running in interactive mode.

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
