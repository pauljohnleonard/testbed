    # define a message-handler function for the server to call.
import random,OSC

addr=("127.0.0.1",7110)

addr=("192.168.0.8",7110)

def default_handler(addr, tags, stuff, source):
        print "---"
        print "received new osc msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"
        
        
s = OSC.OSCServer(addr) # basic
s.addDefaultHandlers()
s.addMsgHandler("default", default_handler) # adding our function
import threading
st = threading.Thread( target = s.serve_forever )
st.start()

x=raw_input(" HIT CR TO QUIT ")
s.close()
