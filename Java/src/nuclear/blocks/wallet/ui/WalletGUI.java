package nuclear.blocks.wallet.ui;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.JScrollPane;
import javax.swing.JToolBar;
import javax.swing.JButton;
import javax.swing.JList;
import javax.swing.JTextPane;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

@SuppressWarnings("serial")
public class WalletGUI extends JFrame {
	public JToolBar toolBar;
	public JLabel coinCountLabel;
	public JLabel addressLabel;

	public WalletGUI() {
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(20,20,600,400);
		getContentPane().setLayout(null);
		
		JPanel panel = new JPanel();
		panel.setBounds(0, 27, 584, 69);
		getContentPane().add(panel);
		panel.setLayout(null);
		
		addressLabel = new JLabel("error");
		addressLabel.setBounds(10, 11, 414, 21);
		panel.add(addressLabel);
		
		coinCountLabel = new JLabel("you have money!");
		coinCountLabel.setBounds(10, 37, 414, 14);
		panel.add(coinCountLabel);
		
		toolBar = new JToolBar();
		toolBar.setBounds(0, 0, 584, 23);
		getContentPane().add(toolBar);
		
		JButton btnFile = new JButton("File");
		btnFile.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
			}
		});
		toolBar.add(btnFile);
		
		JButton btnHelp = new JButton("Help");
		btnHelp.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
			}
		});
		toolBar.add(btnHelp);
		setVisible(true);
	}
}
