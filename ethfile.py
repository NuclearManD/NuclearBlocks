import chaintool, sys
helpstr=""" --- USAGE ---
python ethfile.py [args]
ARGUMENTS:
    -u [file]    : upload file to blockchain
    -d [file]    : download file from blockchain
    -p           : use a password that is not your private key.
                 * Password will be asked at runtime.
    -e           : "I know how to use this progrm. Don't tell
                 *  me what to do and how to do it" -You
"""
def dwnld(fn, ps):
    chaintool.getDaughter(fn)
    # TODO: run encryption
def upload(fn, ps):
    try:
        f=open(fn,'rb')
        data=f.read()
        f.close()
    except:
        print("File IO error.")
        return
    chaintool.upload(data,)
if not ('-u' in sys.argv or '-d' in sys.argv):
    print(helpstr)
else:
    chaintool.start()
    ex=True
    pswrd=chaintool.myPrivateKey
    fn=''
    if '-e' in sys.argv:
        ex=False
    if '-p' in sys.argv:
        if ex:
            print("The password ask box shows no letters,\nlike a linux root password prompt.")
        pswrd=getpass.getpass()
    if '-u' in sys.argv:
        fn=sys.argv[sys.argv.index('-u')+1]
        upload(fn, pswrd)
    if '-d' in sys.argv:
        fn=sys.argv[sys.argv.index('-d')+1]
        dwnld(fn, pswrd)
