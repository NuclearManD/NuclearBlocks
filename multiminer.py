import threading, os
def mine():
    os.system("miner.py")
for i in range(5):
    threading.Thread(target=mine).start()
