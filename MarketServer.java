import java.io.*;
import java.net.*;

public class MarketServer {
    public static void main(String[] args) throws IOException {
        String ip = "";
        int port = 0;
        DatagramSocket serverSocket = new DatagramSocket();
        InetAddress group = InetAddress.getByName(ip);
        
        while (true) {
            byte[] receiveData = new byte[1024];
            DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
            serverSocket.receive(receivePacket);
            
            String message = new String(receivePacket.getData(), 0, receivePacket.getLength());
            System.out.println("Received message: " + message);
            if(message.equals("kill")) break;
            
            byte[] sendData = message.getBytes();
            DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, group, port);
            serverSocket.send(sendPacket);
        }
        serverSocket.close();
    }
}
