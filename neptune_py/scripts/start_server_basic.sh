cd ../..

echo "start router manager"
nohup python -m neptune_py.logic.router_manager.main 2>&1  > /tmp/router_manager.log &  echo $! > /tmp/router_manger.pid
sleep 1;
echo "start router"
nohup python -m neptune_py.logic.router_server.main 2>&1 > /tmp/router_server.log &  echo $! > /tmp/router_server.pid
sleep 1;
echo "start game server"
nohup python -m neptune_py.logic.game_server.main 2>&1 > /tmp/game_server.log &  echo $! > /tmp/game_server.pid
sleep 1;
echo "start gate server"
nohup python -m neptune_py.logic.gate_server.main 2>&1 > /tmp/gate_server.log &  echo $! > /tmp/gate_server.pid

