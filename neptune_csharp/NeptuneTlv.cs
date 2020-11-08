using System;
using System.Net.Sockets;
using System.IO;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;


namespace Neptune
{
    public class Neptune
    {
        /// <summary>
        /// currently the tag field is only used to validate message
        /// </summary>
        public const ushort MagicTag = 13;
    }

    public class NeptuneTLV
    {
        public const int HeaderLength = 6;

        public NeptuneTLV()
        {
        }
       
        static public bool Unpack(byte[] tlvData, out ushort tag, out uint length)
        {
            // sizeof short  + sizeof int32 = 6
            if (tlvData.Length < HeaderLength)
            {
                tag = 0;
                length = 0;
                return false;
            }
            byte[] tagBytes = new byte[2];
            byte[] lengthBytes = new byte[4];

            Array.Copy(tlvData, 0, tagBytes, 0, 2);
            Array.Copy(tlvData, 2, lengthBytes, 0, 4);

            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(tagBytes);
                Array.Reverse(lengthBytes);
            }

            tag = BitConverter.ToUInt16(tagBytes, 0);
            length = BitConverter.ToUInt32(lengthBytes, 0);                 
            return true;
        }

        static public byte[] Pack(ushort tag, byte[] data)
        {
            byte[] tagBytes = BitConverter.GetBytes(tag);
            byte[] lengthBytes = BitConverter.GetBytes(Convert.ToUInt32(data.Length));

            if (BitConverter.IsLittleEndian)
            {
                // convert to bigendian a.k.a network-order
                Array.Reverse(tagBytes);
                Array.Reverse(lengthBytes);
            }

            byte[] res = new byte[tagBytes.Length + lengthBytes.Length + data.Length];
            int offset = 0;
            tagBytes.CopyTo(res, offset);
            offset += tagBytes.Length;
            lengthBytes.CopyTo(res, offset);
            offset += lengthBytes.Length;
            data.CopyTo(res, offset);

            return res;
        }

        public static async Task<byte[]> ReadExactly(Stream stream, int n, CancellationToken cancelToken)
        {
            cancelToken.ThrowIfCancellationRequested();

            byte[] buffer = new byte[n];
            int offset = 0;
            while (true)
            {
                if (cancelToken.IsCancellationRequested)
                {
                    return new byte[0];
                }
                int nRead = await stream.ReadAsync(buffer, offset, n);
                if (nRead == 0)
                {
                    return new byte[0];
                }

                if (nRead < n)
                {
                    offset += nRead;
                    n -= nRead;
                    continue;
                }

                return buffer;
            }
        }
    }
   
    public class NeptuneSocketMessagerClient
    {
        private readonly string address;
        private readonly int port;
        private TcpClient workConn;
        private bool isConnected = false;

        private SemaphoreSlim writeSemaphore = new SemaphoreSlim(1, 1);
        // use semaphore to simulate aync version of Monitor.Pulse
        private SemaphoreSlim pulseSemaphore = new SemaphoreSlim(0, 1);        

        private List<byte[]>[] writeBufferes = new List<byte[]>[2];
        private int currentOutputBufferIndex;

        /// <summary>
        ///  swap output buff and write buff
        /// </summary>
        private void swapBuffer()
        {            
            currentOutputBufferIndex = 1 - currentOutputBufferIndex;            
        }

        /// <summary> buff for write </summary>
        private List<byte[]> writeBuffer
        {
            get => writeBufferes[currentOutputBufferIndex];
        }

        /// <summary>buff hold data pending for send</summary> 
        private List<byte[]> outputBuffer
        {
            get => writeBufferes[1 - currentOutputBufferIndex];
        }

        public enum ErrorReason
        {
            Unknown,
        }
        
        public event EventHandler OnConnected;
        public event EventHandler OnClose;
        public event EventHandler<byte[]> OnRecv;
        public event EventHandler<ErrorReason> OnError;

        public NeptuneSocketMessagerClient(string address, int port)
        {
            this.address = address;
            this.port = port;

            for (int i = 0; i < writeBufferes.Length; i++)
            {
                writeBufferes[i] = new List<byte[]>();
            }
        }

        public bool SendMessage(byte[] message)
        {
            if (!isConnected) return false;

            writeSemaphore.Wait();
            writeBuffer.Add(NeptuneTLV.Pack(Neptune.MagicTag, message));
            writeSemaphore.Release();

            PulseWriteTask();
            return true;
        }

        public void Close()
        {
            if (!isConnected) return;
            isConnected = false;
            // there might still has an thread reading one this socket,
            // instead of closing it, we only shutdown the write direction,
            // (half-opened).
            workConn.Client.Shutdown(SocketShutdown.Send);
        }

        private void PulseWriteTask()
        {
            try
            {
                // notify WriteTask we've got new data to send.
                pulseSemaphore.Release();
            }
            catch (SemaphoreFullException)
            {
                // ignore
            }
        }

        private async Task WriteTask(CancellationToken canelToken)
        {
            canelToken.ThrowIfCancellationRequested();

            Debug.Log($"Write Task Start.");
            while (isConnected && !canelToken.IsCancellationRequested)
            {
                // wait for pulse
                await pulseSemaphore.WaitAsync();
                if (!isConnected || canelToken.IsCancellationRequested) break;

                // wait for buff lock
                await writeSemaphore.WaitAsync();

                // await workConn.GetStream().WriteAsync()                 
                try
                {
                    // hold the semaphore as short as possible
                    // cause it will block SendMessage
                    swapBuffer();
                }
                finally
                {
                    writeSemaphore.Release();
                }

                // the read thread (or the remote peer) may close the socket,
                // we need to prepare for the exceptions which may be raised during sending data.
                try
                {
                    foreach (var data in outputBuffer)
                    {
                        await workConn.GetStream().WriteAsync(data, 0, data.Length);
                    }
                    outputBuffer.Clear();
                }
                catch (Exception e)
                {
                    Debug.LogError(e);
                }
            }
            Debug.Log("Write Task Done.");
        }

        private void HandleRecv(byte[] data)
        {           
            OnRecv?.Invoke(this, data);
        }

        private void HandleError(ErrorReason reason)
        {
            isConnected = false;
            OnError?.Invoke(this, reason);
        }

        private void HandleConnected()
        {
            isConnected = true;
            OnConnected?.Invoke(this, EventArgs.Empty);
        }

        private void HandleClose()
        {
            isConnected = false;
            // when the peer says close, we close.
            workConn.Close();
            PulseWriteTask();
            OnClose?.Invoke(this, EventArgs.Empty);
        }      

        async public void Start(CancellationToken cancelToken)
        {
            cancelToken.ThrowIfCancellationRequested();
            try
            {
                TcpClient tcpClient = new TcpClient();
                // set tcp nodelay
                tcpClient.Client.NoDelay = true;

                await tcpClient.ConnectAsync(address, port);

                workConn = tcpClient;
                HandleConnected();

                Task writeTask = Task.Run(() => WriteTask(cancelToken));

                using (var networkStream = tcpClient.GetStream())
                {
                    while (true)
                    {
                        if (cancelToken.IsCancellationRequested) break;
                        byte[] tlvData = await NeptuneTLV.ReadExactly(networkStream, NeptuneTLV.HeaderLength, cancelToken);
                        if (tlvData.Length == 0)
                        {
                            break;
                        }

                        bool ok = NeptuneTLV.Unpack(tlvData, out ushort tag, out uint length);
                        if (!ok)
                        {
                            Debug.LogError("cannot unpack tlv data");
                            break;
                        }
                    
                        if (tag != Neptune.MagicTag)
                        {
                            Debug.LogError($"wrong tag expected {Neptune.MagicTag} actual {tag}");
                            break;
                        }

                        byte[] message = await NeptuneTLV.ReadExactly(networkStream, Convert.ToInt32(length), cancelToken);
                        if (message.Length == 0)
                        {
                            break;
                        }

                        HandleRecv(message);
                    }
                }
                HandleClose();
            }
            catch (Exception ex)
            {
                Debug.LogErrorFormat("exception {}", ex.ToString());
                HandleError(ErrorReason.Unknown);
            }
        }
    }
}
