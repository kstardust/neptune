// a very websocket wrapper for dotnet WebSocketClient

using System.Collections;
using System.Collections.Generic;
//using WebSocketSharp;
using UnityEngine;

using System.Threading;
using System.Threading.Tasks;
using System.Net.WebSockets;
using System.Net.Sockets;
using System.Text;
using System;

namespace STWebSocket
{
    using WebSocket = System.Net.WebSockets.WebSocket;

    public class WebsocketMessager
    {        
        private const Int64 BufferSize = 4 * 1024 * 1024;
        private string uri;
        private ClientWebSocket workConn;
        private byte[] bytesBuffer = new byte[BufferSize];

        public delegate void WSEvent(int code, string data);
        public event EventHandler<byte[]> OnRecv;
        public event EventHandler OnClose;
        public event EventHandler OnConnected;
        public event EventHandler<string> OnError;

        private List<byte[]> outputQueue;
        private readonly object sendingLock = new object();
        private bool isSending = false;

        public WebsocketMessager(string uri)
        {
            this.uri = uri;
        }

        private void _OnConnected()
        {
            Debug.Log("STWebSocket Connected");
            OnConnected?.Invoke(this, EventArgs.Empty);           
        }

        private void _OnRecv(byte[] data)
        {
            Debug.Log($"STWebSocket Recv {Encoding.UTF8.GetString(data)}");
            OnRecv?.Invoke(this, data);           
        }

        private void _OnClose()
        {
            Debug.Log($"STWebSocket OnClose");
            OnClose?.Invoke(this,EventArgs.Empty);
        }

        private void _OnError(string error)
        {
            Debug.Log($"STWebSocket OnError {error}");
            OnError?.Invoke(this, error);            
        }

        public void Close()
        {
            // Tt seems that CloseAsync is not the right method for closing an ws connection...
            // call CloseOutputAsync will send an Close Message to peer thus close the write
            // side of ws(half-opened), and when the other side response an Close Message,
            // the ReceiveAsync will received it.
            // Similiar discussion here https://github.com/dotnet/runtime/issues/17819
            workConn.CloseOutputAsync(WebSocketCloseStatus.NormalClosure, "", CancellationToken.None);
        }

        private void StartRead()
        {
            WebSocketReceiveResult result;
            Task<WebSocketReceiveResult> task;
            long length;
 
            while (true)
            {
                var buffer = new ArraySegment<byte>(bytesBuffer, 0, bytesBuffer.Length);
                length = 0;
                do
                {
                    task = workConn.ReceiveAsync(buffer, CancellationToken.None);
                    try
                    {
                        task.Wait();
                    }
                    catch (AggregateException ae)
                    {
                        var e = ae.InnerException;
                        _OnError(e.ToString());
                        return;
                    }

                    result = task.Result;
                    length += result.Count;
                } while (!result.EndOfMessage && result.MessageType != WebSocketMessageType.Close);

                if (result.MessageType == WebSocketMessageType.Close)
                {
                    _OnClose();
                    break;
                }

                byte[] output = new byte[length];
                Array.Copy(buffer.Array, output, length);
                _OnRecv(output);
            }
        }

        public void SendText(string message)
        {
            Send(Encoding.UTF8.GetBytes(message), WebSocketMessageType.Text);
        }

        public void SendBinary(byte[] bytes)
        {
            Send(bytes, WebSocketMessageType.Binary);
        }

        public void Send(byte[] data, WebSocketMessageType type)
        {
            if (data.Length == 0) return;
            bool canSend;
            lock (sendingLock)
            {
                canSend = !isSending;
                isSending = true;
            }

            if (canSend)
            {
                // we got the sending lock
                var task = workConn.SendAsync(new ArraySegment<byte>(data, 0, data.Length), type, true, CancellationToken.None);
                try
                {
                    task.Wait();
                }
                finally
                {
                    lock (sendingLock)
                    {
                        isSending = false;
                    }
                }                                               
            }
            else
            {
                outputQueue.Add(data);
            }

        }

        public void Start()
        {
            Task task = new Task(() => ConnectAsync());
            task.Start();
        }

        public void ConnectAsync()
        {
            workConn = new ClientWebSocket();
            Task task = workConn.ConnectAsync(new System.Uri(uri), CancellationToken.None);

            try
            {
                task.Wait();                
            }
            catch (AggregateException ae)
            {
                var e = ae.InnerException;
                Debug.Log(e);
                _OnError(e.ToString());
                return;
            }

            _OnConnected();
            StartRead();                                                        
        }

    }
}