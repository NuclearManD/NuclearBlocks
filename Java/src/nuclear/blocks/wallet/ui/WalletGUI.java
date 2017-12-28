package nuclear.blocks.wallet.ui;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.JScrollPane;
import javax.swing.JToolBar;

import nuclear.blocks.client.ClientIface;
import nuclear.slithercrypto.ECDSAKey;
import nuclear.slithercrypto.blockchain.BlockchainBase;
import nuclear.slithercrypto.blockchain.Transaction;

import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JList;
import javax.swing.JTextPane;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.awt.event.ActionEvent;

@SuppressWarnings("serial")
public class WalletGUI extends JFrame implements ActionListener{
	public JToolBar toolBar;
	public JLabel coinCountLabel;
	public JLabel addressLabel;
	
	final JFileChooser fc = new JFileChooser();
	BlockchainBase man;
	
	ECDSAKey key;
	private ClientIface iface;
	public WalletGUI(BlockchainBase man, ECDSAKey key,ClientIface iface) {
		this.man=man;
		this.key=key;
		this.iface=iface;
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(20,20,800,600);
		getContentPane().setLayout(null);
		
		JPanel panel = new JPanel();
		panel.setBounds(0, 27, 784, 69);
		getContentPane().add(panel);
		panel.setLayout(null);
		
		addressLabel = new JLabel("error");
		addressLabel.setBounds(10, 11, 764, 21);
		panel.add(addressLabel);
		
		coinCountLabel = new JLabel("you have money!");
		coinCountLabel.setBounds(10, 37, 764, 21);
		panel.add(coinCountLabel);
		
		toolBar = new JToolBar();
		toolBar.setBounds(0, 0, 784, 23);
		getContentPane().add(toolBar);
		
		JButton btnUpload = new JButton("Upload");
		btnUpload.addActionListener(this);
		btnUpload.setActionCommand("UPLOAD");
		toolBar.add(btnUpload);
		
		JButton btnDownload = new JButton("Download");
		btnDownload.setActionCommand("DOWNLOAD");
		btnDownload.addActionListener(this);
		toolBar.add(btnDownload);
		setVisible(true);
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		if(e.getActionCommand()=="UPLOAD") {
			JFileChooser jfc = new JFileChooser(System.getProperty("user.home"));
			int retval=jfc.showOpenDialog(this);
			if(retval==JFileChooser.APPROVE_OPTION) {
				File file=jfc.getSelectedFile();
				String path=file.getPath();
				long length=file.length();
				try {
					FileInputStream stream=new FileInputStream(path);
					byte[] buffer=new byte[(int) length];
					for(int i=0;i<length;i++) {
						buffer[i]=(byte) stream.read();
					}
					iface.uploadPair(Transaction.makeFile(key.getPublicKey(), key.getPrivateKey(), buffer, man.getBlockByIndex(man.length()-1).getHash(), file.getName()));
					stream.close();
				} catch (Exception e1) {
					e1.printStackTrace();
				}
			}
		}else if(e.getActionCommand()=="DOWNLOAD") {
			
		}
	}
}
