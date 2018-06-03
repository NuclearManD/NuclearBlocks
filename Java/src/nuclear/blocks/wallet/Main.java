package nuclear.blocks.wallet;

import java.io.File;
import java.io.IOException;
import java.util.Base64;

import nuclear.blocks.client.ClientIface;
import nuclear.blocks.wallet.ui.WalletGUI;
import nuclear.slithercrypto.ECDSAKey;
import nuclear.slithercrypto.blockchain.SavedChain;
import nuclear.slitherge.top.io;

public class Main implements Runnable {
	String basepath=System.getProperty("user.home")+"/AppData/Roaming/NuclearBlocks";
	String keypath=basepath+"/keys/main.key";
	String blockchainStorePlace=basepath+"/blockchain/";
	
	ECDSAKey key;
	
	public static String nodeAdr="68.4.23.94";
	
	ClientIface iface;
	SavedChain chain;
	WalletGUI gui;
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
		gui=new WalletGUI(chain,key,iface);
		gui.addressLabel.setText("Address: "+encode(key.getPublicKey()));
		gui.coinCountLabel.setText("Please wait, connecting to network...");
		gui.setVisible(true);
		gui.balance=chain.getCoinBalance(key.getPublicKey());
		new Thread(this).start();
	}
	
	public static String encode(byte[] publicKey) {
		return Base64.getEncoder().encodeToString(publicKey).replaceAll("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgA", "@");
	}
	public static byte[] decode(String text) {
		text=text.replaceAll("@", "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgA");
		return Base64.getDecoder().decode(text);
	}
	public static void main(String[] args) {
		new Main();
	}

	public void run() {
		while(true) {
			gui.coinCountLabel.setText("Syncing with network...");
			gui.btnReconnect.setEnabled(false);
			int q;
			do{
				q=iface.downloadBlockchain(chain);
				if(q==-1){
					gui.btnReconnect.setEnabled(true);
					while(!gui.selReconnect){
						try {
							Thread.sleep(20);
						} catch (InterruptedException e) {
							break;
						}
					}
					gui.selReconnect=false;
					gui.btnReconnect.setEnabled(false);
				}
			}while(q==-1);
			io.println("Downloaded "+q+" new blocks.");
			gui.balance=chain.getCoinBalance(key.getPublicKey());
			gui.updateBalance();
			try {
				Thread.sleep(1000*15);
			} catch (InterruptedException e) {
				break;
			}
		}
	}
	
}
