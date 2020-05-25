## TO DO LIST:
## 1: DECIDE HOW TMs AND CAPSULEs ARE CLASSED (i.e. make the classes for them, dimwit)
## 2: DECIDE HOW THEY ARE STORED WITHIN THE TRAINER CLASS
## 3: MAKE THE ARENA CLASS. ARE MOVE AND ABILITY FUNCTIONS STORED HERE?

import random as r
import math as m

## Stats stored as a tuple as they shouldn't be changed, alongside the abilities.
## (hp, atk, def, sp.atk, sp.def,speed)
pkmnInfo = {
    'Bulbasaur' : {'stats' : (45,49,49,65,65,45), 'ability' : ['Overgrow','Chlorophyll'], 'moves' : ['Growl','Tackle','Vine Whip','Leech Seed']}
    }

## Natures are stored with name alongside the tuple showing how it affects stat growth
natures = [
    ['Adamant',(1, 1.1, 1, 0.9, 1, 1)],
           ]

class pokemon:
    def __init__(self,species,level):
        
        global pkmnInfo
        self.base = pkmnInfo[species]['stats']
        self.iv = self.ivGenerate() ## generates a random spread of ivs, ex. (31,2,8,28,19,12)
        self.ability = r.choice(pkmnInfo[species]['ability'])
        self.ev = [0,0,0,0,0,0] ## needs to be a list so that it can be changed
        self.level = level
        self.stats = [0,0,0,0,0,0]

        global natures ## need to select a nature to affect stats
        self.nature = r.choice(natures)

        self.moves = r.sample(pkmnInfo[species]['moves'],k=4)
        
        self.statCalculate()

    def ivGenerate(self):
        return (r.randint(0,31),r.randint(0,31),r.randint(0,31),r.randint(0,31),r.randint(0,31),r.randint(0,31))

    def statCalculate(self):
        self.stats[0] = int(((2*self.base[0]+self.iv[0]+self.ev[0]/4)*self.level)/100)+10+self.level
        for x in range(1,6):
            self.stats[x] = int((int(((2*self.base[x]+self.iv[x]+self.ev[x]/4)*self.level)/100)+5)*self.nature[1][x])

    def changeLevel(self,newLevel):
        self.level = newLevel
        self.statCalculate()

class trainer:
    def __init__(self,name,sprite):
        self.name = name

        self.sprite = sprite
        
        ## pokemon data will *always* be stored in the box... the team system will simply be the box
        ## positions of the pokemon in the team. as this is sort of a battle tower-esque mode, there
        ## is no need for the player to be physically using the box except when storing new pkmn
        ## furthermore, temporary pokemon have their own storage system. see tempteam.
        ## tldr; team/box is when user isn't borrowing pokemon, tempteam is their team when they are
        self.team = {
            '1' : 'empty',
            '2' : 'empty',
            '3' : 'empty',
            '4' : 'empty',
            '5' : 'empty',
            '6' : 'empty'
            }
        self.teamCount = 0
        
        self.box = {}
        self.boxCount = 0
        
        self.tempteam = {
            '1' : 'empty',
            '2' : 'empty',
            '3' : 'empty',
            '4' : 'empty',
            '5' : 'empty',
            '6' : 'empty'
            }
        self.tempTeamCount = 0

        self.healingItems = {
            'Potion' : 5,
            'Super Potion' : 0,
            'Hyper Potion' : 0,
            'Max Potion' : 0,
            'Full Restore' : 0,
            'Full Heal' : 0
            }


        ## MARKER START: Unfinished TMs/Capsules tracking within player
        ## PROJECT: Storage within the trainer class of TMs and Capsules so that they may be more easily accessed.
        ## INFORMATION:
        ## Here and to next marker need renovating, as I'm not sure this storage system will work. It may end up,
        ## as it currently is, that the identifier number system may be used. But what if TM #1 gets used up?
        ## Then we'd have slot 1 empty with no way of reassigning. Perhaps this is ok but I really really don't
        ## like it.
        ## END INFORMATION
        
        self.tms = {} ## technical machines, used to teach pokemon new moves, are stored here
        self.tmBP = 0
        self.tmFP = 0

        self.capsules = {} ## ability capsules, used to give pokemon new abilities, are stored here
        self.capsuleCount = 0

        ## MARKER END: Unfinished TMs/Capsules tracking within player
        
    def getNewPokemon(self,pkmn,tempFlag):
        if tempFlag != 'temp':
            self.box[str(self.boxCount)] = pkmn
            self.boxCount += 1
        else:
            self.tempTeam[str(self.tempTeamCount)] = pkmn
            self.tempTeamCount += 1

    def getNewTM(self,tm): ##FIX THIS, UNFINISHED
        self.tms[str(self.tmFP)] = tm
        self.tmFP += 1

    






