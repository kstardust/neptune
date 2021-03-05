import weakref
from .battle_entity import BattleEntity


class Bullet:
    def __init__(self, Attacker: BattleEntity, Target: BattleEntity):
        self.m_Attacker = weakref.proxy(Attacker)
        self.m_Target = weakref.proxy(Target)
        self.m_listBuffs = []
        self.m_Damage = None

    def SetDamage(self, Damage):
        self.m_Damage = Damage

    def AttachBuff(self, Buff):
        self.m_listBuffs.append(Buff)

    def Update(self):
        # called every frame
        if self.m_Target:
            self.m_Target.HitByBullet(self)

    def __str__(self):
        return f"Bullet DMG {self.m_Damage} {self.m_Attacker} -> {self.m_Target}"
