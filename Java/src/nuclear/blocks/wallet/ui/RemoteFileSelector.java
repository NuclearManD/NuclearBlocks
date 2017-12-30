package nuclear.blocks.wallet.ui;

import javax.swing.JFrame;

import nuclear.slithercrypto.blockchain.Block;
import nuclear.slithercrypto.blockchain.BlockchainBase;
import nuclear.slithercrypto.blockchain.Transaction;
import javax.swing.JRadioButton;
import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JTextField;

@SuppressWarnings("serial")
public class RemoteFileSelector{
	private static JTextField txtExtadr;
	private static JTextField txtHash;
	private static JTextField txtSearchEntry;
	/**
	 * @wbp.parser.entryPoint
	 */
	public static Block getFile(BlockchainBase b,byte[] adr) {
		JFrame frame=new JFrame("Select a File");
		frame.getContentPane().setLayout(null);
		ButtonGroup buttonGroup = new ButtonGroup();
		
		JRadioButton rdbtna1 = new JRadioButton("My files only");
		buttonGroup.add(rdbtna1);
		rdbtna1.setBounds(6, 7, 109, 23);
		frame.getContentPane().add(rdbtna1);
		
		JRadioButton rdbtnA = new JRadioButton("Files of another address");
		buttonGroup.add(rdbtnA);
		rdbtnA.setBounds(6, 33, 141, 23);
		frame.getContentPane().add(rdbtnA);
		
		JRadioButton rdbtnA_1 = new JRadioButton("Pick from hash");
		buttonGroup.add(rdbtnA_1);
		rdbtnA_1.setBounds(6, 59, 109, 23);
		frame.getContentPane().add(rdbtnA_1);
		
		JRadioButton rdbtnA_2 = new JRadioButton("All files");
		buttonGroup.add(rdbtnA_2);
		rdbtnA_2.setBounds(6, 85, 109, 23);
		frame.getContentPane().add(rdbtnA_2);
		
		JButton btnCancel = new JButton("CANCEL");
		btnCancel.setBounds(6, 329, 89, 23);
		frame.getContentPane().add(btnCancel);
		
		JButton btnDownload = new JButton("DOWNLOAD");
		btnDownload.setBounds(420, 329, 104, 23);
		frame.getContentPane().add(btnDownload);
		
		txtExtadr = new JTextField();
		txtExtadr.setText("Other Address");
		txtExtadr.setBounds(170, 34, 354, 20);
		frame.getContentPane().add(txtExtadr);
		txtExtadr.setColumns(10);
		
		txtHash = new JTextField();
		txtHash.setText("File Hash");
		txtHash.setBounds(170, 60, 354, 20);
		frame.getContentPane().add(txtHash);
		txtHash.setColumns(10);
		
		txtSearchEntry = new JTextField();
		txtSearchEntry.setText("Search Entry");
		txtSearchEntry.setBounds(170, 86, 183, 20);
		frame.getContentPane().add(txtSearchEntry);
		txtSearchEntry.setColumns(10);
		return null;
	}
}
