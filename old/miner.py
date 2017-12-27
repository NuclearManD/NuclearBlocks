import chaintool, threading, time
print("Finding hashrate....")
chaintool.node_limit=1 # accept only from one node
chaintool.nodes=[]
chaintool.start()
millis=chaintool.millis
b=chaintool.Block("getHashes/s",difficulty=int((2**chaintool.bits)/800000))
t=millis()
i=0
while not b.mineOnce():
    if(chaintool.millis()>(t+5000)):
        break
    i+=1
print("Hashrate: "+str(i/(chaintool.millis()-t))+" kH/s")
print("Ready to mine.")
chaintool.hashrate=i/(chaintool.millis()-t)
block=None
def get_job():
    global block
    while True:
        try:
            block = chaintool.nodes[0].wait_for_mine()
            print("Received new mining job...")
        except:
            time.sleep(0.5)
            chaintool.nodes=[]
            chaintool.get_nodes()
threading.Thread(target=get_job).start()
while True:
    timer=millis()+1000
    cnt=millis()
    off=0
    while block!=None:
        if(millis()>timer):
            timer=millis()+1000
            print(str(int((i-off)/(millis()-cnt)))+" kH/s")
            cnt=millis()
            off=i
        if(block!=None and block.mineOnce()):
            chaintool.nodes[0].submit(block)
            print("Solved block with hash "+hex(block.hash))
            block=None
        i+=1
