using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class NewBehaviourScript : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        var msg = new Messager();
        //msg.ConnectTo("stmonad.com", 80);        
        RpcTesting.Run();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
