package nuclear.blocks.wallet;

import java.io.File;
import java.io.IOException;
import java.util.Base64;

import nuclear.blocks.client.ClientIface;
import nuclear.blocks.wallet.ui.WalletGUI;
import nuclear.slithercrypto.ECDSAKey;
import nuclear.slithercrypto.blockchain.SavedChain;
import nuclear.slithercrypto.blockchain.Transaction;
import nuclear.slitherge.top.io;

public class Main implements Runnable {
	String basepath=System.getProperty("user.home")+"/AppData/Roaming/NuclearBlocks";
	String keypath=basepath+"/keys/main.key";
	String blockchainStorePlace=basepath+"/blockchain/";
	
	ECDSAKey key;
	
	String nodeAdr="192.168.1.150";
	
	ClientIface iface;
	SavedChain chain;
	
	public Main() {
		if(new File(keypath).exists())
			key=new ECDSAKey(keypath);
		else{
			new File(keypath).getParentFile().mkdirs();
			key=new ECDSAKey();
			key.save(keypath);
		}
		io.println("Got key...");
		try {
			iface=new ClientIface(nodeAdr);
		} catch (IOException e) {
			e.printStackTrace();
		}
		chain=new SavedChain(blockchainStorePlace);
		io.println("Loading GUI");
		WalletGUI gui=new WalletGUI(chain,key,iface);
		gui.addressLabel.setText("Address: "+Base64.getEncoder().encodeToString(key.getPublicKey()).replaceAll("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgA", "@"));
		gui.coinCountLabel.setText("Please wait, connecting to network...");
		gui.setVisible(true);
		iface.downloadBlockchain(chain);
		gui.balance=chain.getCoinBalance(key.getPublicKey());
		gui.coinCountLabel.setText("Balance: "+gui.balance+" KiB");
		new Thread(this).start();
	}
	
	public static void main(String[] args) {
		new Main();
	}

	public void run() {
		while(true) {
			try {
				Thread.sleep(1000*60*15);
			} catch (InterruptedException e) {
				break;
			}
			io.println("Downloaded "+iface.downloadBlockchain(chain)+" new blocks.");
		}
	}
	
}
