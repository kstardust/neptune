class EDamageType:
    eAD = 1
    eAP = 2


class Damage:
    def __init__(self, eType, nHp):
        self.m_nValue = nHp
        self.m_eType = eType

    def __str__(self):
        return f'Damage {self.m_eType} {self.m_nValue}'
