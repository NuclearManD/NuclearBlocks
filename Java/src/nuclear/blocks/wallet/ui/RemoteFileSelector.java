package nuclear.blocks.wallet.ui;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;

import javax.swing.ButtonGroup;
import javax.swing.GrayFilter;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JRadioButton;
import javax.swing.JTextField;
import javax.swing.JTree;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.TreePath;

import nuclear.blocks.wallet.Main;
import nuclear.slithercrypto.blockchain.Block;
import nuclear.slithercrypto.blockchain.BlockchainBase;
import nuclear.slithercrypto.blockchain.Transaction;
import nuclear.slitherge.top.io;

public class RemoteFileSelector implements ActionListener{
	private JTextField txtExtadr;
	private JTextField txtHash;
	private JTextField txtSearchEntry;
	private JButton btnDownload;
	private JTree list;
	
	public Transaction selection=null;
	private boolean terminate=true;
	
	BlockchainBase man;
	
	byte[] adr;
	
	String[] files= {"No Files to Display!"};
	Transaction[] blocks;
	private DefaultMutableTreeNode root;
	private String last_cmd="null";
	
	/**
	 * @wbp.parser.entryPoint
	 */
	public RemoteFileSelector(BlockchainBase b,byte[] adr) {
		this.adr=adr;
		this.man=b;
		terminate=false;
		JFrame frame=new JFrame("Select a File");
		frame.setSize(550, 400);
		frame.getContentPane().setLayout(null);
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		
		
		ButtonGroup buttonGroup = new ButtonGroup();
		
		JRadioButton rdbtna1 = new JRadioButton("My files only");
		buttonGroup.add(rdbtna1);
		rdbtna1.setBounds(6, 7, 109, 23);
		rdbtna1.addActionListener(this);
		rdbtna1.setActionCommand("MYFILES");
		frame.getContentPane().add(rdbtna1);
		
		JRadioButton rdbtnA = new JRadioButton("Files of another address");
		buttonGroup.add(rdbtnA);
		rdbtnA.setBounds(6, 33, 141, 23);
		rdbtnA.addActionListener(this);
		rdbtnA.setActionCommand("EXTFILE");
		frame.getContentPane().add(rdbtnA);
		
		JRadioButton rdbtnA_1 = new JRadioButton("Pick from hash");
		buttonGroup.add(rdbtnA_1);
		rdbtnA_1.setBounds(6, 59, 109, 23);
		rdbtnA_1.addActionListener(this);
		rdbtnA_1.setActionCommand("HASHFILE");
		frame.getContentPane().add(rdbtnA_1);
		//*
		JRadioButton rdbtnA_2 = new JRadioButton("All files");
		buttonGroup.add(rdbtnA_2);
		rdbtnA_2.setBounds(6, 85, 109, 23);
		rdbtnA_2.addActionListener(this);
		rdbtnA_2.setActionCommand("ALLFILES");
		frame.getContentPane().add(rdbtnA_2);
		//*/
		//io.println("Loaded radiobuttons...");
		JButton btnCancel = new JButton("CANCEL");
		btnCancel.setActionCommand("CANCEL");
		btnCancel.addActionListener(this);
		btnCancel.setBounds(6, 329, 89, 23);
		frame.getContentPane().add(btnCancel);
		
		btnDownload = new JButton("DOWNLOAD");
		btnDownload.setActionCommand("DOWNLOAD");
		btnDownload.addActionListener(this);
		btnDownload.setBounds(420, 329, 104, 23);
		btnDownload.setEnabled(false);
		frame.getContentPane().add(btnDownload);
		//io.println("Loaded buttons...");
		txtExtadr = new JTextField();
		txtExtadr.setText("Other Address");
		txtExtadr.setBounds(170, 34, 354, 20);
		frame.getContentPane().add(txtExtadr);
		txtExtadr.setColumns(10);
		txtExtadr.addActionListener(this);
		txtExtadr.setActionCommand("UPD");
		
		txtHash = new JTextField();
		txtHash.setText("File Hash");
		txtHash.setBounds(170, 60, 354, 20);
		frame.getContentPane().add(txtHash);
		txtHash.setColumns(10);
		txtHash.addActionListener(this);
		txtHash.setActionCommand("UPD");
		
		txtSearchEntry = new JTextField();
		txtSearchEntry.setText("Search Entry");
		txtSearchEntry.setBounds(170, 86, 183, 20);
		frame.getContentPane().add(txtSearchEntry);
		txtSearchEntry.setColumns(10);
		txtSearchEntry.addActionListener(this);
		txtSearchEntry.setActionCommand("UPD");
		//io.println("Loaded textboxes...");
		root=new DefaultMutableTreeNode("Unselected");
		list = new JTree(root);
		writeList();
		list.setEnabled(false);
		list.setBounds(6, 115, 518, 203);
		frame.getContentPane().add(list);

		frame.setVisible(true);
		//io.println("Frame VISIBLE.");
		String selectionName=null;
		while((!terminate)&&frame.isDisplayable()) {
			try {
				Thread.sleep(20);// 50 fps
			} catch (InterruptedException e) {
				break;
			}
			TreePath q=list.getSelectionPath();
			String str=null;
			if(q!=null)
				str=q.getLastPathComponent().toString();
			if(str==null) {
				selectionName=null;
				btnDownload.setEnabled(false);
			}else if(!str.equals(selectionName)) {
				for(int i=0;i<files.length;i++)
					if(files[i].equals(str)) {
						selection=blocks[i];
						selectionName=str;
						btnDownload.setEnabled(true);
						break;
					}
			}
		}
		frame.dispose();
		io.println("Done");
	}
	private void writeList() {
		DefaultTreeModel model = (DefaultTreeModel) list.getModel();
		root.removeAllChildren();
		for(String i:files) {
			DefaultMutableTreeNode x= new DefaultMutableTreeNode(i);
			root.add(x);
		}
		model.reload();
	}
	public void actionPerformed(ActionEvent e) {
		String c=e.getActionCommand();
		io.println("command: "+c);
		if(c=="UPD") {
			c=last_cmd;
		}else
			last_cmd=c;
		if(c.equals("MYFILES")) {
			txtExtadr.setEnabled(false);
			txtHash.setEnabled(false);
			txtSearchEntry.setEnabled(false);
			ArrayList<Transaction> files=man.getFilesOf(adr);
			blocks=new Transaction[files.size()];
			files.toArray(this.blocks);
			this.files=new String[blocks.length];
			for(int i=0;i<blocks.length;i++) {
				this.files[i]=new String(blocks[i].getMeta(),StandardCharsets.UTF_8);
			}
			writeList();
			list.setEnabled(true);
			root.setUserObject("My Files");
		}else if(c.equals("EXTFILE")) {
			txtExtadr.setEnabled(true);
			txtHash.setEnabled(false);
			txtSearchEntry.setEnabled(false);
			try {
				byte[] adr=Main.decode(txtExtadr.getText());
				ArrayList<Transaction> files=man.getFilesOf(adr);
				blocks=new Transaction[files.size()];
				files.toArray(this.blocks);
				this.files=new String[blocks.length];
				for(int i=0;i<blocks.length;i++) {
					this.files[i]=new String(blocks[i].getMeta(),StandardCharsets.UTF_8);
				}
				root.setUserObject("Some Files");
				list.setEnabled(true);
			}catch(Exception e123) {
				list.clearSelection();
				files=new String[1];
				files[0]= "Invalid Address";
				list.setEnabled(false);
			}
			writeList();
		}else if(c.equals("HASHFILE")) {
			try {
				root.setUserObject("File From Hash");
				txtExtadr.setEnabled(false);
				txtHash.setEnabled(true);
				txtSearchEntry.setEnabled(false);
				boolean notfound=true;
				Transaction t=null;
				for(int i=0;i<man.length()&&notfound;i++) {
					Block blk=man.getBlockByIndex(i);
					for(int j=0;j<blk.numTransactions();j++) {
						t=blk.getTransaction(j);
						if(Arrays.equals(t.getDaughterHash(),Main.decode(txtHash.getText())))
							notfound=false;
					}
				}
				files=new String[1];
				if(notfound) {
					list.setEnabled(false);
					files[0]="Not a File";
				}else {
					list.setEnabled(true);
					files[0]=new String(t.getMeta(),StandardCharsets.UTF_8);
				}
			}catch(Exception e123) {
				list.clearSelection();
				files=new String[1];
				files[0]= "Invalid Hash";
				list.setEnabled(false);
			}
			writeList();
		}else if(c.equals("ALLFILES")) {
			root.setUserObject("All Files");
			try {
				txtExtadr.setEnabled(false);
				txtHash.setEnabled(false);
				txtSearchEntry.setEnabled(true);
				files=new String[0];
				blocks=new Transaction[0];
				for(int i=0;i<man.length();i++) {
					Block blk=man.getBlockByIndex(i);
					for(int j=0;j<blk.numTransactions();j++) {
						Transaction t=blk.getTransaction(j);
						if(new String(t.getMeta(),StandardCharsets.UTF_8).contains(txtSearchEntry.getText())&&t.type==Transaction.TRANSACTION_STORE_FILE){
							files=append(files,new String(t.getMeta(),StandardCharsets.UTF_8));
							blocks=append(blocks,t);
							io.println("Found file: "+new String(t.getMeta(),StandardCharsets.UTF_8));
						}
					}
				}
				list.setEnabled(true);
			}catch(Exception e123) {
				list.clearSelection();
				files=new String[1];
				files[0]= "Error!";
				list.setEnabled(false);
				e123.printStackTrace();
			}
			writeList();
		}else if(c.equals("CANCEL")) {
			terminate=true;
			selection=null;
		}else if(c.equals("DOWNLOAD")) {
			terminate=true;
		}
		if(files.length==0) {
			list.setEnabled(false);
			files=new String[1];
			files[0]="No Results";
			writeList();
		}
	}/*
	public static void main(String[]args) {
		io.println("Loading test...");
		ECDSAKey key=new ECDSAKey();
		BlockChainManager man=new BlockChainManager();
		man.addPair(Transaction.makeFile(key.getPublicKey(), key.getPrivateKey(), "lol NIKQ".getBytes(StandardCharsets.UTF_8), new byte[32], "DATA?!?"));
		man.commit(key.getPublicKey());
		RemoteFileSelector selector=new RemoteFileSelector(man,key.getPublicKey());
		if(selector.selection==null)
			io.println("CAnCel!");
		else {
			io.println(new String(selector.selection.getMeta(),StandardCharsets.UTF_8));
			io.println(Main.encode(selector.selection.getDaughterHash()));
		}
	}*/
	private String[] append(String[] ar, String obj) {
		ar=Arrays.copyOf(ar, ar.length+1);
		ar[ar.length-1]=obj;
		return ar;
	}
	private Transaction[] append(Transaction[] ar, Transaction obj) {
		ar=Arrays.copyOf(ar, ar.length+1);
		ar[ar.length-1]=obj;
		return ar;
	}
}
