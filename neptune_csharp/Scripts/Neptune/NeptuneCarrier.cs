using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Threading;
using UnityEngine;
using System;


namespace Neptune
{
    public delegate void EventConnect();
    public delegate void EventClose();
    public delegate void EventError(int errno);
    public delegate void EventRecv(NeptuneMessageType mType, byte[] data);

    public class NeptuneMessagerFE
    {
        public event EventConnect OnConnect;
        public event EventClose OnClose;
        public event EventRecv OnRecv;
        public event EventError OnError;

        private int mid;
        private INeptuneMessager messager;

        public int Mid
        {
            get => mid;
        }

        public NeptuneMessagerFE(INeptuneMessager messager, int mid)
        {
            this.mid = mid;
            this.messager = messager;
        }

        public void InvokeOnConnect()
        {
            OnConnect?.Invoke();
        }

        public void InvokeOnClose()
        {
            OnClose?.Invoke();
        }

        public void InvokeOnError(int errno)
        {
            OnError?.Invoke(errno);
        }

        public void InvokeRecv(NeptuneMessageType mType, byte[] data)
        {
            OnRecv?.Invoke(mType, data);
        }

        public void Close()
        {
            messager.Close();
        }

        public void Send(NeptuneMessageType mType, byte[] message)
        {
            messager.SendMessage(mType, message);
        }
    }

    public class NeptuneCarrier : MonoBehaviour
    {
        private Dictionary<int, NeptuneMessagerFE> messagers = new Dictionary<int, NeptuneMessagerFE>();

        private Dictionary<int, List<NeptuneMessage>>[] readablesDoubleBuffer = new Dictionary<int, List<NeptuneMessage>>[2];
        private int readablesIndex = 0;

        private Dictionary<int, int> errorEvents = new Dictionary<int, int>();
        private HashSet<int> closeEvents = new HashSet<int>();
        private HashSet<int> connectEvents = new HashSet<int>();

        private SemaphoreSlim connectSemaphore = new SemaphoreSlim(1, 1);
        private SemaphoreSlim errorSemaphore = new SemaphoreSlim(1, 1);
        private SemaphoreSlim closeSemaphore = new SemaphoreSlim(1, 1);
        // we use one giant lock for all connections, but I suppose it's enough for client-side.
        private SemaphoreSlim readSemaphore = new SemaphoreSlim(1, 1);

        private int messagerId = 0;

        private int NewMsgId
        {
            get => messagerId++;
        }

        public Dictionary<int, List<NeptuneMessage>> readableEvents
        {
            get => readablesDoubleBuffer[readablesIndex];
        }

        public Dictionary<int, List<NeptuneMessage>> readableEventsWrite
        {
            get => readablesDoubleBuffer[1 - readablesIndex];
        }

        public void swapReadables()
        {
            readSemaphore.Wait();
            readablesIndex = 1 - readablesIndex;
            readSemaphore.Release();
        }

        public void Start()
        {
            for (int i = 0; i < readablesDoubleBuffer.Length; i++)
            {
                readablesDoubleBuffer[i] = new Dictionary<int, List<NeptuneMessage>>();
            }
        }

        // override this method to provide custom messager backend type
        public INeptuneMessager GenMessagerBackend(string address, int port)
        {
            return new NeptuneTypedMessager(new NeptuneTlvMessagerClient(address, port));
        }

        public NeptuneMessagerFE Dial(string address, int port)
        {
            INeptuneMessager messager = GenMessagerBackend(address, port);

            int mid = NewMsgId;
            messager.OnClose += (_, e) => { OnClose(mid, e); };
            messager.OnConnected += (_, e) => { OnConnected(mid, e); };
            messager.OnMessage += (_, e) => { OnRecv(mid, e); };
            messager.OnError += (_, e) => { OnError(mid, e); };

            Task.Run(messager.Start);
            messagers[mid] = new NeptuneMessagerFE(messager, mid);
            return messagers[mid];
        }

        private void OnConnected(int mid, EventArgs e)
        {
            if (messagers.ContainsKey(mid))
            {
                connectSemaphore.Wait();
                connectEvents.Add(mid);
                connectSemaphore.Release();
            }
        }

        private void OnRecv(int mid, NeptuneMessage e)
        {            
            if (messagers.ContainsKey(mid))
            {
                readSemaphore.Wait();
                try
                {
                    bool ok = readableEventsWrite.TryGetValue(mid, out List<NeptuneMessage> value);
                    if (ok)
                    {
                        value.Add(e);
                    }
                    else
                    {
                        readableEventsWrite[mid] = new List<NeptuneMessage> { e };
                    }
                }
                finally
                {
                    readSemaphore.Release();
                }
            }
        }

        private void OnClose(int mid, EventArgs e)
        {
            if (messagers.ContainsKey(mid))
            {
                closeSemaphore.Wait();
                closeEvents.Add(mid);
                closeSemaphore.Release();
            }
        }

        private void OnError(int mid, int errocode)
        {
            if (messagers.ContainsKey(mid))
            {
                errorSemaphore.Wait();
                try
                {
                    errorEvents[mid] = errocode;
                }
                finally
                {
                    errorSemaphore.Release();
                }
            }
        }

        private void ProcessErrorEvent()
        {
            Dictionary<int, int> errors = new Dictionary<int, int>();
            try
            {
                connectSemaphore.Wait();
                errors = new Dictionary<int, int>(errorEvents);
                errorEvents.Clear();
            }
            finally
            {
                connectSemaphore.Release();
            }

            foreach (KeyValuePair<int, int> kv in errors)
            {
                bool ok = messagers.TryGetValue(kv.Key, out NeptuneMessagerFE value);
                if (ok)
                {
                    value.InvokeOnError(kv.Value);
                    messagers.Remove(kv.Value);
                }
                else
                {
                    Debug.LogError($"ERROR: no such messager {kv.Key}");
                }
            }
        }

        private void ProcessCloseEvent()
        {
            HashSet<int> closes = new HashSet<int>();
            try
            {
                closeSemaphore.Wait();
                closes = new HashSet<int>(closeEvents);
                closeEvents.Clear();
            }
            finally
            {
                closeSemaphore.Release();
            }

            foreach (int mid in closes)
            {
                bool ok = messagers.TryGetValue(mid, out NeptuneMessagerFE messager);
                if (ok)
                {
                    messager.InvokeOnClose();
                    messagers.Remove(mid);
                }
                else
                {
                    Debug.LogError($"ERROR: no such messager {mid}");
                }
            }
        }

        private void ProcessConnectedEvent()
        {
            HashSet<int> connects = new HashSet<int>();
            try
            {
                connectSemaphore.Wait();
                connects = new HashSet<int>(connectEvents);
                connectEvents.Clear();
            }
            finally
            {
                connectSemaphore.Release();
            }

            foreach (int mid in connects)
            {
                bool ok = messagers.TryGetValue(mid, out NeptuneMessagerFE messager);
                if (ok)
                {
                    messager.InvokeOnConnect();
                }
                else
                {
                    Debug.LogError($"ERROR: no such messager {mid}");
                }
            }
        }

        private void ProcessRecvEvent()
        {
            swapReadables();

            foreach (var readable in readableEvents)
            {
                bool ok = messagers.TryGetValue(readable.Key, out NeptuneMessagerFE messager);
                if (ok)
                {
                    foreach (var msg in readable.Value)
                    {
                        messager.InvokeRecv(msg.mType, msg.payload);
                    }
                }
                else
                {
                    Debug.LogError($"ERROR: no such messager {messager}");
                }
            }
            readableEvents.Clear();
        }

        // Update is called once per frame
        void Update()
        {
            ProcessErrorEvent();
            ProcessCloseEvent();
            ProcessConnectedEvent();
            ProcessRecvEvent();
        }
    }
}