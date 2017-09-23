import chaintool
print("Finding hashrate....")
b=chaintool.Block("getHashes/s",difficulty=int((2**chaintool.bits)/80000))
t=chaintool.millis()
i=0
while not b.mineOnce():
    if(chaintool.millis()>(t+5000)):
        break
    i+=1
print("Hashrate: "+str(i/(chaintool.millis()-t))+" kH/s")
print("Ready to mine.")
chaintool.hashrate=i/(chaintool.millis()-t)
