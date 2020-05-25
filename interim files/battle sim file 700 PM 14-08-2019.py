## TO DO LIST:
## 1: DECIDE HOW TMs AND CAPSULEs ARE CLASSED (i.e. make the classes for them, dimwit)
## 2: DECIDE HOW THEY ARE STORED WITHIN THE TRAINER CLASS
## 3: MAKE THE ARENA CLASS. ARE MOVE AND ABILITY FUNCTIONS STORED HERE?
## 4: FINISH WRITING THE processTurn() FUNCTION
##  4a: Finish writing the switchPokemon function
## 5: FINISH WRITING THE move CLASS
## 6: Make it so that Pokemon can use a move in turn!!!
## 7: END THE 'END OF TURN' FUNCTION
## 8: PLEASE REVIEW THE switchPokemon() FUNCTION AS I'M NOT CONFIDENT IT DOES WHAT I WANT IT TO DO
## 9: FINISH THE trigger CLASS FROM triggerQueue.py TO ENSURE THAT IT EVALUATES TRIGGERS CORRECTLY.

## 10: FINISH THE dealDamage, executeMove, etc. FUNCTIONS! Then maybe some gui stuff :)

## Code Design Philosophy (Principle of Networked Objects): There should be a path from every possible object to every other object only from within the objects themselves.
## This means that no 'if/else' checking or iteration to get the target we need. There should be a pointer within an object that points it to some number (maybe 0) of other objects which have pointers to the desired object.
## This is important!!!!!!!!!

import random as r
import math as m
from triggerQueue import *

## Stats stored as a tuple as they shouldn't be changed, alongside the abilities.
## (hp, atk, def, sp.atk, sp.def,speed)
pkmnInfo = {
    'Bulbasaur' : {'stats' : (45,49,49,65,65,45), 'type1' : 'Grass', 'type2' : 'Poison', 'ability' : ['Overgrow'], 'moves' : ['Growl','Tackle','Vine Whip','Leech Seed']}
    }

## Natures are stored with name alongside the tuple showing how it affects stat growth
natures = [
    ['Adamant',(1, 1.1, 1, 0.9, 1, 1)]
           ]

IDAssign = 0

class pokemon:
    def __init__(self,species,level,trainer):
        
        global pkmnInfo
        self.base = pkmnInfo[species]['stats']
        self.iv = self.ivGenerate() ## generates a random spread of ivs, ex. (31,2,8,28,19,12)
        self.ability = r.choice(pkmnInfo[species]['ability'])

        self.types = [pkmnInfo[species]['type1'], pkmnInfo[species]['type2']]

        global natures ## need to select a nature to affect stats
        self.nature = r.choice(natures)

        self.moveNames = r.sample(pkmnInfo[species]['moves'],k=4)
        self.moves = []
        global moveInfo
        for nameOfMove in self.moveNames:
            self.moves.append([move(nameOfMove,self), moveInfo[nameOfMove]['pp']])
        
        self.ev = [0,0,0,0,0,0] ## needs to be a list so that it can be changed
        self.level = level
        self.stats = (0,0,0,0,0,0)
        self.statCalculate()
        self.hp = self.stats[0]
        self.modifiers = [0,0,0,0,0,0] ## stored as a list, can be changed. There will be a dict added that corresponds the -6 <-> 6 with an actual modifier to the output damage/defense/etc.
                                       ## they are called stages as the mod changes are called 'stat stages'
        self.accuracy = 0
        self.evasion = 0

        self.status = None
        self.statusCount = 0 ##counts time
        self.fainted = False

        self.shiny = False
        self.nickname = species
        self.species = species

        global IDAssign
        self.pokemonID = int(IDAssign) ## pokemonID is used for trigger checking; i.e. to see if the trigger is
                                       ## still active at end of turn
        IDAssign += 1 

        self.chosenMove = None
        self.trainer = trainer

        self.protectCount = 0
        self.protect = False

        trainer.getNewPokemon(self)
        

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

    def modifierReset(self):
        self.modifiers = [0,0,0,0,0,0]
        self.accuracy = 0
        self.evasion = 0

moveInfo = {
    'Growl' : {'type' : 'Normal', 'category' : 'Status', 'description' : "A cute growl makes the attacker less aggressive.", 'power' : None, 'pp' : 40, 'accuracy' : 95, 'function' : 'self.Growl(self.pokemon.trainer.number)'},
    'Leech Seed' : {'type' : 'Grass', 'category' : 'Status', 'description' : "Plants seeds to steal health.", 'power' : None, 'pp' : 10, 'accuracy' : 95,  'function' : 'self.LeechSeed(self.pokemon.trainer.number)'},
    'Tackle' : {'type' : 'Normal', 'category' : 'Physical', 'description' : "The user rams its body into its opponent.", 'power' : '40', 'pp' : 35, 'accuracy' : 95,  'function' : 'self.Tackle(self.pokemon.trainer.number)'},
    'Vine Whip' : {'type' : 'Grass', 'category' : 'Physical', 'description' : "Whips the foe with slender vines.", 'power' : '45', 'pp' : 25, 'accuracy' : 95,  'function' : 'self.VineWhip(self.pokemon.trainer.number)'}
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
        self.accuracy = moveInfo[name]['accuracy']

    def activate(self):
        exec(self.function)

abilityInfo = {
    'Intimidate' : {'category' : 'enter', 'description' : "Lowers opponent's attack by one stage.", 'function' : 'self.Intimidate(self.pokemon.trainer.number)'},
    'Overgrow' : {'category' : 'damaging', 'description' : "Grass moves boosted when weak.", 'function' : 'self.Overgrow(self.pokemon.trainer.number)'},
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
        if self.teamCount == 6:
            if tempFlag:
                self.box[str(self.boxCount)] = pkmn
                self.boxCount += 1
            else:
                self.tempTeam[str(self.tempTeamCount)] = pkmn
                self.tempTeamCount += 1
        else:
            self.teamCount += 1
            self.team[str(self.teamCount)] = pkmn

    def getNewTM(self,tm): ##FIX THIS, UNFINISHED
        self.tms[str(self.tmFP)] = tm
        self.tmFP += 1

    def receiveNumber(self,num):
        self.number = num


#---------------------------------------------------------------------------------------------------------------------------------------
class Arena:
    def __init__(self,trainer1,trainer2,tempFlag = True):
        self.trainer1 = trainer1
        trainer1.receiveNumber('1')
        
        self.trainer2 = trainer2
        trainer2.receiveNumber('2')

        self.trainerCount = 2
        
        if tempFlag:
            self.t1pkmn = trainer1.tempTeam['1']
            self.t2pkmn = trainer2.tempTeam['1']
        else:
            self.t1pkmn = trainer1.team['1']
            self.t2pkmn = trainer2.team['1']

        self.otherPokemon = {
            '1' : self.t2pkmn,
            '2' : self.t1pkmn
            }

        self.turnCount = 0 ##for turn counting moves and effects
        self.weather = None
        self.stones = None

        self.endTurnQueue = triggerQueue.trigger(20,self)

        global statStages
        global accStages
        global evasStages
        self.stages = statStages
        self.accStages = accStages
        self.evasStages = evasStages

        ##
        ## REMEBER TO MAKE IT SO THAT THE TRAINER'S NUMBER IS RESET AFTER EVERY BATTLE!!!!!!!!!!!!!!!!
        ##

#---------------------------------------------------------------------------------------------------------------------------------------
## TURN PROCESSING BEGINS HERE

    def startBattle(self):
        print('Trainer 1 has sent out ' + self.t1pkmn.nickname + '.')
        print('Trainer 2 has sent out ' + self.t2pkmn.nickname + '.')
        self.mainloop()

    def mainLoop(self):
        while True:
            print('What move to use? Or switch?')
            ## acceptInput()
            ## when both players have entered an input (need GUI for this):
            self.processTurn()
            self.endTurn()
            if self.battleOver:
                break
        self.endBattle() ## NEEDS TO BE CODED

    def endBattle(self):
        return

    def endTurn(self):
        self.endTurnQueue.evalTriggers()
        self.checkFainted()

    def processTurn(self):

        ## Shows how the turn will be handled
        ## Turn order (by speed, not priority) is returned by self.turnOrder()
        ## First, check for switches
        ## Then, check **IN ORDER OF PRIORITY** for moves
        
        
        t1move = self.t1pkmn.chosenMove
        t2move = self.t2pkmn.chosenMove
        #t3move = self.t3pkmn.chosenMove
        #t4move = self.t4pkmn.chosenMove

        self.order = self.turnOrder()

        count = 0
        numProcessed = 0
        for pokemon in order:
            if 'SWITCH_POKEMON' in pokemon.chosenMove: ## Stored in chosen move as ['SWITCH_POKEMON',<number between 2-6 of the one to be swapped with>]
                self.switchPokemon(pokemon,pokemon.chosenMove[1]) ##WRITE THIS FUNCTION!!!!!!!!!!!!!!!!!!!!!!!!! (done?)
                numProcessed += 1
        if numProcessed >= 2:
            return
        for x in range(0,13):
            priorityCheck = 5 - x ##priorities range from -7 to 5
            for pokemon in order:
                if 'SWITCH_POKEMON' in pokemon.chosenMove:
                    pass
                else: ##thus it's a move that's being used; stored as [num,num] where first num is move number (0-3) and second is priority
                    if pokemon.chosenMove[1] == priorityCheck: ##i.e. if it has priority
                        self.executeMove(pokemon)
                        #pokemon.moves[pokemon.chosenMove[0]][0].activate() ## moves are [[<move object>,'pp'],[<move object>, 'pp']]
                        ## pokemon.moves[pokemon.chosenMove[0]][0] is the move object of the move used. Remember; pokemon.moves is the moves list, and as its stored as [[<move object>,'pp'],[<move object>, 'pp']], index 0 of
                        ## index chosenMove[0] is a move object. so we are basically summoning that!
                        numProcessed += 1
                if numProcessed >= 2:
                    return

    def executeMove(self,pokemon):
        ## FIRST SECTION: CHECK IF MOVE HITS
        ## This will be done by calculating a value that a randomly calculated uniform float (0,100) must be greater than to cause a miss. That is...
        ## If my calculated accuracy (with mods, etc) is 75, then you'd need to be greater than 75 to cause a miss. I.e. 87 would miss, 74 wouldn't, 75 wouldn't, 99.3817264 would miss, etc.

        if random.uniform(0,100) <= pokemon.moves[pokemon.chosenMove[0]][0].accuracy * self.accStages[str(pokemon.accuracy)] * self.evasStages[str(self.otherPokemon[pokemon.trainer.num].evasion)]:
            ## first, the .moves thing is the acc of the move. then, self.accStages thing is the accuracy of the user. then, self.evasStages thing is the evasion of the other pokemon
            print(pokemon.nickname + ' used ' + pokemon.moves[pokemon.chosenMove[0]][0].name + '.')
            if pokemon.moves[pokemon.chosenMove[0]][0].category == 'Physical' or pokemon.moves[pokemon.chosenMove[0]][0].category == 'Special':
                self.dealDamage(pokemon,self.otherPokemon[pokemon.trainer.num],pokemon.moves[pokemon.chosenMove[0]][0])
                pokemon.moves[pokemon.chosenMove[0]][0].activate()

    def dealDamage(self,user,target,move):
        typeModifier = self.typeEffectiveness(user,target,move)
        stagesModifier = self.stagesModifiers(user,target)

    def typeEffectiveness(self,user,target,move):
        global weakness
        global resistance
        global immune
        typeModifier = 1
        for targetType in target.types:
            if move.type in weakness[targetType]:
                typeModifier = typeModifier * 2
            elif move.type in resistance[targetType]:
                typeModifier = typeModifier * 0.5
            else:
                return 0
        if move.type in user.types:
            typeModifier = typeModifier * 1.5
        return typeModifier

    def stagesModifier(self,user,target,move): ##TO BE FINISHED
        pass
        
    def turnOrder(self): ## returns turn order based on **SPEED**
        if self.t1pkmn.stats[5] > self.t2pkmn.stats[5]:
            return [self.t1pkmn,self.t2pkmn]
        elif self.t2pkmn.stats[5] == self.t1pkmn.stats[5]:
            if r.randint(0,2) == 1:
                return [self.t1pkmn,self.t2pkmn]
            else:
                return [self.t2pkmn,self.t1pkmn]
        else:
            return [self.t2pkmn,self.t1pkmn]

#---------------------------------------------------------------------------------------------------------------------------------------
## SWITCH AND FAINTED PROCESSING BEGINS HERE

    def switchPokemon(self,pokemon,operatorNum,target): ## swaps a trainer's pokemon. target is the target num of the swap
        pokemon.modifierReset()
        pokemon.trainer.team['1'], pokemon.trainer.team[target] = pokemon.trainer.team[target], pokemon.trainer.team['1'] ## swaps the trainer's first and target pokemon in their dict
        pokemon = pokemon.trainer.team['1']
        print('Trainer has switched their pokemon!')
        ## playSwitchAnimation() [to be coded]
        if pokemon.trainer.number == '1':
            self.t1pkmn = trainer1.team['1']
            #if self.t2pkmn.ability.type.lower() == 'enemy switch': ## need to check to see if the enemy's ability activates on switch in
            #    self.t2pkmn.ability.activate()
            if self.t1pkmn.ability.type.lower() == 'end of turn':
                self.trigger.addTrigger('self.t1pkmn.pokemonID==' + str(self.t1pkmn.pokemonID),self.t1pkmn.ability.function)
        else:
            self.t2pkmn = trainer2.team['1']
            #if self.t1pkmn.ability.type.lower() == 'enemy switch':
            #    self.t1pkmn.ability.activate()
            if self.t2pkmn.ability.type.lower() == 'end of turn':
                self.trigger.addTrigger('self.t2pkmn.pokemonID==' + str(self.t2pkmn.pokemonID),self.t2pkmn.ability.function)

        if pokemon.ability.category == 'enter': ## ex. Intimidate. Abilities that activate on entering the battlefield
            pokemon.ability.activate()

        if self.stones: ## for checking to see if spikes/rocks/toxicspikes are in play
            if 'Spikes' in self.stones:
                self.spikes(pokemon)
            elif 'Rocks' in self.stones:
                self.rocks(pokemon)
            elif 'ToxicSpike' in self.stones:
                self.toxicSpikes(pokemon)
                
        self.checkFainted()

    def checkFainted(self):
        for pokemon in self.order:
            if pokemon.hp <= 0:
                pokemon.fainted = True
                self.faintedSwitch(pokemon)

    def faintedSwitch(self,pokemon):
        if pokemon.ability.category == 'faint':
            pokemon.ability.activate()
        print(pokemon.nickname + ' has fainted!')
        ## TO BE ADDED: ACCEPT INPUT FROM PLAYER ON NEXT PKMN TO SWAP TO.
        target = input('sonny dog, gimme a number: ')
        pokemon.trainer.team['1'], pokemon.trainer.team[target] = pokemon.trainer.team[target], pokemon.trainer.team['1'] 
        pokemon = pokemon.trainer.team['1']
        print('Trainer has switched their pokemon!')
        if pokemon.trainer.number == '1':
            self.t1pkmn = trainer1.team['1']
            if self.t1pkmn.ability.category.lower() == 'end of turn':
                self.trigger.addTrigger('self.t1pkmn.pokemonID==' + str(self.t1pkmn.pokemonID),self.t1pkmn.ability.function)
        else:
            self.t2pkmn = trainer2.team['1']
            if self.t2pkmn.ability.category.lower() == 'end of turn':
                self.trigger.addTrigger('self.t2pkmn.pokemonID==' + str(self.t2pkmn.pokemonID),self.t2pkmn.ability.function)

        if pokemon.ability.category == 'enter': ## ex. Intimidate. Abilities that activate on entering the battlefield
            pokemon.ability.activate()

        if self.stones: ## for checking to see if spikes/rocks/toxicspikes are in play
            if 'Spikes' in self.stones:
                self.spikes(pokemon)
            elif 'Rocks' in self.stones:
                self.rocks(pokemon)
            elif 'ToxicSpike' in self.stones:
                self.toxicSpikes(pokemon)

        self.checkFainted()


#---------------------------------------------------------------------------------------------------------------------------------------
## WEATHER AND STONES FUNCTIONS BELOW

    #def None(self):
     #   return

    def spikes(self,pokemon):
        if 'Flying' in pokemon.types:
            return
        else:
            print(pokemon.nickname + ' was hurt by the spikes!')
            pokemon.takeDamage(int(pokemon.stats[0]/8),True)

    def rocks(self,pokemon):
        print(pokemon.nickname + ' was hurt by stealth rock!')
        if 'Flying' in pokemon.types:
            pokemon.takeDamage(int(pokemon.stats[0]/4),True)
        else:
            pokemon.takeDamage(int(pokemon.stats[0]/8),True)

    def toxicSpikes(self,pokemon):
        if 'Flying' in pokemon.types:
            return
        elif 'Poison' in pokemon.types:
            print(pokemon.nickname + ' absorbed the toxic spikes!')
            self.stones = None
        else:
            print(pokemon.nickname + ' was badly poisoned!')
            pokemon.status = 'Badly Poisoned'
            
    def rainyWeather(self):
        ## To be added
        print('The rain continues to fall.')

    def sandstormWeather(self):
        print('The sandstorm rages on.')

    def sunnyWeather(self):
        print('The heat is blazing.')

    def snowyWeather(self):
        print('The hail continues to fall.')

#---------------------------------------------------------------------------------------------------------------------------------------

statStages = {
    '-6' : 2/8,
    '-5' : 2/7,
    '-4' : 2/6,
    '-3' : 2/5,
    '-2' : 2/4,
    '-1' : 2/3,
    '0' : 2/2,
    '1' : 3/2,
    '2' : 4/2,
    '3' : 5/2,
    '4' : 6/2,
    '5' : 7/2,
    '6' : 8/2
    }

accStages = {
    '-6' : 3/9,
    '-5' : 3/8,
    '-4' : 3/7,
    '-3' : 3/6,
    '-2' : 3/5,
    '-1' : 3/4,
    '0' : 3/3,
    '1' : 4/3,
    '2' : 5/3,
    '3' : 6/3,
    '4' : 7/3,
    '5' : 8/3,
    '6' : 9/3
    }

evasStages = {
    '6' : 3/9,
    '5' : 3/8,
    '4' : 3/7,
    '3' : 3/6,
    '2' : 3/5,
    '1' : 3/4,
    '0' : 3/3,
    '-1' : 4/3,
    '-2' : 5/3,
    '-3' : 6/3,
    '-4' : 7/3,
    '-5' : 8/3,
    '-6' : 9/3
    }

weakness = {
    'Bug' : ['Fire','Flying','Rock'],
    'Dark' : ['Fighting','Bug','Fairy'],
    'Dragon' : ['Dragon','Fairy','Ice'],
    'Electric' : ['Ground'],
    'Fairy' : ['Steel','Poison'],
    'Fighting' : ['Psychic','Flying','Fairy'],
    'Fire' : ['Water','Ground','Rock'],
    'Flying' : ['Electric','Ice','Rock'],
    'Ghost' : ['Ghost','Dark'],
    'Grass' : ['Fire','Ice','Poison','Flying','Bug'],
    'Ground' : ['Water','Grass','Ice'],
    'Ice' : ['Fire','Fighting','Rock','Steel'],
    'Normal' : ['Fighting'],
    'Poison' : ['Ground','Psychic'],
    'Psychic' : ['Bug','Dark','Ghost'],
    'Rock' : ['Water','Grass','Fighting','Ground','Steel'],
    'Steel' : ['Fire','Ground','Fighting'],
    'Water' : ['Electric','Grass']
    }

resistance = {
    'Bug' : ['Grass','Fighting','Ground'],
    'Dark' : ['Ghost','Dark'],
    'Dragon' : ['Fire','Water','Grass','Electric'],
    'Electric' : ['Electric','Flying'],
    'Fairy' : ['Fighting','Bug','Dark'],
    'Fighting' : ['Bug','Rock','Dark],
    'Fire' : ['Fire','Grass','Ice','Bug','Steel','Fairy'],
    'Flying' : ['Grass','Fighting','Bug'],
    'Ghost' : ['Poison','Bug'],
    'Grass' : ['Water','Electric','Grass','Ground'],
    'Ground' : ['Poison','Rock'],
    'Ice' : ['Ice'],
    'Normal' : [],
    'Poison' : ['Grass','Fighting','Poison','Bug','Fairy'],
    'Psychic' : ['Fighting','Psychic'],
    'Rock' : ['Normal','Fire','Poison','Flying'],
    'Steel' : ['Normal','Grass','Ice','Flying','Psychic','Bug','Rock','Dragon','Steel','Fairy'],
    'Water' : ['Fire','Water','Ice','Steel']
    }

immune = {
    'Bug' : [],
    'Dark' : ['Psychic'],
    'Dragon' : [],
    'Electric' : [],
    'Fairy' : ['Dragon'],
    'Fighting' : [],
    'Fire' : [],
    'Flying' : ['Ground'],
    'Ghost' : ['Normal','Fighting'],
    'Grass' : [],
    'Ground' : ['Electric'],
    'Ice' : [],
    'Normal' : ['Ghost'],
    'Poison' : [],
    'Psychic' : [],
    'Rock' : [],
    'Steel' : ['Poison'],
    'Water' : []
    }

templateForTypes = {
    'Bug' : [],
    'Dark' : [],
    'Dragon' : [],
    'Electric' : [],
    'Fairy' : [],
    'Fighting' : [],
    'Fire' : [],
    'Flying' : [],
    'Ghost' : [],
    'Grass' : [],
    'Ground' : [],
    'Ice' : [],
    'Normal' : [],
    'Poison' : [],
    'Psychic' : [],
    'Rock' : [],
    'Steel' : [],
    'Water' : []
    }
