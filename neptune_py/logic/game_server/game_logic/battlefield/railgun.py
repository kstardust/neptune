from .components import RailgunComponent
from .battle_entity import BattleEntity
from .damage import Damage, EDamageType


class Railgun(RailgunComponent):

    def Load(self):
        pass

    def Fire(self):
        for Target in self.m_Scope.Aim():
            Bullet = self.m_clsBulletType(self.m_Entity, Target)
            Bullet.SetDamage(Damage(EDamageType.eAD, self.m_Entity.m_Attributes.m_nAttackDamage))
            print("Fire", Bullet)
            self.m_BattleGround.PendingBulletBuffer.append(Bullet)

    def AttachToEntity(self, Entity: BattleEntity):
        self.m_Entity = Entity
        self.m_BattleGround = Entity.GetBattleGround()
        self.m_nTickID = Entity.GetBattleGround().GetTicker().InvokeRepeat(0, self.m_nAtkRate, self.Fire)

    def DetachFromEntity(self, Entity: BattleEntity):
        Entity.GetBattleGround().GetTicker().CancelTick(self.m_nTickID)
