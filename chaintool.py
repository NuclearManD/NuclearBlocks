import time, os, hashlib, threading, socket
from ecdsa import SigningKey, VerifyingKey, NIST384p
ips=['127.0.0.1','192.168.1.132', '68.4.20.23']
ports=[19200]#, 19201] # a common baud rate XD
node_limit=20
hashrate=0
can_mine=False
save_main=False# save main blockchain?
save_sub=False # save daughter blocks?
full_node=False # run a full node?
if __name__=="__main__" and input("Run Node? [Y/n]")=='Y':
    full_node=True
millis = lambda: int(round(time.time() * 1000))
FirstBlock=None
TopBlock=None
bits=256
maxBlockSize=4096
allblocks=[]
def HASH(data, bits=bits):
    j=hashlib.sha256(data)
    out=int(j.hexdigest(),16)
    out&=(2**bits)-1
    return out
length=int(bits/8)
current_data=""
current_age=millis()
blocks=[]
daughter_blocks=[]
nodes=[]
def info(x):
    print("[INFO]  "+x)
def warn(x):
    print("[WARN]  "+x)
def error(x):
    print("[ERROR] "+x)
class Block:
    def __init__(self, data, miner=b'', lsblock=None, difficulty=None):
        global allblocks
        self.data=data
        self.lsblock=lsblock
        self.miner=myPublicKey
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
        self.header+=self.miner
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
        self.miner=data[:75]
        data=data[75:]
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
class BlockFS:
    def __init__(self, items=[]):
        self.items=items
    def pack():
        pass
def mine(block):
    i=0
    info("Mining a new block...")
    timer=millis()+1000
    cnt=millis()
    off=0
    while not block.mineOnce():
        if(millis()>timer):
            timer=millis()+1000
            info(str(int((i-off)/(millis()-cnt)))+" kH/s")
            cnt=millis()
            off=i
        i+=1
    info("Took "+str(i)+" attempts to mine block with hash "+hex(block.hash))
def createBlock(newdata):
    global TopBlock
    if len(newdata)>maxBlockSize:
        error("Block too big!")
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
def addData(data):
    global current_age, current_data
    if len(current_data+data)<(maxBlockSize-(3*length+28)):
        current_data+=(hex(len(data))[2:]).zfill(4)+data
    elif len(data)<(maxBlockSize-(3*length+28)):
        mine_remote(Block(current_data))
        current_data=(hex(len(data))[2:]).zfill(4)+data
        current_age=millis()
    else:
        error("Cannot submit that much data.")#mine_remote_daughter(newdata, cmt+":"+str(myPublicKey.to_bytes(16, 'little'))+hex(daughter.hash)+';')
    if len(current_data)+(3*length+24)>4090 or (current_age+120000<millis() and len(current_data)>1024):
        mine_remote(Block(current_data))
        current_data=""
        current_age=millis()
ls_sub_blk=None
def client_thread(cs, ip):
    global solved, ls_sub_blk
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
            info("["+ip+"] Pinged.")
            reply=b'OK'
        elif data[:2]==b'I=':
            data=data[2:]
            index=int.from_bytes(data[:8],"little")
            reply=b'DONE'
            info("["+ip+"] I set to "+str(index))
        elif data==b"GBLK":
            info("["+ip+"] Block requested.")
            if len(blocks)>index:
                chunk=blocks[index].pack()
            else:
                chunk=b"NONE"
            reply=chunk
            reply=len(reply).to_bytes(8, 'little')+reply
        elif data[:4]==b'FSB?':
            hsh=int.from_bytes(data[4:],'little')
            info("["+ip+"] Getting daughter block with hash "+hex(hsh))
            for i in daughter_blocks:
                if i.hash==hsh:
                    reply=i.pack()
                    break
            if reply==b'DONE':
                reply=b'NONE'
            reply=len(reply).to_bytes(8, 'little')+reply
        elif data[:5]==b'NODES':
            info("["+ip+"] Requested node list...")
            li=''
            for i in nodes:
                li+=i.ip+','
            reply=li[:-1].encode()
            reply=len(reply).to_bytes(8, 'little')+reply
        elif data[:6]==b'APPEND':
            threading.Thread(target=addData, args=(data[6:]))
        elif data[:6]==b'STORE':
            data=data[6:]
            pos=int.from_bytes(data[:8],"little")+8
            threading.Thread(target=mine_remote_daughter, args=(data[8:pos],data[pos:]))
        elif data[:5]==b'IAMNODE':
            info("["+ip+"] "+ip+" is a node...")
            done=False
            for i in nodes:
                if i.ip==ip:
                    done=True
            if (not done) and len(nodes)<=node_limit:
                for i in ports:
                    nodes.append(Client(ip,i))
            reply=b'OK'
        elif data[:3]==b'SUB':
            try:
                info("["+ip+"] Submitting a new block to the chain...")
                b=Block('')
                b.unpack(data[3:])
                if b.validate() and blocks[len(blocks)-1].hash==b.lshash:
                    blocks.append(b)
                    solved=True
                    ls_sub_blk=b
                    save()
                elif b.validate() and blocks[0].hash==b.lshash:
                    daughter_blocks.append(b)
                    solved=True
                    ls_sub_blk=b
                    save()
                else:
                    warn("  That was an invalid block.")
                    warn("  > Hash was "+hex(b.hash))
            except:
                error("  Error unpacking block from client.")
        #print("response start: "+reply.decode())
        cs.sendall(reply)
    info("Client "+ip+" has disconnected.")
    cs.close()
def start_new_thread(a, b):
    what=threading.Thread(target=a, args=b)
    what.start()
running_node=False
cs_list=[]
def server(port):
    global running_node, cs_list
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    try:
        s.bind(('', port))
        info("Node on port "+str(port)+" started.")
        running_node=True
    except:
        error("Cannot run 2 nodes on same machine.")
        return
    # become a server socket
    s.listen(5)
    while True:
        (cs, adr) = s.accept()
        info("CONNECTED: "+adr[0]+':'+str(adr[1]))
        start_new_thread(client_thread ,(cs,adr[0]))
        cs_list.append(cs)
class Client():
    def __init__(self, ip, port):
        self.ip=ip
        info("Connecting to "+str(ip)+':'+str(port)+"...")
        self.conn=socket.socket()
        self.conn.set_timeout(6)
        self.conn.connect((ip, port))
        self.conn.sendall(b"PING")
        if self.conn.recv(4).decode()!='OK':
            error(str(ip)+" is not a node.")
            self.conn.close()
            self.inUse=True
        else:
            info("  Node discovered: "+ip+':'+str(port))
            self.inUse=False
            if running_node:
                self.inUse=True # stop polling processes
                self.avsend(b'IAMNODE')
                self.conn.recv(2)
                self.inUse=False # resume polling processes
                threading.Thread(target=node_mining_thread,args=(self,))
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
        self.inUse=True # stop polling processes
        self.avsend(b'FSB?'+h_ash.to_bytes(length,'little'))
        resp=self.avrec()
        self.inUse=False # resume polling processes
        if resp==b'NONE':
            info("Node "+self.ip+" hasn't block "+hex(h_ash))
            return False
        else:
            blk=Block('')
            blk.unpack(resp)
            if blk.validate() and blk.hash==h_ash:
                info("Got daughter block "+hex(h_ash)+" from "+self.ip)
                daughter_blocks.append(blk)
                return True
            else:
                error("Invalid daughter block from "+hex(h_ash))
                return False
    def getOneBlock(self):
        self.inUse=True # stop polling processes
        self.avsend(b'I='+len(blocks).to_bytes(length,'little'))
        if self.conn.recv(4)!=b'DONE':
            error("Node "+self.ip+" is no longer valid.")
            return True
        self.avsend(b'GBLK')
        tmp=self.avrec()
        self.inUse=False # resume polling processes
        if tmp==b'NONE':
            return True
        else:
            blk=Block('')
            blk.unpack(tmp)
            try:
                blk.lshash=blocks[len(blocks)-1].hash
            except:
                info("I think we found the genesis block...")
            if blk.validate():
                info("Downloaded block "+hex(blk.hash))
                blocks.append(blk)
            else:
                error("Invalid block sent from node "+self.ip+".")
                return True
        return False
    def getNodes(self):
        self.inUse=True # stop polling processes
        self.avsend(b'NODES')
        tmp=self.avrec().decode().split(',')
        self.inUse=False # resume polling processes
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
        if running_node:
            self.inUse=True # stop polling processes
            self.avsend(b'IAMNODE')
            self.conn.recv(2)
            self.inUse=False # resume polling processes
    def downloadAll(self):
        info("Node "+self.ip+" downloading all blocks...")
        while not self.getOneBlock():
            pass
        info("Node "+self.ip+" hasn't yet any more blocks.")
    def submit(self,block):
        self.avsend(b'SUB'+block.pack())
    def upload(self, data, head):
        self.avsend(b"STORE"+len(data).to_bytes(8, 'little')+data+head)
    def wait_for_mine(self):
        while True:
            if self.inUse:
                continue
            if select.select(cs_list, [], [], 0.1)[0] and self.conn.recv(4)==b'MINE':
                info("Mining request received.")
                tmp=Block('')
                tmp.unpack(self.avrec())
                return tmp
    def save(self, data):
        self.avsend(b'APPEND'+data)
def save():
    data=[]
    for i in blocks:
        if i.validate():
            data.append(i.pack())
    for b in daughter_blocks:
        used=False
        for i in blocks:
            if i.data.encode().find(b.hash.to_bytes(length, 'little'))>-1 or i.data.find(hex(b.hash))>-1:
                used=True
                break
        if used and b.validate():
            data.append(b.pack())
    if(len(data)==0):
        error("cannot save empty blockchain.")
        return
    file=open("data.python_blockchain",'w')
    file.write(str(data))
    file.close()
def load():
    global blocks, daughter_blocks
    file=open("data.python_blockchain",'r')
    try:
        data=eval(file.read())
    except:
        error("the file storing the blockchain is corrupted.  Cannot load corrupted file.")
        return
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
    orphans_removed=0
    for b in orphans:
        if b.validate():
            daughter_blocks.append(b)
            orphans_removed+=1
        else:
            error("Found an invalid block saved!")
    if orphans_removed<len(orphans):
        warn("Orphaned blocks were left over!")
    for i in t_blks:
        if not i.validate():
            error("saved blockchain is INVALID.")
            return
    if len(blocks)<len(t_blks):
        if len(blocks)>0 and blocks[len(blocks)-1].hash!=t_blks[len(t_blks)-1].hash:
            warn("Saved blockchain isn't the same as the one loaded.")
        blocks=t_blks
    else:
        warn("Blockchain loaded is longer or same size as the saved chain.")
def get_nodes():
    for i in ips:
        if not (running_node and i in ['127.0.0.1', 'localhost']):
            for x in ports:
                try:
                    nodes.append(Client(i,x))
                except:
                    pass
                if len(nodes)>=node_limit:
                    return
    for i in nodes:
        i.getNodes()
        if len(nodes)>=node_limit:
            return
def checker_thread():
    while True:
        info("Downloading...")
        old_len=len(nodes)
        if len(nodes)==0:
            warn("Ran out of nodes...")
            get_nodes()
        for i in nodes:
            i.downloadAll()
            i.getNodes()
        save()
        if full_node:
            for i in range(old_len, len(nodes)):
                threading.Thread(target=node_mining_thread, args=(i,)).start()
        info("Done downloading new blocks.")
        time.sleep(120)  # two minutes
solved=True
times=[]
difficulties=[]
def mine_remote(block):
    global solved, times, difficulties
    try:
        while not solved:  # wait for mining job to complete
            pass
        solved=False
        rml=[]
        for i in cs_list:
            try:
                info("Giving mining job to "+str(i.getpeername()))
                reply=block.pack()
                reply=b'MINE'+len(reply).to_bytes(8, 'little')+reply
                i.sendall(reply)
            except:
                rml.append(i)
        for i in rml:
            cs_list.remove(i) # different loop to prevent iteration issues
        t=millis()
        while not solved:
            pass
        times.append(millis()-t)
        difficulties.append(block.difficulty)
    except:
        solved=True # on error fix solved so that next usage of the function will work
def mine_remote_daughter(data, refhead):
    mine_remote(Block(data,lsblock=blocks[0]))
    mine_remote(Block(refhead+hex(ls_sub_blk.hash)))
def node_mining_thread(i):
    while True:
        blk=i.wait_for_mine()
        do_mine=True
        for j in blocks[-5:]:
            if j.data==blk.data:
                if True:#j.validate():
                    i.submit(j)
                    do_mine=False
                    break
                #else:
                #    print("ERROR: block with data containing "+str(blk.data[:10])+"is in the blockchain but is invalid!")
        if do_mine:
            mine_remote(blk)
def start(pri_key):
    global myPrivateKey,myPublicKey
    myPrivateKey=pri_key
    myPublicKey=SigningKey.from_der(myPrivateKey).get_verifying_key().to_der()
    info("Public Key: "+hex(int.from_bytes(myPublicKey,'little')))
    #myPublicKey=int.from_bytes(myPublicKey,'little')
    if full_node:
        for port in ports:
            th=threading.Thread(target=server, args=(port,))
            th.start()
    try:
        load()
    except:
        warn("Starting for the first time?")
    time.sleep(0.1)
    # Let's re-download the blocks from time to time.
    threading.Thread(target=checker_thread).start()
    #while True:
        #pass
def get_key():
    
    tmp=b''
    try:
        j=open("pk.int",'rb')
        tmp=j.read()
        j.close()
    except:
        print("No private key file!")
        if input("Type 'Y' to generate a new key")=='Y':
            tmp=SigningKey.generate().to_der()
        else:
            raise Exception("No key generated")
        j=open("pk.int",'wb')
        j.write(tmp)
        j.close()
        print("Saved.")
    return tmp
if __name__=="__main__":
    start(get_key())
