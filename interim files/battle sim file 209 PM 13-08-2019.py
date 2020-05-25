## TO DO LIST:
## 1: DECIDE HOW TMs AND CAPSULEs ARE CLASSED (i.e. make the classes for them, dimwit)
## 2: DECIDE HOW THEY ARE STORED WITHIN THE TRAINER CLASS
## 3: MAKE THE ARENA CLASS. ARE MOVE AND ABILITY FUNCTIONS STORED HERE?
## 4: FINISH WRITING THE processTurn() FUNCTION
##  4a: Finish writing the switchPokemon function
## 5: FINISH WRITING THE move CLASS
## 6: Make it so that Pokemon can use a move in processTurn()!!!

import random as r
import math as m
from triggerQueue import *

## Stats stored as a tuple as they shouldn't be changed, alongside the abilities.
## (hp, atk, def, sp.atk, sp.def,speed)
pkmnInfo = {
    'Bulbasaur' : {'stats' : (45,49,49,65,65,45), 'type1' : 'Grass', 'type2' : 'Poison', 'ability' : ['Overgrow','Chlorophyll'], 'moves' : ['Growl','Tackle','Vine Whip','Leech Seed']}
    }

## Natures are stored with name alongside the tuple showing how it affects stat growth
natures = [
    ['Adamant',(1, 1.1, 1, 0.9, 1, 1)],
           ]

class pokemon:
    def __init__(self,species,level,trainer):
        
        global pkmnInfo
        self.base = pkmnInfo[species]['stats']
        self.iv = self.ivGenerate() ## generates a random spread of ivs, ex. (31,2,8,28,19,12)
        self.ability = r.choice(pkmnInfo[species]['ability'])

        self.type1 = pkmnInfo[species]['type1']
        self.type2 = pkmnInfo[species]['type2']

        global natures ## need to select a nature to affect stats
        self.nature = r.choice(natures)

        self.moveNames = r.sample(pkmnInfo[species]['moves'],k=4)
        self.moves = []
        global moveInfo
        for nameOfMove in moveNames:
            self.moves.append([move(nameOfMove,self), moveInfo[nameOfMove]['pp']])
        
        self.ev = [0,0,0,0,0,0] ## needs to be a list so that it can be changed
        self.level = level
        self.stats = (0,0,0,0,0,0)
        self.statCalculate()
        self.hp = self.stats[0]

        self.status = None
        self.statusCount = 0 ##counts time 

        self.shiny = False
        self.nickname = species
        self.species = species

        self.chosenMove = None
        self.trainer = trainer
        

    def ivGenerate(self):
        return (r.randint(0,31),r.randint(0,31),r.randint(0,31),r.randint(0,31),r.randint(0,31),r.randint(0,31))

    def statCalculate(self):
        self.stats = list(self.stats)
        self.stats[0] = int(((2*self.base[0]+self.iv[0]+self.ev[0]/4)*self.level)/100)+10+self.level
        for x in range(1,6):
            self.stats[x] = int((int(((2*self.base[x]+self.iv[x]+self.ev[x]/4)*self.level)/100)+5)*self.nature[1][x])
        self.stats = tuple(self.stats)
        
    def changeLevel(self,newLevel):
        self.level = newLevel
        self.statCalculate()

    def takeDamage(self,damage,nonCombat=False):
        self.hp -= damage
        if not nonCombat:
            self.lastDamage = damage

moveInfo = {
    'Tackle' : {'type' : 'Normal', 'category' : 'Physical', 'description' : "The user rams its body into its opponent.", 'power' : '40', 'pp' : 35, 'function' : 'Tackle(self.pokemon.trainer.number)'}
    }

class move:
    def __init__(self,name,pokemon):
        global moveInfo
        self.name = name
        self.type = moveInfo[name]['type']
        self.category = moveInfo[name]['category']
        self.description = moveInfo[name]['description']
        self.power = moveInfo[name]['description']
        self.maxPP = moveInfo[name]['description']

abilityInfo = {
    'Intimidate' : {'type' : 'enter', 'description' : "Lowers opponent's attack by one stage.", 'function' : 'Intimidate(self.pokemon.trainer.number)'}
    }

class ability:
    def __init__(self,name,pokemon):
        global abilityInfo
        self.name = name
        self.type = abilityInfo[name]['type']
        self.description = abilityInfo[name]['description']
        self.function = abilityInfo[name]['function']
        self.pokemon = pokemon

    def activate(self):
        exec(self.function)
    

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
            '1' : None,
            '2' : None,
            '3' : None,
            '4' : None,
            '5' : None,
            '6' : None
            }
        self.teamCount = 0
        
        self.box = {}
        self.boxCount = 0
        
        self.tempteam = {
            '1' : None,
            '2' : None,
            '3' : None,
            '4' : None,
            '5' : None,
            '6' : None
            }
        self.tempTeamCount = 0

        self.healingItems = {
            'Potion' : 0,
            'Super Potion' : 0,
            'Hyper Potion' : 0,
            'Max Potion' : 0,
            'Full Restore' : 0,
            'Full Heal' : 0
            }

        self.active = None


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
        
    def getNewPokemon(self,pkmn,tempFlag=False):
        if tempFlag:
            self.box[str(self.boxCount)] = pkmn
            self.boxCount += 1
        else:
            self.tempTeam[str(self.tempTeamCount)] = pkmn
            self.tempTeamCount += 1

    def getNewTM(self,tm): ##FIX THIS, UNFINISHED
        self.tms[str(self.tmFP)] = tm
        self.tmFP += 1

    def receiveNumber(self,num):
        self.number = num



class Arena:
    def __init__(self,trainer1,trainer2,tempFlag = True):
        self.trainer1 = trainer1
        trainer1.receiveNumber(1)
        
        self.trainer2 = trainer2
        trainer2.receiveNumber(2)

        self.trainerCount = 2
        
        if tempFlag:
            self.t1pkmn = trainer1.tempTeam['1']
            self.t2pkmn = trainer2.tempTeam['1']
        else:
            self.t1pkmn = trainer1.team['1']
            self.t2pkmn = trainer2.team['1']

        self.turnCount = 0 ##for turn counting moves and effects
        self.weather = None
        self.stones = None

        ##
        ## REMEBER TO MAKE IT SO THAT THE TRAINER'S NUMBER IS RESET AFTER EVERY BATTLE!!!!!!!!!!!!!

    def processTurn(self):
        t1move = self.t1pkmn.chosenMove
        t2move = self.t2pkmn.chosenMove
        #t3move = self.t3pkmn.chosenMove
        #t4move = self.t4pkmn.chosenMove

        order = self.turnOrder()

        count = 0
        for pokemon in order:
            if 'SWITCH_POKEMON' in pokemon.chosenMove: ## Stored in chosen move as ['SWITCH_POKEMON',<number between 2-6 of the one to be swapped with>]
                self.switchPokemon(pokemon,pokemon.chosenMove[1]) ##WRITE THIS FUNCTION!!!!!!!!!!!!!!!!!!!!!!!!!
        for pokemon in order:
            if 'SWITCH_POKEMON' in pokemon.chosenMove:
                pass
            else:
                
            

    def turnOrder(self):
        if self.t1pkmn.stats[5] > self.t2pkmn.stats[5]:
            return [self.t1pkmn,self.t2pkmn]
        elif self.t2pkmn.stats[5] == self.t1pkmn.stats[5]:
            if r.randint(0,2) == 1:
                return [self.t1pkmn,self.t2pkmn]
            else:
                return [self.t2pkmn,self.t1pkmn]
        else:
            return [self.t2pkmn,self.t1pkmn]

    def switchPokemon(self,pokemon,operatorNum,target):
        pokemon.trainer.team['1'], pokemon.trainer.team[target] = pokemon.trainer.team[target], pokemon.trainer.team['1']
        print('Trainer has switched their pokemon!')
        ## playSwitchAnimation() [to be coded]
        if pokemon.trainer.number = '1':
            self.t1pkmn = trainer1.team['1']
            if self.t2pkmn.ability.type == 'enemy switch': ## need to check to see if the enemy's ability activates on switch in
                self.t2pkmn.ability.activate()
        else:
            self.t2pkmn = trainer2.team['1']
            if self.t1pkmn.ability.type == 'enemy switch':
                self.t2pkmn.ability.activate()

        if pokemon.ability.type == 'enter': ## ex. Intimidate. Abilities that activate on entering the battlefield
            pokemon.ability.activate()

        if self.stones: ## for checking to see if spikes/rocks/toxicspikes are in play
            if 'Spikes' in self.stones:
                self.spikes(pokemon)
            elif 'Rocks' in self.stones:
                self.rocks(pokemon)
            elif 'ToxicSpike' in self.stones:
                self.toxicSpikes(pokemon)
    

    ## WEATHER AND STONES FUNCTIONS BELOW

    #def None(self):
     #   return

    def spikes(self,pokemon):
        if pokemon.type1 == 'Flying' or pokemon.type2 == 'Flying':
            return
        else:
            print(pokemon.nickname + ' was hurt by the spikes!')
            pokemon.takeDamage(int(pokemon.stats[0]/8),True)

    def rocks(self,pokemon):
        if pokemon.type1 == 'Flying' or pokemon.type2 == 'Flying':
            print(pokemon.nickname + ' was hurt by stealth rock!')
            pokemon.takeDamage(int(pokemon.stats[0]/4),True)
        else:
            print(pokemon.nickname + ' was hurt by stealth rock!')
            pokemon.takeDamage(int(pokemon.stats[0]/8),True)
            
    def rainyWeather(self):
        ## To be added
        print('The rain continues to fall.')

    def sandstormWeather(self):
        print('The sandstorm rages on.')

    def sunnyWeather(self):
        print('The heat is blazing.')

    def snowyWeather(self):
        print('The hail continues to fall.')

