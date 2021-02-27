from .battlefield.battleground import BattleGround
from .battlefield.battle_entity import BattleEntity
from .battlefield.railgun import Railgun
from .battlefield.scope import BinaryScope
from .battlefield.bullet import Bullet


if __name__ == '__main__':
    BG = BattleGround(1, 2)
    Entity1 = BattleEntity(1)
    Entity2 = BattleEntity(2)
    BG.AddBattleEntity(Entity1)
    BG.AddBattleEntity(Entity2)

    Entity1.AddComponent(Railgun(BinaryScope(2, BG), Bullet, 2))
    Entity2.AddComponent(Railgun(BinaryScope(1, BG), Bullet, 2))

    for i in range(600):
        BG.Update()
