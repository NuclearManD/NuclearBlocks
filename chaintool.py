import time, os, hashlib, threading, socket, pickle
ips=['127.0.0.1','192.168.1.132', '68.4.20.23']
ports=[19200]#, 19201] # a common baud rate XD
node_limit=20
can_mine=False
save_main=False# save main blockchain?
save_sub=False # save daughter blocks?
full_node=False # run a full node?
if input("Run Node? [Y/n]")=='Y':
    full_node=True
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
blocks=[]
daughter_blocks=[]
nodes=[]
class Block:
    def __init__(self, data, miner=0, lsblock=None, difficulty=None):
        global allblocks
        self.data=data
        self.lsblock=lsblock
        self.miner=miner
        if difficulty!=None:
            self.difficulty=min(int(((2**bits)-1)/difficulty),(2**bits)-1)
        if self.lsblock==None:
            if(len(blocks)>0 and blocks[len(blocks)-1].validate()):
                self.lsblock=blocks[len(blocks)-1]
                self.lshash=self.lsblock.hash
            else:
                self.lshash=0
            if difficulty==None:
                self.difficulty=int((2**bits)/400000)
        else:
            self.lshash=self.lsblock.hash
            if difficulty==None:
                self.difficulty=lsblock.difficulty
        self.time=int(time.time()) # EPOCH time!
        self.scratch=bytes(length)
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
    print("Mining a new block...")
    timer=millis()+1000
    cnt=millis()
    off=0
    while not block.mineOnce():
        if(millis()>timer):
            timer=millis()+1000
            print(str(int((i-off)/(millis()-cnt)))+" kH/s")
            cnt=millis()
            off=i
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
    daughter_blocks.append(daughter)
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
    if len(current_data)+(3*length+24)>4090 or (current_age+300000<millis() and len(current_data)>1024):
        createBlock(current_data)
        current_data=""
        current_age=millis()
def client_thread(cs, ip):
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
        elif data[:4]==b'FSB?':
            hsh=int.from_bytes(data[4:],'little')
            print("Getting daughter block with hash "+hex(hsh))
            for i in daughter_blocks:
                if i.hash==hsh:
                    reply=i.pack()
                    break
            if reply==b'DONE':
                reply=b'NONE'
            reply=len(reply).to_bytes(8, 'little')+reply
        elif data[:5]==b'NODES':
            print("Requested node list...")
            li=''
            for i in nodes:
                li+=i.ip+','
            reply=li[:-1].encode()
            reply=len(reply).to_bytes(8, 'little')+reply
        elif data[:5]==b'IAMNODE':
            print(ip+" is a node...")
            done=False
            for i in nodes:
                if i.ip==ip:
                    done=True
            if (not done) and len(nodes)<=node_limit:
                for i in ports:
                    nodes.append(Client(ip,i))
            reply=b'OK'
        #print("response start: "+reply.decode())
        cs.sendall(reply)
    print("A client has disconnected.")
    cs.close()
def start_new_thread(a, b):
    what=threading.Thread(target=a, args=b)
    what.start()
running_node=False
def server(port):
    global running_node
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    try:
        s.bind(('', port))
        print("Node on port "+str(port)+" started.")
        running_node=True
    except:
        print("Cannot run 2 nodes on same machine.")
        return
    # become a server socket
    s.listen(5)
    while True:
        (cs, adr) = s.accept()
        print("CONNECTED: "+adr[0]+':'+str(adr[1]))
        start_new_thread(client_thread ,(cs,adr[0]))
class Client():
    def __init__(self, ip, port):
        self.ip=ip
        print("Connecting to "+str(ip)+':'+str(port)+"...")
        self.conn=socket.socket()
        self.conn.connect((ip, port))
        self.conn.sendall(b"PING")
        if self.conn.recv(4).decode()!='OK':
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
    def getDaughterBlock(self, h_ash):
        self.avsend(b'FSB?'+h_ash.to_bytes(length,'little'))
        resp=self.avrec()
        if resp==b'NONE':
            print("Node "+self.ip+" hasn't block "+hex(h_ash))
            return False
        else:
            blk=Block('')
            blk.unpack(resp)
            if blk.validate() and blk.hash==h_ash:
                print("Got daughter block "+hex(h_ash)+" from "+self.ip)
                daughter_blocks.append(blk)
                return True
            else:
                print("Invalid daughter block from "+hex(h_ash))
                return False
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
            try:
                blk.lshash=blocks[len(blocks)-1].hash
            except:
                print("I think we found the genesis block...")
            if blk.validate():
                print("Downloaded block "+hex(blk.hash))
                blocks.append(blk)
            else:
                print("Invalid block.")
                print(blk.hash)
                print(blocks[0].hash)
                return True
        return False
    def getNodes(self):
        self.avsend(b'NODES')
        tmp=self.avrec().decode().split(',')
        for i in tmp:
            if len(nodes)>=node_limit:
                return
            ok=True
            for i in nodes:
                if i.ip==i:
                    ok=False
                    break
            if ok:
                try:
                    nodes.append(Client(i,x))
                except:
                    pass
    def downloadAll(self):
        print("Node "+self.ip+" downloading all blocks...")
        while not self.getOneBlock():
            print("Possibly more blocks...")
        print("Node "+self.ip+" hasn't yet any more blocks.")
        if running_node:
            self.avsend(b'IAMNODE')
            self.conn.recv(2)
def save():
    data=[]
    for i in blocks:
        if i.validate():
            data.append(i.pack())
    for b in daughter_blocks:
        used=False
        for i in blocks:
            if i.find(b.hash.to_bytes(length, 'little'))>-1 or i.find(hex(b.hash).encode())>-1:
                used=True
                break
        if used and b.validate():
            data.append(b.pack())
    if(len(data)==0):
        print("ERROR: cannot save empty blockchain.")
        return
    file=open("data.python_blockchain",'w')
    file.write(str(data))
    file.close()
def load():
    global blocks, daughter_blocks
    file=open("data.python_blockchain",'r')
    data=eval(file.read())
    file.close()
    orphans=[]
    for i in data:
        blk=Block('')
        blk.unpack(i)
        orphans.append(blk)
    del data
    did_things=True
    t_blks=[orphans[0]]
    orphans.remove(orphans[0])
    prev_blk=t_blks[0]
    while did_things:
        did_things=False
        for i in orphans:
            if i.lshash==prev_blk.hash:
                t_blks.append(i)
                orphans.remove(i)
                did_things=True
    for b in orphans:
        used=False
        for i in t_blks:
            if i.data.encode().find(b.hash.to_bytes(length, 'little'))>-1 or i.data.find(hex(b.hash))>-1:
                used=True
                break
        if used and b.validate():
            daughter_blocks.append(b)
    for i in t_blks:
        if not i.validate():
            print("ERROR: saved blockchain is INVALID.")
            return
    if len(blocks)<len(t_blks):
        if len(blocks)>0 and blocks[len(blocks)-1].hash!=t_blks[len(t_blks)-1].hash:
            print("WARNING: Saved blockchain isn't the same as the one loaded.")
        blocks=t_blks
    else:
        print("Blockchain loaded is longer or same size as the saved chain.")
def get_nodes():
    for i in ips:
        if not (running_node and i in ['127.0.0.1', 'localhost']):
            for x in ports:
                try:
                    nodes.append(Client(i,x))
                except:
                    pass
    for i in nodes:
        i.getNodes()
def checker_thread():
    while True:
        print("Downloading...")
        if len(nodes)==0:
            print("Ran out of nodes...")
            get_nodes()
        for i in nodes:
            i.downloadAll()
            i.getNodes()
        save()
        print("Done.")
        time.sleep(600)  # ten minutes
if full_node:
    for port in ports:
        th=threading.Thread(target=server, args=(port,))
        th.start()
try:
    load()
except:
    print("Starting for the first time?")
time.sleep(0.1)
#get_nodes()
# Let's re-download the blocks from time to time.
threading.Thread(target=checker_thread).start()
#while True:
    #pass
