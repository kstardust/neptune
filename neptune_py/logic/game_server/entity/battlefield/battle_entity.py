import collections
from .components import ComponentMixin


class BattleEntity:
    def __init__(self, eCamp):
        self.m_eCamp = eCamp
        self.m_BattleGround = None
        self.m_Id = None
        self.m_dictComponents = collections.defaultdict(set)

    def AddComponent(self, Component: ComponentMixin):
        self.m_dictComponents[Component.m_eType].add(Component)
        Component.AttachToEntity(self)

    def RemoveComponent(self, Component: ComponentMixin):
        if Component not in self.m_dictComponents[Component.eType]:
            return
        Component.DetachFromEntity(self)
        self.m_dictComponents[Component.m_eType].discard(Component)

    def GetComponentByType(self, eComponentType):
        # get the first component(actually a random one cause set is unordered)
        setComponents = self.GetComponentsByType(eComponentType)
        if setComponents:
            return setComponents[0]

    def GetComponentsByType(self, eComponentType):
        return self.m_dictComponents[eComponentType]

    def Update(self):
        # called every frame
        pass

    def OnEnterBattleGround(self, nEntityID, BattleGroud):
        self.m_BattleGround = BattleGroud
        self.m_Id = nEntityID

    def GetBattleGround(self):
        return self.m_BattleGround

    def OnDamage(self, Damage):
        pass

    def AddBuff(self, Buff):
        pass

    def HitByBullet(self, Bullet):
        print(f"{self} hit by bullet")

    def __str__(self):
        return f"Entity {self.m_Id}"
