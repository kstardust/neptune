from neptune_py.skeleton import tick


class BattleGround:
    def __init__(self, *eCamps):
        self.m_dictBattleEntiteCamps = {
            i: {} for i in eCamps
        }
        self._m_listBulletsDoubleBuffer = [[], []]
        self._m_nCurrentBulletBufferIndex = 0
        self.m_nEntityID = 0
        self.m_Ticker = None
        self.m_Ticker = tick.NeptuneTicker()

        self.m_nFrames = 0
        # reversed, place to keep other global status
        self._m_GlobalStatus = {}

    def GetGlobalStatus(self, eKey):
        return self._m_GlobalStatus.get(eKey)

    def AddBattleEntity(self, BattleEntity):
        nID = self.GenEntitiyID()
        BattleEntity.OnEnterBattleGround(nID, self)
        self.m_dictBattleEntiteCamps[BattleEntity.m_eCamp][nID] = BattleEntity

    def GetEntitiesByCamp(self, eCamp):
        return self.m_dictBattleEntiteCamps[eCamp].values()

    @property
    def CurrentBulletBuffer(self):
        return self._m_listBulletsDoubleBuffer[self._m_nCurrentBulletBufferIndex]

    @property
    def PendingBulletBuffer(self):
        return self._m_listBulletsDoubleBuffer[1-self._m_nCurrentBulletBufferIndex]

    def SwapBulletBuffer(self):
        self._m_nCurrentBulletBufferIndex = 1 - self._m_nCurrentBulletBufferIndex

    def GenEntitiyID(self):
        self.m_nEntityID += 1
        return self.m_nEntityID

    def GetTicker(self):
        return self.m_Ticker

    def UpdateEntites(self):
        for dictCampEntities in self.m_dictBattleEntiteCamps.values():
            for Entity in dictCampEntities.values():
                Entity.Update()

    def UpdateBullets(self):
        for Bullet in self.CurrentBulletBuffer:
            Bullet.Update()
        self.CurrentBulletBuffer.clear()

    def Update(self):
        self.m_nFrames += 1
        print(f"Frame: {self.m_nFrames} --------------------")
        self.UpdateEntites()
        self.UpdateBullets()
        self.m_Ticker.Update()
        self.SwapBulletBuffer()
