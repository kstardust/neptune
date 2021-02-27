import abc


class EComponentType:
    eRailgun = 1
    eActiveAbility = 2
    ePassiveAbility = 3


class ComponentMixin:
    @abc.abstractmethod
    def AttachToEntity(self, Entity):
        pass

    @abc.abstractclassmethod
    def DetachFromEntity(self, Entity):
        pass

    @abc.abstractproperty
    def m_eType(self):
        pass


class ScopeComponent:
    def __init__(self, nTargetCamp, BattleGround):
        self.m_BattleGround = BattleGround
        self.m_nTargetCamp = nTargetCamp

    @abc.abstractmethod
    def Aim(self):
        pass


class RailgunComponent(ComponentMixin):
    def __init__(self, Scope: ScopeComponent, BulletType, nAtkSpeed):
        self.m_Scope = Scope
        self.m_clsBulletType = BulletType
        self.m_nAtkRate = 1 / nAtkSpeed

    @abc.abstractmethod
    def Load(self):
        pass

    @abc.abstractmethod
    def Fire():
        pass
