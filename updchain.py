import chaintool, sys
args=sys.argv
if len(args)<2:
    print("USAGE: python3 updchain.py <filename>")
else:
    chaintool.setup(0x115200)
    try:
        f=open(args[1])
        data=f.read()
        f.close()
        fname=args[1][:16]
        fname=" "*(16-len(fname))+fname
        chaintool.nodes[0].save(chaintool.myPublicKey.to_bytes(8,'little')+fname+len(data).to_bytes(8,'little')+data.encode())
    except:
        print("ERROR.")
