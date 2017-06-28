import time, os, hashlib, threading, socket
ips=['127.0.0.1']
ports=[19200]#, 19201] # a common baud rate XD


save_main=False# save main blockchain?
save_sub=False # save daughter blocks?
full_node=True # run a full node?

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
current_data=""
current_age=millis()
class Block:
    def __init__(self, data, miner=0, lsblock=TopBlock, difficulty=None):
        global allblocks
        self.data=data
        self.lsblock=lsblock
        self.miner=miner
        if difficulty!=None:
            self.difficulty=min(int(((2**bits)-1)/difficulty),(2**bits)-1)
        if self.lsblock==None:
            self.lshash=0
            if difficulty==None:
                self.difficulty=int((2**bits)/400000)
        else:
            self.lshash=self.lsblock.hash
            if difficulty==None:
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
    def unpack(self,data):
        self.hash=int.from_bytes(data[:length],'little')
        data=data[length:]
        self.lshash=int.from_bytes(data[:length],'little')
        data=data[length:]
        self.miner=int.from_bytes(data[:16],'little')
        data=data[16:]
        self.time=int.from_bytes(data[:8],'little')
        data=data[8:]
        self.difficulty=int.from_bytes(data[:length],'little')
        data=data[length:]
        self.scratch=data[:length]
        self.data=data[length:].decode()
        self.validate()
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
    blocks.append(TopBlock)
    return TopBlock
def createDaughterBlock(newdata,cmt):
    global TopBlock
    daughter=Block(newdata, lsblock=TopBlock)
    mine(daughter)
    createBlock(cmt+":DAUGHTER"+str(myPublicKey.to_bytes(16, 'little'))+hex(daughter.hash))
    TopBlock.daughter=daughter
    return daughter
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
def client_thread(cs):
    index=0
    while True:
        data=b''
        length=0
        try:
            tmp=cs.recv(8)
            if not tmp:
                break
            elif tmp==b'PING':
                data=b'PING'
            else:
                length= int.from_bytes(tmp,'little')
        except:
            break
        while len(data)<length:
            data+=cs.recv(min(8192,length-len(data)))
        reply=b'DONE'
        if data==b"PING":
            print("Pinged.")
            reply=b'OK'
        elif data[:2]==b'I=':
            data=data[2:]
            index=int.from_bytes(data[:8],"little")
            reply=b'DONE'
            print("I set to "+str(index))
        elif data==b"GBLK":
            print("Block requested.")
            if len(blocks)>index:
                chunk=blocks[index].pack()
            else:
                chunk=b"NONE"
            reply=chunk
            reply=len(reply).to_bytes(8, 'little')+reply
        #print("response start: "+reply.decode())
        cs.sendall(reply)
    print("A client has disconnected.")
    cs.close()
def start_new_thread(a, b):
    what=threading.Thread(target=a, args=b)
    what.start()
def server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    try:
        s.bind(('', port))
        print("Node on port "+str(port)+" started.")
    except:
        print("Cannot run 2 nodes on same machine.")
        return
    # become a server socket
    s.listen(5)
    while True:
        (cs, adr) = s.accept()
        print("CONNECTED: "+adr[0]+':'+str(adr[1]))
        start_new_thread(client_thread ,(cs,))
class Client():
    def __init__(self, ip, port):
        self.ip=ip
        self.conn=socket.socket()
        self.conn.connect((ip, port))
        self.conn.sendall(b"PING")
        if self.conn.recv(10).decode()!='OK':
            print("ERROR: "+str(ip)+" is not a node.")
            self.conn.close()
        else:
            print("Node discovered: "+ip+':'+str(port))
    def avsend(self, data):
        self.conn.sendall(len(data).to_bytes(8, 'little'))
        self.conn.sendall(data)
    def avrec(self):
        data=b''
        length=0
        tmp=self.conn.recv(8)
        length=int.from_bytes(tmp,'little')
        while len(data)<length:
            data+=self.conn.recv(min(8192,length-len(data)))
        return data
    def getOneBlock(self):
        self.avsend(b'I='+len(blocks).to_bytes(length,'little'))
        if self.conn.recv(4)!=b'DONE':
            print("ERROR: Node "+self.ip+" is no longer valid.")
            return True
        self.avsend(b'GBLK')
        tmp=self.avrec()
        if tmp==b'NONE':
            return True
        else:
            blk=Block('')
            blk.unpack(tmp)
            blk.lshash=blocks[len(blocks)-1].hash
            if blk.validate():
                print("Downloaded block "+hex(blk.hash))
                blocks.append(blk)
        return False
    def downloadAll(self):
        print("Node "+self.ip+" downloading all blocks...")
        while not self.getOneBlock():
            pass
        print("Node "+self.ip+" hasn't yet any more blocks.")
FirstBlock=Block("Who says data can't outlive its owners?",difficulty=1, miner=hash(11))
FirstBlock.scratch=bytes(length)
blocks=[FirstBlock]
nodes=[]
for i in ips:
    for x in ports:
        sok=socket.socket()
        try:
            nodes.append(Client(i,x))
        except:
            pass
if full_node:
    for port in ports:
        th=threading.Thread(target=server, args=(port,))
        th.start()
print("Downloading...")
for i in nodes:
    i.downloadAll()
print("Done.")
while True:
    pass
