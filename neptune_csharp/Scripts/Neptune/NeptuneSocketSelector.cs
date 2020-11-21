using UnityEngine;
using System.Collections;
using System;
using System.Net.Sockets;
using System.IO;
using System.Net;
using System.Text;
using System.Collections.Generic;

// Dont not use Socket.Select, seems that it cannot handle connection failed on
// macOS, could be an bug I am not sure since it is barely used(according to google search results)

namespace Neptune
{
    public enum NeptuneSocketStatus: uint
    {
        Inited,
        Connected,
        Closed,
    }

    public struct NeptuneSocketInfo
    {
        public NeptuneSocketStatus status;
        public byte[] readBuffer;
        public byte[] writeBuffer;
    }

    class NeptuneSocketExcpetion : Exception
    {

    }

    class NeptuneSocketNotConnectedExcpetion : NeptuneSocketExcpetion
    {

    }

    public class NeptuneSocket
    {       
        public Socket socket;
        private MemoryStream writeStream;

        private MemoryStream readStream;
        private BinaryReader reader;
        public byte[] readBuffer;
        public NeptuneSocketStatus status;

        public NeptuneSocketStatus Status
        {
            get => status;
        }

        public NeptuneSocket(Socket socket)
        {
            this.socket = socket;
            status = NeptuneSocketStatus.Inited;
            writeStream = new MemoryStream();
        }

        public byte[] SendBuffer
        {
            get => writeStream.ToArray();
        }

        public void Write(byte[] data)
        {
            if (status != NeptuneSocketStatus.Connected)
            {
                throw new NeptuneSocketNotConnectedExcpetion();
            }
            writeStream.Write(data, 0, data.Length);
        }

        public void OnConnect()
        {
            status = NeptuneSocketStatus.Connected;
            Debug.Log("=-----------------onconnect");
        }

        public void OnRecv(byte[] data)
        {
            Debug.Log("on=========recv");
        }

        public void OnClose()
        {
            status = NeptuneSocketStatus.Closed;
            Debug.Log("-----------------------onClose");
        }

        public void OnError(int errno)
        {
            status = NeptuneSocketStatus.Closed;
        }
    }

    public class NeptuneSocketSelector : MonoBehaviour
    {        
        private List<Socket> readList = new List<Socket>();
        private List<Socket> writeList = new List<Socket>();
        private Dictionary<Socket, NeptuneSocket> socketInfo = new Dictionary<Socket, NeptuneSocket>();

        public delegate void NeptuneSocketRecvEvent(Socket socket, byte[] data);
        public delegate void NeptuneSocketConnectEvent(Socket socket);
        public delegate void NeptuneSocketCloseEvent(Socket socket);
        public delegate void NeptuneSocketErrorEvent(Socket socket);

        public event NeptuneSocketRecvEvent OnRecv;
        public event NeptuneSocketCloseEvent OnClose;
        public event NeptuneSocketConnectEvent OnConnect;
        public event NeptuneSocketErrorEvent OnError;

        // Use this for initialization
        void Start()
        {
            var s1 = ConnectTo("localhost", 1313);
            var s2 = ConnectTo("localhost", 1313);            
        }

        void AddRead(Socket socket)
        {
            readList.Add(socket);
        }

        void AddWrite(Socket socket)
        {
            writeList.Add(socket);
        }

        void RemoveRead(Socket socket)
        {
            readList.Remove(socket);
        }

        void RemoveWrite(Socket socket)
        {
            writeList.Remove(socket);
        }

        Socket ConnectTo(string server, int port)
        {
            IPHostEntry hostEntry = Dns.GetHostEntry(server);
            IPEndPoint endPoint = null;

            // TODO: try next address when the previous one failed
            foreach (var address in hostEntry.AddressList)
            {
                endPoint = new IPEndPoint(address, port);
                break;
            }

            Socket socket = new Socket(endPoint.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
            socket.SetSocketOption(SocketOptionLevel.Tcp, SocketOptionName.NoDelay, 1);
            socket.Blocking = false;

            try
            {
                socket.Connect(endPoint);
            } catch (SocketException e)

            {
                // Call Connect on an nonblocking socket will raise an SocketException
                // we simply ignore it.
            }                    
            socketInfo[socket] = new NeptuneSocket(socket);
            AddWrite(socket);
            return socket;
        }

        // Update is called once per frame
        void Update()
        {
            List<Socket> errorList = new List<Socket>(writeList);
            List<Socket> readableList = new List<Socket>(readList);
            List<Socket> writeableList = new List<Socket>(writeList);

            if (readableList.Count + writeableList.Count == 0) return;

            Socket.Select(readableList, writeableList, errorList, 0);

            HashSet<Socket> removeSet = new HashSet<Socket>();

            // handle error
            foreach (var socket in errorList)
            {
                var npSocket = socketInfo[socket];
                npSocket.OnError(1);
                removeSet.Add(socket);
                Debug.Log($"----------------error------------{socket}");
            }

            // handle read
            foreach (var socket in readableList)
            {
                byte[] buffer = new byte[socket.Available];
                int n = socket.Receive(buffer);
                var npSocket = socketInfo[socket];
                if (n == 0)
                {
                    // closed
                    npSocket.OnClose();
                    removeSet.Add(socket);
                }
                else
                {
                    npSocket.OnRecv(buffer);
                }
            }

            // handle write
            foreach (var socket in writeableList)
            {
                Debug.Log($"=======weritable {socket.Poll(1, SelectMode.SelectWrite)} {socket.Poll(1, SelectMode.SelectError)}");
                if (!socket.Connected)
                {
                    // its weired, how could an unconnected socket be writeable?
                    // more weired thing is, the socket will be writable even if
                    // the server doent listen on that port...insane.
                    continue;
                }
                var npSocket = socketInfo[socket];
                if (npSocket.Status == NeptuneSocketStatus.Inited)
                {
                    npSocket.OnConnect();
                    AddRead(socket);
                }
                else
                {
                    // flush write
                    try
                    {
                        // TODO: this wont drain the sendbuffer when traffic is busy(only partial data will be sent)
                        if (npSocket.SendBuffer.Length > 0)
                        {
                            // n is the numeber of sent bytes
                            int n = socket.Send(npSocket.SendBuffer);
                        }
                    } catch (SocketException e)
                    {
                        Debug.LogError(e);
                        removeSet.Add(socket);
                    } catch (ObjectDisposedException e)
                    {
                        Debug.LogError(e);
                        removeSet.Add(socket);
                    }                    
                }
            }
          
            foreach (var socket in removeSet)
            {
                RemoveRead(socket);
                RemoveWrite(socket);
                socketInfo.Remove(socket);
            }

        }
    }
}