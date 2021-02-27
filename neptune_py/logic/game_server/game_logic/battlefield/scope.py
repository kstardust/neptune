from .components import ScopeComponent


class BinaryScope(ScopeComponent):
    def Aim(self):
        return self.m_BattleGround.GetEntitiesByCamp(self.m_nTargetCamp)
