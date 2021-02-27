from .components import RailgunComponent
from .battle_entity import BattleEntity


class Railgun(RailgunComponent):

    def Load(self):
        pass

    def Fire(self):
        for Target in self.m_Scope.Aim():
            Bullet = self.m_clsBulletType(self.m_Entity, Target)
            print("Fire", Bullet)
            self.m_BattleGround.PendingBulletBuffer.append(Bullet)

    def AttachToEntity(self, Entity: BattleEntity):
        self.m_Entity = Entity
        self.m_BattleGround = Entity.GetBattleGround()
        self.m_nTickID = Entity.GetBattleGround().GetTicker().InvokeRepeat(0, self.m_nAtkRate, self.Fire)
