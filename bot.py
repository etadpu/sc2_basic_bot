import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR


class sc2Bot(sc2.BotAI):

  ####################### STEPPER ###############################
    
    async def on_step(self, iteration):
        # what to do every step
        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        
  ###############################################################


    async def build_workers(self):
        # nexus = command center
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    
    async def build_pylons(self):
      if self.supply_left < 6 and not self.already_pending(PYLON) and self.can_afford(PYLON):
        # nexuses = self.units(NEXUS).ready  // nexus basically always exists
        nexuses = self.units(NEXUS).ready
        if nexuses.exists:
          await self.build(PYLON, near=nexuses.first)

    async def build_assimilators(self):
      for nexuses in self.units(NEXUS).ready:
        # all vaspene closer than 20 from nexus
        vaspenes = self.state.vespene_geyser.closer_than(20.0, nexuses)
        for vaspene in vaspenes:
          # if we can afford and as long as there are no assimilators closer than 1 from the current vaspene
          # meaning, assimilator on top of vaspene 
          if self.can_afford(ASSIMILATOR) and not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
            # select a worker near vaspene position
            worker = self.select_build_worker(vaspene.position)
            if worker is None:
              break
            # build assimilator on top of the vaspene
            await self.do(worker.build(ASSIMILATOR, vaspene))

####################### RUNNER ###############################

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, sc2Bot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=False)

###############################################################