import pygame,threading,time,numpy,sys
import fontManager
from filters import *
from process import *
# from IO import *
from const import *
import ecgsource
import sonifyOSC
import spectral
import visify


DRAW_RAW_ECG=False     # don't display raw ECG data

# PATH for reading from file. you can use *
data_files="data_good/PJL-GOOD*"


# 4 modes avialable
# FILE        -- read from file with pauses (hold sapce down for fast)
# FILE_LIVE   -- no pause (just like doing it LIVE but from file
# LIVE        -- use arduino ECG stone
# LIVE_RECORD -- record LIVE session (prompts for a tag)
 
mode=ecgsource.EcgSource.FILE_LIVE

tag=None

if mode ==  ecgsource.EcgSource.LIVE_RECORD:
    print " Enter tag "
    tag=raw_input()
    print tag

#-------------------------------------------------------------------------------    
# feedback=FeedBack(target_hrv=TARGET_HRV,srate=INTERPOLATOR_SRATE)
# interpolator=Interpolator(srate=INTERPOLATOR_SRATE,client=None)

#  Signal flow
#
#  ECG at 200Hz  -->  
#  processor    (filter and create moving average ) -->     (moving average, time)  
#  peaker  ( identify RR peaks from processed ECG) -->      (peak_time,  magnitude)
#  TODO next is a mess refactoring needed
#  tachimeter  and   RRtoBPM ( convert intervals into BPM) --->             (bpm, peak_time)


# Clients must implement
# process(bpm,t,val)
  

clients=Clients()

try:
    clients.add(sonifyOSC.OSCSonify())
except:
    raise

visify=None  #visify.Visify()
#clients.add(visify)

spectralVarDT=spectral.SpectralVarDT(srate=3.2,nsamps=256)
clients.add(spectralVarDT.interpolator)
spectral=spectralVarDT.spectral

bpmfilt=BPMFilter(client=clients)
rrtobpm=RRtoBPM(median_filter_length=5,client=bpmfilt)
tachi=Tachiometer(median_filter_length=5,client=rrtobpm)
peaker=Peaker(client=tachi,dt=DT)
processor=Processor(peak_client=peaker,collector=None,dt=DT)


#        Display stuff
pygame.init()
clock=pygame.time.Clock()
modes=pygame.display.list_modes()
fontMgr = fontManager.cFontManager((('Courier New', 16), (None, 48), (None, 24), ('arial', 24)))

caption=" HIT ESCAPE TO QUIT"  

# Allocate screen space.

# full=modes[0]
# MAC puts puts screen below menu so take a bit off the height.
# dim_display=(full[0],full[1]-50)


height=720
width=1280

dim_display=(width,height)


#----------  0
#    ECG
#----------  y1
#
#----------  y2
#     BPM                        CHAOS
#----------- height   ----    |              |
#                             x1           width

y1=int(height/4)
y2=y1+int(height/6)

y12=y2-y1
y2h=height-y2

x1=width-y2h
x1w=y2h

dim_chaos=(x1w,y2h)
print dim_chaos

dim_ecg=(width,y1)
dim_bpm=(x1,y2h)
dim_spect=(width,y12)

display = pygame.display.set_mode(dim_display)

class ReadClient:   
    """
     Does the GUI control
     Handles values from the ECG stream.
     THis is called from the ECG thread so no gui stuff is allowed.
    """

    def __init__(self,processor,mutex):
        self.processor=processor
        self.mutex=mutex

        
    # Read ECG values and feed the processor
    def process(self,val,replay,server):
        
        global space_hit,peakPtr

      
        if ecg_display.is_full():
            if replay:
             
                print " Hit key to continue "
                         
                space_hit=False
                while not space_hit and not server.stopped:
                    time.sleep(0.1)
                space_hit=False
                
                self.mutex.acquire()       
                ecg_display.scroll(0.1)
                self.mutex.release()
           
            else:
            
                print " RESETING CNT"
                self.mutex.acquire()
                ecg_display.reset()
                self.mutex.release()
               
        mutex.acquire()       
         
        self.processor.process(val)
        
        ecg_display.add_points(processor)
        
      
        mutex.release()
        
class ECGDisplay:
    
    def __init__(self,surf):
          
        self.cnt=0
        self.surf=surf
        self.N=surf.get_width()
        N=surf.get_width()
        self.x_points=numpy.zeros(N,dtype='i')    #  time axis 
        
        for i in range(N):
            self.x_points[i]=i
        
        #  Y axis- displays
        self.ecg_points=numpy.zeros(N,dtype='i')    #  val of ECG
        self.filtered_ecg_points=numpy.zeros(N,dtype='i')    #  filtered ECG
        self.mv_av_points=numpy.zeros(N,dtype='i')    #  processed ECG
        self.threshold_points=numpy.zeros(N,dtype='i')    
        
        
        self.g_points=[self.ecg_points,self.filtered_ecg_points,self.mv_av_points,self.threshold_points]
        
        self.peakPtrStart=0
        self.timeLeft=0
        self.windowTime=DT*N
   
    def is_full(self):
       return self.cnt >= self.N
   
    #  scroll the  ECG by n samples 
    def scroll(self,fact):
        
        # scroll by n samples
        n=int(self.N*fact)
            
        i1=self.N-n
        for pts in self.g_points:
            pts[0:self.N-n]=pts[n:self.N]
        self.cnt -= n
        self.timeLeft = self.timeLeft+n*DT
            
        # This is not very clever Eventually will be a problem  . . .
        self.peakPtrStart=0
    
    def reset(self):
        self.cnt=0
        self.timeLeft=processor.time
        
    def draw(self):    
        self.surf.fill((0,0,0))
    
        if self.cnt > 2:
            cnt=self.cnt
            points2=numpy.column_stack((self.x_points,self.mv_av_points))
            points3=numpy.column_stack((self.x_points,self.threshold_points))
            points4=numpy.column_stack((self.x_points,self.filtered_ecg_points))
            
            if DRAW_RAW_ECG:
                points1=numpy.column_stack((self.x_points,self.ecg_points))
                pygame.draw.lines(ecg_surf, (0,255,0), False, points1[:(cnt-1)])
            
            pygame.draw.lines(ecg_surf, (0,0,255), False, points2[:(cnt-1)])
            pygame.draw.lines(ecg_surf, (255,0,255), False, points4[:(cnt-1)],3)
            pygame.draw.lines(ecg_surf, (150,0,0), False, points3[:(cnt-1)])
     
        n=len(tachi.RR)
        
        
        peakPtr=self.peakPtrStart
      
        # medPtLast=None
        
        while peakPtr<n:
            
            t=tachi.RR[peakPtr][0]
            dTime=t - self.timeLeft
            
            if dTime < 0:
                self.peakPtrStart += 1
                peakPtr += 1
            elif dTime > self.windowTime:
                break
            else:
                xi=int(dTime/processor.dt)
                yi=self.val2Screen(tachi.RR[peakPtr][1])
                #med=self.val2Screen(tachi.RRmed[peakPtr][1])
                col=RRstate.color[tachi.RR[peakPtr][2]]
                
                #if medPtLast != None:
                #    pygame.draw.line(ecg_surf,(255,255,255),medPtLast,(xi,med))
                    
                #medPtLast=(xi,med)
                pygame.draw.rect(ecg_surf,col,(xi,yi,4,dim_ecg[1]-yi))
                peakPtr += 1
        
        
            
    def add_points(self,processor):
        self.ecg_points[self.cnt]=self.ecg2screen(processor.y_val)
        self.filtered_ecg_points[self.cnt]=self.f2screen(processor.f_val)
        self.threshold_points[self.cnt]=self.val2Screen(peaker.thresh1)        
        self.mv_av_points[self.cnt]=self.val2Screen(processor.s_val)
        self.cnt  += 1
        
    def f2screen(self,val):
        """ 
        map value -640-640  to the height
        """
        return dim_ecg[1]*0.5*(.8-val/500.0) 
    
    def ecg2screen(self,val):
        """
        map val in range -1 to 1 to screen
        """
        return dim_ecg[1]*0.5*(1-val) 
                      
    def val2Screen(self,val):
            # moving average to screen value 
            return dim_ecg[1]*(1.0-val/MAX_MV_AV)

class BPMDisplay:
    
    KEY_WIDTH=40
    
    def __init__(self,surf_bpm,surf_chaos):
           # BPM
        self.bpmScreenPtLast=None
        self.surf_bpm=surf_bpm
        self.surf_chaos=surf_chaos
        self.bpmPtr=0
        self.bpm_background=(50,50,50)
        self.surf_bpm.fill(self.bpm_background)
        self.xBPMright=int((surf_bpm.get_width()*6)/6)-1
        self.xBPM_ref=-BPMDisplay.KEY_WIDTH
    # map bpm to pixels
        self.tBPMscale=10
        self.draw_bpm_key(0,0,0)
        
        #  Chaos window
        self.chaos_last=None
        breath_per_min=10.0
        
        # t*target_hrv_scale      should give 1 per breath
        self.breath_period = 60.0/breath_per_min 
        self.bpmLast=BPMFilter
        self.bpmLast=DEFAULT_BPM
     
    def t2screen(self,t):
        return int(t*self.tBPMscale)-self.xBPM_ref
     

    def bpm2screen(self,bpm):
        H=self.surf_bpm.get_height()
        return int(H-(bpm-BPM_MIN_DISP)*H/(BPM_MAX_DISP-BPM_MIN_DISP))
          
    def t_bpm2screen(self,t,bpm):
        H=self.surf_bpm.get_height()
        return [self.t2screen(t),self.bpm2screen(bpm)]
    
    def draw_bpm_key(self,bpmVal,bpmAv,bpmAvF):
        
        bpmLine=40
        
        pygame.draw.rect(self.surf_bpm,(0,0,0),(0,0,BPMDisplay.KEY_WIDTH, self.surf_bpm.get_height()))
       
        y=self.bpm2screen(bpmVal)
        
        pygame.draw.rect(self.surf_bpm,(0,0,255),(0,y,BPMDisplay.KEY_WIDTH,self.surf_bpm.get_height()))
      
        y=self.bpm2screen(bpmAv)
        
        pygame.draw.line(self.surf_bpm,(0,255,255),(0,y),(BPMDisplay.KEY_WIDTH,y),5)
      
        y=self.bpm2screen(bpmAvF)
        
        pygame.draw.line(self.surf_bpm,(255,255,0),(0,y),(BPMDisplay.KEY_WIDTH,y),5)
       
       
        while True:
          
          y=self.bpm2screen(bpmLine)
          if y < 0:
              break
          
          if y < dim_bpm[1]:
              ttt=str(bpmLine)
              fontMgr.Draw(self.surf_bpm, 'Courier New', 16, ttt, (0,y), (20,255,255))
          
          bpmLine+=5
        
    def draw_time_key(self):
        
        tt=int(math.ceil((self.xBPM_ref+BPMDisplay.KEY_WIDTH)/self.tBPMscale))
        wid=self.surf_bpm.get_width()
        h=self.surf_bpm.get_height()
        
        while True:
            if tt % 10 == 0:
                xx=self.t2screen(tt)
                if xx > wid:
                    return
                pygame.draw.line(self.surf_bpm,(0,0,0),(xx,0),(xx,h-15))
                str = " {}:{:0>2d}".format((tt/60),tt%60)
      
                fontMgr.Draw(self.surf_bpm, 'Courier New', 16, str, (xx-30,h-15), (60,255,255))
    
            tt+=1
            
    
    def draw(self):
        
       # PLOT the BPM based values ------------------------------------------------------------
        
           
        while self.bpmPtr < len(bpmfilt.BPMfilt):
            
            
#             bpmNew=rrtobpm.BPMraw[self.bpmPtr][1]
#             timeNew=rrtobpm.BPMraw[self.bpmPtr][0]
#             

            bpmNew=bpmfilt.BPMfilt[self.bpmPtr][1]
            timeNew=bpmfilt.BPMfilt[self.bpmPtr][0]
             
            xNew,tmp=self.t_bpm2screen(timeNew,bpmNew)
            
            xOver = xNew-self.xBPMright
            
            if xOver > 0 :
                self.xBPM_ref += xOver
                bpm_surf.scroll(-xOver)
                pygame.draw.rect(self.surf_bpm,self.bpm_background,(self.xBPMright-xOver+1,0,xOver,self.surf_bpm.get_height()))
                self.bpmScreenPtLast[0] -= xOver
                
                
            self.draw_bpm_key(bpmNew,bpmfilt.average,bpmfilt.average_fast)
             
            
            bpmScreenPtNew=self.t_bpm2screen(timeNew,bpmNew)
            chaos_new=None
            
            if self.bpmScreenPtLast != None:
                pygame.draw.line(bpm_surf,(0,255,0),self.bpmScreenPtLast,bpmScreenPtNew,5)
                chaos_new=(self.bpmScreenPtLast[1],bpmScreenPtNew[1])
             
            bpmAv=bpmfilt.average_fast   
            ptAv=self.bpm2screen(bpmfilt.average)
            pt=[ptAv,ptAv]
            
       
            if self.chaos_last != None:
                chaos_surf.fill((250,250,250),special_flags=pygame.BLEND_MULT)
                col=self.chaos_color_at3(bpmAv,self.bpmLast,bpmNew)
                pygame.draw.line(self.surf_chaos,col,self.chaos_last,chaos_new,15)
                
                pygame.draw.circle(self.surf_chaos,col,pt,5)
                if visify:
                    visify.set_colour(col.r,col.g,col.b)
               
                        
            self.bpmLast=bpmNew
            self.bpmScreenPtLast=bpmScreenPtNew
            self.chaos_last=chaos_new
            self.bpmPtr += 1
            self.draw_time_key()
            
    def chaos_color_at3(self,av,bpmLast,bpmNow):
        dx=bpmNow-av
        dy=bpmLast-av
        hue=(int(math.atan2(dx,dy)*180.0/math.pi)+180+120)%360
        col=pygame.Color(0)
        sat=min(100,int(math.sqrt(dx*dx+dy*dy))*100.0/10.0)
        sat=max(0,sat)
        #sat=100
        hue=min(360,hue)
        hue=max(0,hue)
        col.hsva=(hue,sat,100,100)
        return col
    
   
    def chaos_color_at2(self,t):
        """
        Modulate the colour of chaos line
        """
        i=(t/self.breath_period*512)%512
        
        if i > 256:
            i=512-i
            
        return (i,0,256-i)
    
  
    def chaos_color_at(self,t):
        """
        Modulate the colour of chaos line
        """
        
        
        hue=int(t*7)%360
        col=pygame.Color(255,255,255)
        col.hsva=(hue,100,100,100)
        return col
    
class SpectralDisplay:
    
    
    def __init__(self,surf,spectral):
        self.surf=surf
        self.spectral=spectral
        
        
    def draw(self):
        if self.spectral.XX == None:
            return
             
        self.surf.fill((0,0,0))
        
        n=self.surf.get_height()
        wid=self.surf.get_width()
          
        cnt=0
        fact=0.2
        XX=self.spectral.XX
        freqs=self.spectral.freqBin
        
        cnt=0
        WID=20
        WIDO2=WID/2
        str=""
        for xx in XX:
            
            val=abs(xx)
            val=val*fact
            fBin=self.spectral.freqBin[cnt]
            if fBin < RESFREQ_MIN:
                col=C_LOW
            elif fBin < RESFREQ_MID:
                fact1=(RESFREQ_MID-fBin)/(RESFREQ_MID-RESFREQ_MIN)
                fact2=1.0-fact1
                r=C_LOW[0]*fact1+C_MID[0]*fact2
                g=C_LOW[1]*fact1+C_MID[1]*fact2
                b=C_LOW[2]*fact1+C_MID[2]*fact2
                col=(r,g,b)
            elif self.spectral.freqBin[cnt] < RESFREQ_MAX:
                fact1=(RESFREQ_MID-fBin)/(RESFREQ_MID-RESFREQ_MAX)
                fact2=1.0-fact1
                r=C_HIGH[0]*fact1+C_MID[0]*fact2
                g=C_HIGH[1]*fact1+C_MID[1]*fact2
                b=C_HIGH[2]*fact1+C_MID[2]*fact2
                col=(r,g,b)
            else:
                col=C_HIGH
#             else:
#                 str+= "%3.2f "      % (spectral.freqs[cnt]*60)
#                 col=(255,255,0)
#                 
            pygame.draw.line(self.surf,col,(cnt*WID+WIDO2,n-1),(cnt*WID+WIDO2,n-val),WID-1)
        
           # fontMgr.Draw(self.surf, 'Courier New', 16, str, (wid-400,0), (60,255,255))
            cnt+=1
            if cnt*WID> wid:
                break
            
            
#  GUI stuff ---------------------------------------------------------


ecg_surf=pygame.Surface(dim_ecg)
ecg_display=ECGDisplay(ecg_surf)

chaos_surf=pygame.Surface(dim_chaos,flags=pygame.SRCALPHA)
bpm_surf=pygame.Surface(dim_bpm)
bpm_display=BPMDisplay(bpm_surf,chaos_surf)

spect_surf=pygame.Surface(dim_spect)
spect_display=SpectralDisplay(spect_surf,spectral)
         
#  read ecg on a seperate thread feeding into the processor
#  DON'T DO ANY GUI STUFF ON THIS THREAD
#  aquire the lock before playing around with and display data
mutex=threading.Lock()
 
read_client=ReadClient(processor,mutex)

ecg_src=ecgsource.EcgSource(read_client,mutex,mode=mode,data_files=data_files,new_file_client=None,tag=tag)

ecg_src.start()
 

"""
main gui loop
"""
while True:
      
#  Display the caption if set.
    if caption != ecg_src.get_caption() :
        caption=ecg_src.get_caption()
        pygame.display.set_caption(caption)
        caption=None
         
    k = pygame.key.get_pressed()
    
    if k[pygame.K_ESCAPE] or pygame.event.peek(pygame.QUIT):
        space_hit=True
        time.sleep(.2)
        ecg_src.quit()
        pygame.quit()
        break
    
    if k[pygame.K_SPACE]:
        space_hit=True
        
    
    # Make sure the data does not get tweaked during disply.
    ecg_src.mutex.acquire()
    
    # ECG based values  --------------------------------------------------
    
    ecg_display.draw()
    bpm_display.draw()     
    spect_display.draw()
    
    ecg_src.mutex.release()
   
    
    display.blit(ecg_display.surf,(0,0))
    display.blit(bpm_surf,(0,y2))
    display.blit(chaos_surf,(x1,y2))
    display.blit(spect_surf,(0,y1))

    pygame.display.flip()
    clock.tick(FPS)