import collections
import itertools
from .components import ComponentMixin


class BattleEntityAttributes:
    def __init__(self):
        pass

    def Init(self):
        self.m_nHp = 1000
        self.m_nEnergy = 0
        self.m_nAbilityEnergy = 100

        self.m_nAttackDamage = 100

        self.m_nArmor = 10
        self.m_nAgility = 100


class BattleEntity:
    def __init__(self, eCamp):
        self.m_eCamp = eCamp
        self.m_BattleGround = None
        self.m_Id = None
        self.m_dictComponents = collections.defaultdict(set)
        self.m_bDead = False
        self.m_Attributes = BattleEntityAttributes()
        self.m_Attributes.Init()

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

    def Dead(self):
        self.BeforeDead()
        self.m_bDead = True
        for Component in itertools.chain.from_iterable(self.m_dictComponents.values()):
            Component.DetachFromEntity(self)
        self.m_BattleGround.OnEntityDead(self)
        self.AfterDead()

    def AfterDead(self):
        pass

    def BeforeDead(self):
        pass

    def OnDamage(self, Damage):
        if self.m_bDead:
            return

        self.m_Attributes.m_nHp -= Damage.m_nValue
        if self.m_Attributes.m_nHp <= 0:
            self.Dead()

    def AddBuff(self, Buff):
        if self.m_bDead:
            return
        pass

    def HitByBullet(self, Bullet):
        if self.m_bDead:
            return

        self.OnDamage(Bullet.m_Damage)
        print(f"{self} hit by bullet {Bullet.m_Damage} HP: {self.m_Attributes.m_nHp}")

    def __str__(self):
        return f"Entity {self.m_Id}"
