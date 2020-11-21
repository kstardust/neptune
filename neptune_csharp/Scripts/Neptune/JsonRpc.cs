using System;
using System.Reflection;
using UnityEngine;
using Newtonsoft.Json;
using System.Text;

namespace Neptune
{
    public class JsonRpc
    {
        public string methodName;
        public string[] args;
    }

    public class TestRpcEntity
    {
        public TestRpcEntity()
        {
        }

        public void RpcMethodFoobar(int arg1, string arg2)
        {
            Debug.Log($"RpcMethodFoobar {arg1} {arg2}");
        }
    }

    public class NeptuneRpc
    {
        private object entity;
        private object stub;
        private INeptuneMessager messager;

        public NeptuneRpc(object entity, INeptuneMessager messager)
        {
            this.entity = entity;
            this.messager = messager;    
        }

        public void Init()
        {
        }

        public void Call(string jsonData)
        {
            JsonRpc jrpc = JsonConvert.DeserializeObject<JsonRpc>(jsonData);
            Type entityType = this.entity.GetType();
            
            MethodInfo method = entityType.GetMethod(jrpc.methodName);
            if (method == null)
            {
                Debug.LogError($"No such method: {jrpc.methodName}");
                return;
            }

            ParameterInfo[] paramsInfo = method.GetParameters();
            if (paramsInfo.Length != jrpc.args.Length)
            {
                Debug.LogError(
                    $"Method parameter num not match, expect: {paramsInfo.Length} actual: {jrpc.args.Length}"
                );
                return;
            }

            object[] paramObjs = new object[paramsInfo.Length];
            for (int i = 0; i < paramsInfo.Length; i++)
            {
                paramObjs[i] = JsonConvert.DeserializeObject(jrpc.args[i], paramsInfo[i].ParameterType);
            }

            method.Invoke(this.entity, paramObjs);
        }

        public string EncodeCall(string method, params object[] args)
        {
            JsonRpc jrpc = new JsonRpc();
            jrpc.methodName = method;
            string[] argList = new string[args.Length];
            for (int index = 0; index < args.Length; index++)
            {
                argList[index] = JsonConvert.SerializeObject(args[index]);
            }
            jrpc.args = argList;
            return JsonConvert.SerializeObject(jrpc);
        }

        public void RpcCall(string method, params object[] args)
        {
            messager.SendMessage(NeptuneMessageType.Call, Encoding.UTF8.GetBytes(EncodeCall(method, args)));
        }
    }

    //public class RpcTesting
    //{
    //    public static void Run()
    //    {
    //        NeptuneRpc rpc = new NeptuneRpc(new TestRpcEntity(), 1);
    //        string result = rpc.EncodeCall("RpcMethodFoobar", 13, "13");
    //        rpc.Call(result);
    //    }
    //}
}