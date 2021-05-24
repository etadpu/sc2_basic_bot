import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.game_data import GameData
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
   CYBERNETICSCORE, STALKER


class sc2Bot(sc2.BotAI):

  ####################### STEPPER ###############################
    
    async def on_step(self, iteration):
        # distribute_workers() is ready made from bot_ai.py
        await self.distribute_workers() 
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.go_expand()
        #await self.build_fighter_unit_buildings()
        #await self.build_gateways(4)
        await self.build_one_gateway()
        await self.build_cyberneticscore()
        await self.build_stalkers()

  ###############################################################


    async def build_workers(self):
        # nexus = command center
        for nexus in self.units(NEXUS).ready.idle:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    
    async def build_pylons(self):
      if self.supply_left < 6 and not self.already_pending(PYLON) and self.can_afford(PYLON):
        # nexus = self.units(NEXUS).ready  // nexus basically always exists
        nexus = self.units(NEXUS).ready
        if nexus.exists:
          await self.build(PYLON, near=nexus.first)


    async def build_assimilators(self):
      for nexus in self.units(NEXUS).ready:
        # all vaspene closer than 20 from nexus
        vaspenes = self.state.vespene_geyser.closer_than(16.0, nexus)
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


    async def go_expand(self):
      if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
        # most things are already handled for us with expand_now()
        await self.expand_now()


# TODO fix building placements
    async def build_fighter_unit_buildings(self):
      if self.units(PYLON).ready.exists:
        pylon = self.units(PYLON).ready.random
        if self.units(GATEWAY).ready.exists:
          if \
            not self.units(CYBERNETICSCORE) \
              and not self.already_pending(CYBERNETICSCORE)\
                 and self.can_afford(CYBERNETICSCORE):
            await self.build(CYBERNETICSCORE, near=pylon)
        else:
          if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
            await self.build(GATEWAY, near=pylon)


# TODO fix positions of buildings. its clogging up the mining area
# TODO refactor getPylon
    async def build_gateways(self, number_of_gateways):
      # Needed to avoid crash
      if self.units(PYLON).ready.exists and self.units(GATEWAY).amount < number_of_gateways and self.can_afford(GATEWAY) and self.already_pending(GATEWAY) < number_of_gateways:
        # Get a random pylon (from our already built pylons)
        pylon = self.units(PYLON).ready.random
        # Gotta check already pending, otherwise we crash and burn
        await self.build(GATEWAY, near=pylon)
    
    
    async def build_one_gateway(self):
      if self.units(PYLON).ready.exists and not self.units(GATEWAY).exists and self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
        pylon = self.units(PYLON).ready.random
        await self.build(GATEWAY, near=pylon)


    async def build_cyberneticscore(self):
      if self.units(GATEWAY).ready.exists and self.units(PYLON).ready.exists and not self.units(CYBERNETICSCORE) and self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
        pylon = self.units(PYLON).ready.random
        await self.build(CYBERNETICSCORE, near=pylon)

    async def build_stalkers(self):
      for gateway in self.units(GATEWAY).ready.idle:
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(STALKER) and self.supply_left > 0:
          await self.do(gateway.train(STALKER))



            

####################### RUNNER ###############################

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, sc2Bot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=False)

###############################################################