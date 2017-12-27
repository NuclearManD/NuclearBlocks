package nuclear.blocks.wallet;

import java.io.File;
import java.util.Base64;

import nuclear.blocks.wallet.ui.WalletGUI;
import nuclear.slithercrypto.ECDSAKey;

public class Main {
	String keypath=System.getProperty("user.home")+"/AppData/Roaming/NuclearBlocks/keys/main.key";
	
	ECDSAKey key;
	public Main() {
		if(new File(keypath).exists())
			key=new ECDSAKey(keypath);
		else{
			new File(keypath).getParentFile().mkdirs();
			key=new ECDSAKey();
			key.save(keypath);
		}
		WalletGUI gui=new WalletGUI();
		gui.addressLabel.setText(Base64.getEncoder().encodeToString(key.getPublicKey()));
		gui.coinCountLabel.setText("Please wait, connecting to network...");
		
	}
	
	public static void main(String[] args) {
		new Main();
	}
	
}
