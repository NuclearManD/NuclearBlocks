import time, os, hashlib
millis = lambda: int(round(time.time() * 1000))
FirstBlock=None
TopBlock=None
bits=256
myPrivateKey=0x115200
allblocks=[]
def HASH(data, bits=bits):
    j=hashlib.sha256(data)
    out=int(j.hexdigest(),16)
    out&=(2**bits)-1
    return out
myPublicKey=HASH(myPrivateKey.to_bytes(32, 'little'),128)
print("Public Key: "+hex(myPublicKey))
length=int(bits/8)
class Block:
    def __init__(self, data, miner=0, lsblock=TopBlock, difficulty=None):
        global allblocks
        self.data=data
        self.lsblock=lsblock
        self.difficulty=difficulty
        self.miner=miner
        if self.lsblock==None:
            self.lshash=0
            self.difficulty=int((2**bits)/400000)
        else:
            self.lshash=self.lsblock.hash
            if self.difficulty==None:
                self.difficulty=lsblock.difficulty
        self.time=int(time.time()) # EPOCH time!
        self.scratch=bytes(length)
        self.daughter=None
        self.nextBlock=None
        self.hash=0
        self.isValid=False
        allblocks.append(self)
    def gen_header(self):
        self.header=self.lshash.to_bytes(length, 'little')
        self.header+=self.miner.to_bytes(16, 'little')
        self.header+=self.time.to_bytes(8, 'little')
        self.header+=self.difficulty.to_bytes(length, 'little')
        self.header+=self.scratch
        return self.header
    def pack(self):
        self.hash_comp=self.getHash().to_bytes(length, 'little')
        self.result=self.hash_comp+self.gen_header()+bytes(self.data,"UTF-8")
        return self.result
    def getHash(self):
        self.hash=HASH(self.gen_header()+bytes(self.data,"UTF-8"))
        return self.hash
    def validate(self):
        self.isValid=self.getHash()<self.difficulty
        return self.isValid
    def mineOnce(self):
        if self.validate():
            return True
        self.miner=myPublicKey
        self.scratch=os.urandom(length)
        return self.validate()
def mine(block):
    i=0
    while not block.mineOnce():
        i+=1
    print("Took "+str(i)+" attempts to mine block with hash "+hex(block.hash))
def createBlock(newdata):
    global TopBlock
    if len(newdata)>4096:
        print("Block too big!")
        return
    TopBlock=Block(newdata, lsblock=TopBlock)
    mine(TopBlock)
    return TopBlock
def createDaughterBlock(newdata,cmt):
    global TopBlock
    daughter=Block(newdata, lsblock=TopBlock)
    mine(daughter)
    createBlock(cmt+":DAUGHTER"+str(myPublicKey.to_bytes(16, 'little'))+hex(daughter.hash))
    TopBlock.daughter=daughter
    return daughter
FirstBlock=createBlock("Who says data can't outlive its owners?")
current_data=""
current_age=millis()
def addData(data, cmt='uu'):
    global current_age, current_data
    if len(current_data+data)<(4096-(3*length+28)):
        current_data+=(hex(len(data))[2:]).zfill(4)+data
    elif len(data)<(4096-(3*length+28)):
        createBlock(current_data)
        current_data=(hex(len(data))[2:]).zfill(4)+data
        current_age=millis()
    else:
        daughter=Block(newdata, lsblock=TopBlock)
        mine(daughter)
        addData(cmt+":DAUGHTER"+str(myPublicKey.to_bytes(16, 'little'))+hex(daughter.hash))
    if len(current_data)+(3*length+24)>4090 or (current_age+300000<millis() and len(current_data>1024)):
        createBlock(current_data)
        current_data=""
        current_age=millis()
    
