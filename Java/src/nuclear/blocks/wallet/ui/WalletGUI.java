package nuclear.blocks.wallet.ui;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;

import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.JTextPane;
import javax.swing.JToolBar;

import nuclear.blocks.client.ClientIface;
import nuclear.blocks.wallet.Main;
import nuclear.slithercrypto.ECDSAKey;
import nuclear.slithercrypto.blockchain.BlockchainBase;
import nuclear.slithercrypto.blockchain.Transaction;
import nuclear.slitherge.top.io;

@SuppressWarnings("serial")
public class WalletGUI extends JFrame implements ActionListener{
    protected int mining;
	public JToolBar toolBar;
	public JLabel coinCountLabel;
	public JTextPane addressLabel;
	public JTextArea txtrAddress;
	public JTextArea kibAmt;
	protected JLabel miningData;
	protected JLabel tmp;
	protected JButton btnUpload,btnDownload,btnSend;
	
	protected final JFileChooser fc = new JFileChooser();
	protected BlockchainBase man;
	
	protected ECDSAKey key;
	protected ClientIface iface;
	
	
	public double balance=0.0;
	
	protected String path;
	protected byte[] buffer;
	protected File file;
	protected byte[] lasthash;
	
	public WalletGUI(BlockchainBase man1, ECDSAKey key1,ClientIface iface1) {
		this.man=man1;
		this.key=key1;
		this.iface=iface1;
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(20,20,800,600);
		getContentPane().setLayout(null);
		
		JPanel panel = new JPanel();
		panel.setBounds(0, 27, 784, 69);
		getContentPane().add(panel);
		panel.setLayout(null);
		
		addressLabel = new JTextPane();
		addressLabel.setEditable(false);
		addressLabel.setText("Error : no address?!?!?!");
		addressLabel.setBackground(null);
		addressLabel.setBounds(10, 11, 764, 21);
		panel.add(addressLabel);
		
		coinCountLabel = new JLabel("you have money!");
		coinCountLabel.setBounds(10, 37, 432, 21);
		panel.add(coinCountLabel);
		
		miningData=new JLabel("Not currently mining (safe to exit)");
		miningData.setBounds(474, 38, 300, 20);
		panel.add(miningData);
		
		toolBar = new JToolBar();
		toolBar.setBounds(0, 0, 784, 23);
		getContentPane().add(toolBar);
		
		btnUpload = new JButton("Upload");
		btnUpload.addActionListener(this);
		btnUpload.setActionCommand("UPLOAD");
		toolBar.add(btnUpload);
		
		btnDownload = new JButton("Download");
		btnDownload.setActionCommand("DOWNLOAD");
		btnDownload.addActionListener(this);
		toolBar.add(btnDownload);

		
		tmp = new JLabel("SEND COINS");
		tmp.setBounds(10, 107, 109, 22);
		getContentPane().add(tmp);
		
		txtrAddress = new JTextArea();
		txtrAddress.setText("Address Here");
		txtrAddress.setBounds(10, 135, 764, 22);
		getContentPane().add(txtrAddress);
		
		kibAmt = new JTextArea();
		kibAmt.setText("KiB Amount");
		kibAmt.setBounds(10, 168, 109, 22);
		getContentPane().add(kibAmt);
		
		btnSend = new JButton("SEND");
		
		miningUpd();
		
		btnSend.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				byte[] adr=Main.decode(txtrAddress.getText());
				if(!man.isActive(adr))
					if(JOptionPane.showConfirmDialog(null, "This address doesn't look like a valid address. It may be valid, but you might want to check it.\nIt is possible that your KiB will be lost forever if you send and the address is wrong. Are you sure you want to send?")!=JOptionPane.YES_OPTION)
						return;
				double toSend=Double.parseDouble(kibAmt.getText());
				if(toSend+1.09>balance) {
					JOptionPane.showMessageDialog(null, "Error: Transaction will fail.\n You do not have enough KiB to send.");
					return;
				}
				if(JOptionPane.showConfirmDialog(null, "Confirm you want to send "+toSend+" KiB")!=JOptionPane.YES_OPTION)
					return;
				iface.uploadTransaction(Transaction.sendCoins(key.getPublicKey(), adr, key.getPrivateKey(), toSend));
				balance-=toSend+1.09;
				updateBalance();
			}
		});
		
		
		btnSend.setBounds(10, 201, 89, 23);
		getContentPane().add(btnSend);
	}

	public void actionPerformed(ActionEvent e) {
		if(e.getActionCommand()=="UPLOAD") {
			if(1.09>balance) {
				if(JOptionPane.showConfirmDialog(null, "Error: Transaction will fail.\n You do not have enough KiB to send that, try anyway?")!=JOptionPane.YES_OPTION)
						return;
				
			}
			JFileChooser jfc = new JFileChooser(System.getProperty("user.home"));
			int retval=jfc.showOpenDialog(this);
			if(retval==JFileChooser.APPROVE_OPTION) {
				file=jfc.getSelectedFile();
				path=file.getPath();
				long length=file.length();
				try {
					FileInputStream stream=new FileInputStream(path);
					buffer=new byte[(int) length];
					for(int i=0;i<length;i++) {
						buffer[i]=(byte) stream.read();
					}
					stream.close();
					lasthash=new byte[32];
					if(man.length()>0)
						lasthash=man.getBlockByIndex(man.length()-1).getHash();
					new Thread(new Runnable() {

						public void run() {
					    	 mining++;
					    	 miningUpd();
					    	 iface.uploadPair(Transaction.makeFile(key.getPublicKey(), key.getPrivateKey(), buffer, lasthash, file.getName()));
					    	 balance-=1.09;
							 updateBalance();
							 mining--;
					    	 miningUpd();
					     }
					}).start();
				} catch (Exception e1) {
					e1.printStackTrace();
				}
			}
		}else if(e.getActionCommand()=="DOWNLOAD") {
			new Thread(new Runnable() {
			    public void run() {
			    	RemoteFileSelector selector=new RemoteFileSelector(man,key.getPublicKey());
					if(selector.selection==null)
						return;
					byte[] sel=selector.selection.getDaughterHash();
					io.println(selector.selection.toString());
					int us = fc.showSaveDialog(null);
					if(us==JFileChooser.APPROVE_OPTION) {
						File file=fc.getSelectedFile();
						io.println("Saving...");
						try(FileOutputStream f=new FileOutputStream(file)){
							byte[] data=iface.downloadDaughter(sel).getData();
							f.write(data);
						}catch (Exception e1) {
							e1.printStackTrace();
							JOptionPane.showMessageDialog(null, "Error: Download failed!");
						}
					}
			    }
			}).start();
		}
	}

	public void miningUpd() {
		if(mining==0)
			miningData.setText("Not currently mining (safe to exit)");
		else
			miningData.setText(mining+" operations running. (do not exit)");
		miningData.paintImmediately(miningData.getVisibleRect());
	}

	public void updateBalance() {
		coinCountLabel.setText("Balance: "+balance+" KiB");
	}
}
