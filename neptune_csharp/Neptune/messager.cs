using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;
//using System.Collections;
using UnityEngine;
//using System.Collections.Generic;


public class Messager
{
    public Socket workSocket = null;
    public const int bufferSize = 4096;
    public byte[] buffer = new byte[bufferSize];
    public StringBuilder sb = new StringBuilder();

    public Messager()
    {
    }

    public void ConnectTo(string address, int port)
    {
        IPHostEntry ipHostInfo = Dns.GetHostEntry(address);
        IPAddress ipAddress = ipHostInfo.AddressList[0];
        IPEndPoint remoteEP = new IPEndPoint(ipAddress, port);

        Socket client = new Socket(ipAddress.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
        client.BeginConnect(remoteEP, new AsyncCallback(ConnectedCallback), client);
    }

    public void ConnectedCallback(IAsyncResult ar)
    {
        try
        {
            workSocket = (Socket)ar.AsyncState;
            workSocket.EndConnect(ar);
            Debug.Log("connected");
            workSocket.Send(Encoding.ASCII.GetBytes("GET / \r\n\r\n"));
            workSocket.BeginReceive(buffer, 0, bufferSize, 0, new AsyncCallback(OnReceived), null);
        } catch (Exception e) {
            Debug.LogError(e.ToString());
        }
    }

    public void OnReceived(IAsyncResult ar)
    {
        try
        {
            int bytes = workSocket.EndReceive(ar);
            Debug.Log(Encoding.ASCII.GetString(buffer, 0, bytes));
            if (bytes > 0)
            {
                workSocket.BeginReceive(buffer, 0, bufferSize, 0, new AsyncCallback(OnReceived), null);
            } else {
                Debug.Log("done");
            }
        } catch (Exception e) {
            Debug.LogError(e.ToString());
        }
    }
}
