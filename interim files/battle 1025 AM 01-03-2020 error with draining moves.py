##CONSIDER ADDING A SLIDING GREY RECTANGLE TO THE TABLET FOR UPDATING POKEMON.
##CAN MAKE IT SO THAT IT DOESN'T REGISTER GO AGAINT UNTIL IT HAS COMPLETELY FINISHED

import random as r
from pkmnData import *
import time


IDAssign = 0

def genFunc(f, *args):
    return lambda *args2: f(*args)

class pokemon:
    def __init__(self,species,level,trainer=False):
        
        global pkmnInfo
        self.base = pkmnInfo[species]['stats']  
        self.iv = self.ivGenerate() ## generates a random spread of ivs, ex. (31,2,8,28,19,12)

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
        self.statusCondition = None
        self.statusCount = 0 ##counts time
        self.fainted = False
        self.shiny = False
        self.name = species
        self.species = species
        global IDAssign
        self.pokemonID = int(IDAssign) ## pokemonID is used for trigger checking; i.e. to see if the trigger is
                                       ## still active at end of turn
        IDAssign += 1
        
        self.chosenMove = None
        if trainer != False:
            self.trainer = trainer
            self.trainer.addPokemon(self)

        self.protectCount = 0

        ##resettables
        self.sleepCount = 0
        self.flinched = False
        self.lastUsedProtect = False
        self.protectCount = 0
        self.switchedInThisTurn = True

        ##reset on switch out
        self.magnetRise = False
        self.taunt = False
        self.tauntCount = 0

        ##other move things
        self.twoTurnMove = None
        
    def getTrainer(self,trainer):
        self.trainer = trainer
        self.trainer.addPokemon(self)

    def resettables(self,dontChangeSleep=False):
        self.flinched = False
        if not self.lastUsedProtect:
            self.protectCount = 0
        self.lastUsedProtect = False
        self.lastDamage = 0
        self.lastDamageDealt = 0
        self.switchedInThisTurn = False
        if not dontChangeSleep:
            if self.sleepCount > 0:
                self.sleepCount -= 1

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

    def takeDamage(self,damage,CombatDamage=True):
        self.hp -= damage
        if CombatDamage:
            self.lastDamage = damage
        if self.hp <= 0:
            self.hp = 0
            self.fainted = True

    def modifierReset(self):
        self.modifiers = [0,0,0,0,0,0]
        self.accuracy = 0
        self.evasion = 0
        self.magnetRise = False
        self.twoTurnMove = None
        self.taunt = False
        self.resettables(True)

    def changeModifier(self,modifier,amount):
        modDict = {'HP':0,'ATTACK':1,'DEFENSE':2,'SPECIAL ATTACK':3,'SPECIAL DEFENSE':4,'SPEED':5}
        if modifier.upper() == 'ACCURACY':
            if self.accuracy==6 and amount > 0:
                return 'higher'
            elif self.accuracy==-6 and amount < 0:
                return 'lower'
            else:
                self.accuracy += amount
                return 'ALLOK'
        elif modifier.upper() == 'EVASION':
            if self.evasion==6 and amount > 0:
                return 'higher'
            elif self.evasion == -6 and amount < 0:
                return 'lower'
            else:
                self.evasion += amount
                return 'ALLOK'
        else:
            stat = self.modifiers[modDict[modifier.upper()]]
            if stat == 6 and amount > 0:
                return 'higher'
            elif stat == -6 and amount < 0:
                return 'lower'
            else:
                self.modifiers[modDict[modifier.upper()]] += amount
                return 'ALLOK'


class ability:
    def __init__(self,name,pokemon):
        global abilityInfo
        self.name = name
        self.category = abilityInfo[name]['category']
        self.description = abilityInfo[name]['description']
        self.function = abilityInfo[name]['function']
        self.pokemon = pokemon

    def activate(self):
        exec(self.function)

class trainer:
    def __init__(self,name,trainerClass,spriteName=False):
        self.name = name
        self.trainerClass = trainerClass
        self.sprite = spriteName
        self.team = {'0' : None, '1' : None, '2' : None, '3' : None, '4' : None, '5' : None}
        self.teamPointer = 0
        self.box = {}
        self.boxPointer = 0
        self.boxCount = 0
        self.active = None
    def addPokemon(self,pokemon):
        self.box[str(self.boxPointer)] = [pokemon,False]
        self.boxPointer += 1
    def addToTeam(self,pointer):
        if self.teamPointer == 6:
            return False
        self.team[str(self.teamPointer)] = self.box[str(pointer)][0]
        self.teamPointer += 1
        return True
    def removeFromTeam(self,pointer):
        if self.teamPointer == 0:
            return False
        self.teamPointer -= 1
        temp = self.team[str(teamPointer)]
        self.team[str(teamPointer)] = None
        return temp

class Arena:
    def __init__(self,trainer1,trainer2):
        self.removeList = []
        self.userTrainer = trainer1
        self.userTrainer.active = 0
        self.enemyTrainer = trainer2
        self.enemyTrainer.active = 0
        self.turnCount = 0
        self.faintedMidBattle = [False,False]
        self.newUserActive = [False,0]
        self.newEnemyActive = [False,0]
        self.endOfTurnQueue = serviceQueue()
        self.statusConditions = {'badly poisoned' : self.hurtByBadPoison}

        ##move effects
        ##  important note!!!
        ##      some of these dicts share their names with moves
        ##      ex. yawn
        ##      if these moves have an EOT effect, such as yawn does
        ##      then the EOT func is called moveEOT
        ##      ex. self.yawn -> dictionary, self.yawnEOT -> function
        self.badPoison = {}
        self.lightScreen = {self.userTrainer : 0, self.enemyTrainer : 0}
        self.reflect = {self.userTrainer : 0, self.enemyTrainer : 0}
        self.wish = {self.userTrainer : [0,0], self.enemyTrainer : [0,0]}
        self.yawn = {}

        self.criticalHit = False
        self.trickRoom = False
        self.trickRoomCount = 0
        
        ##first is user, second is enemy
        ## lol this is mostly just getters and setters in python of all langauges. this is what we, in the
        ## memes industry, call a "big brain maneuver"

        self.emergencyUserSwitch = ''
        self.emergencyEnemySwitch = ''

    def setEmergencyUserSwitch(self,inp):
        self.emergencyUserSwitch = inp

    def setApp(self,app):
        self.app = app

    def setUserActive(self,index):
        self.userTrainer.active = index

    def setEnemyActive(self,index):
        self.enemyTrainer.active = index
        
    def findActiveName(self,trainer): ##getters and setters in a language without private/public vars ooohhhhh yeeeessss real programmer hours
        return trainer.team[str(trainer.active)].name

    def findUserIndexName(self,index):
        return self.userTrainer.team[str(index)].name

    def findUserActive(self):
        return self.userTrainer.team[str(self.userTrainer.active)].name

    def findUserPokemon(self):
        return self.userTrainer.team[str(self.userTrainer.active)]

    def findEnemyPokemon(self):
        return self.enemyTrainer.team[str(self.enemyTrainer.active)]

    def returnUsefulMoveInfo(self,trainer): ##returns list of [moveName,moveType] for the user's active
        res = []
        for move in trainer.team[str(trainer.active)].moves:
            res.append([move[0].name,move[0].type])
        return res

    def getEnemyHP(self):
        return (self.enemyTrainer.team[str(self.enemyTrainer.active)].hp,self.enemyTrainer.team[str(self.enemyTrainer.active)].stats[0])

    def getEnemyLevel(self):
        return self.enemyTrainer.team[str(self.enemyTrainer.active)].level

    def getUserLevel(self):
        return self.userTrainer.team[str(self.userTrainer.active)].level

    def getUserHP(self):
        return (self.userTrainer.team[str(self.userTrainer.active)].hp,self.userTrainer.team[str(self.userTrainer.active)].stats[0])

    def getUserSpecies(self,index):
        try:
            return self.userTrainer.team[index].species
        except:
            return False

    def getUserPokemonID(self):
        return self.userTrainer.team[str(self.userTrainer.active)].pokemonID

    def getEnemyPokemonID(self):
        return self.enemyTrainer.team[str(self.enemyTrainer.active)].pokemonID

    def getEnemyNameAndClass(self):
        return self.enemyTrainer.trainerClass + ' ' + self.enemyTrainer.name

    def getEnemySpecies(self,index):
        return self.enemyTrainer.team[index].name

    def doesMoveHit(self,move,user,targ):
        x  = move.accuracy
        if move.name not in ['Magical Leaf']:
            x = x * accStages[str(user.accuracy)]
        if move.name not in ['Chip Away','Magical Leaf']:
            x = x * evasStages[str(targ.evasion)]
        if r.uniform(0,100) <= x:
            return True
        else:
            return False

    def speedOrderModifiers(self,pokemon):
        Modifier = 1
        if pokemon.statusCondition == 'paralyzed':
            Modifier = Modifier/2
        return Modifier * stages[str(pokemon.modifiers[5])]

    def processTurn(self,userInput,enemyInput):
        ##input types:
        ## ATTACK: e.g. ('attack',<move object>,id)
        ## SWITCH: e.g. ('switch',TEAM INDEX,id)
        ## (where ID refers to whether it is enemyTrainer or userTrainer- e.g. id='user' -> user trainer)
        ##
        ####################################
        ##      VERY IMPORTANT FUNC       ##
        ## This function will create a    ##
        ## queue of functions that will   ##
        ## then be activated sequentially.##
        ## The entirety of the turn is    ##
        ## decided upon before it is      ##
        ## displayed to the user. Any text##
        ## that will be displayed is queu-##
        ## ed, any anims, any behind-the- ##
        ## scenes stuff such as damage,   ##
        ## etc. is all decided upon before##
        ## hand.                          ##
        ##                                ##
        ####################################
        ##
        tempActiveUserTrainer = self.userTrainer.active
        tempActiveEnemyTrainer = self.enemyTrainer.active
        if self.enemyTrainer.team[str(self.enemyTrainer.active)].twoTurnMove != None:
            enemyInput = self.enemyTrainer.team[str(self.enemyTrainer.active)].twoTurnMove
        if userInput[0] == 'attack' and enemyInput[0] == 'attack': ## need to decide which goes first
            ## first check priority if both are attacks- then if one's priority is higher we do this
            if userInput[1].priority > enemyInput[1].priority: 
                order = (userInput,enemyInput)
            elif userInput[1].priority < enemyInput[1].priority:
                order =(enemyInput,userInput)
            else: ## if here, priority is same (as will be the case for most moves) so must use speed to tie break
                userSpeed = self.userTrainer.team[str(self.userTrainer.active)].stats[5] * self.speedOrderModifiers(self.userTrainer.team[str(self.userTrainer.active)])
                enemySpeed = self.enemyTrainer.team[str(self.enemyTrainer.active)].stats[5] * self.speedOrderModifiers(self.enemyTrainer.team[str(self.enemyTrainer.active)])
                if userSpeed > enemySpeed:
                    if not self.trickRoom: ##trick room is a move that makes slower pokemon move first
                        order = (userInput,enemyInput)
                    else:
                        order = (enemyInput,userInput)
                elif userSpeed < enemySpeed:
                    if not self.trickRoom:
                        order = (enemyInput,userInput)
                    else:
                        order = (userInput,enemyInput)
                else: ## speeds are tied so we choose randomly
                    x = [enemyInput,userInput]
                    r.shuffle(x)
                    order = tuple(x)
        elif userInput[0] != enemyInput[0]: ## i.e. if one is switching and one isn't
            if userInput[0] == 'switch': ## is user the one switching?
                order = (userInput,enemyInput)
            else: ## so enemy is switching
                order = (enemyInput,userInput)
        else: ## so both are switching, speed decides who moves first (code is copied from before)
            if self.userTrainer.team[str(self.userTrainer.active)].stats[5] > self.enemyTrainer.team[str(self.enemyTrainer.active)].stats[5]:
                order = (userInput,enemyInput)
            elif self.userTrainer.team[str(self.userTrainer.active)].stats[5] < self.enemyTrainer.team[str(self.enemyTrainer.active)].stats[5]:
                order = (enemyInput,userInput)
            else:
                x = [enemyInput,userInput]
                r.shuffle(x)
                order = tuple(x)
        q = serviceQueue()
        for x in order:
            badFlag = 0
            ##this function is basically recreating how an actual battle is seen by the user behind the scenes
            ##this allows me to do processing in the order in which I would be receiving the commands as if they
            ##were received in real time (as the game is trying to mimic)
            if x[2] == 'user' and self.faintedMidBattle[0]:
                pass
            elif x[2] == 'enemy' and self.faintedMidBattle[1]:
                pass
            elif x[0] == 'switch':
                if x[2] == 'user': ## I could compress k=genfunc(...); q.add(k) into one line but they are kept separate for clarity
                    if self.userTrainer.team[str(x[1])].statusCondition != None and self.userTrainer.team[str(x[1])].statusCondition != 'paralyzed':
                        k = genFunc(self.endOfTurnQueue.add,genFunc(self.statusConditions[self.userTrainer.team[str(x[1])].statusCondition],self.userTrainer.team[str(x[1])])) ##comments on x[2] == 'enemy'
                        q.add(k) 

                    k = genFunc(self.app.runText,r.choice(userSwitchMessages) % self.findActiveName(self.userTrainer))
                    q.add(k)
                    q.add(self.userTrainer.team[str(self.userTrainer.active)].modifierReset)
                    q.add(self.app.switchUser)
                    k = genFunc(self.setUserActive,x[1])
                    q.add(k)
                    k = genFunc(self.app.runText,r.choice(userSendInMessages) % self.findUserIndexName(x[1]))
                    q.add(k)
                    q.add(self.app.throwStartPokeball)
                    tempActiveUserTrainer = str(x[1])
                    STATUSCONDITION = self.userTrainer.team[str(x[1])].statusCondition
                    if STATUSCONDITION != None:
                        q.add(self.app.setUserStatus)
                        dict_STATUS = {'badly poisoned':self.hurtByBadPoison,'poisoned':self.hurtByPoison,'burned':self.hurtByBurn}
                        if STATUSCONDITION in ['badly poisoned','poisoned','burned']:
                            self.endOfTurnQueue.add(genFunc(dict_STATUS[STATUSCONDITION],self.userTrainer.team[x[1]]))
                elif x[2] == 'enemy':
                    if self.enemyTrainer.team[str(x[1])].statusCondition != None and self.enemyTrainer.team[str(x[1])].statusCondition != 'paralyzed':
                        k = genFunc(self.endOfTurnQueue.add,genFunc(self.statusConditions[self.enemyTrainer.team[str(x[1])].statusCondition],self.enemyTrainer.team[str(x[1])])) ##double layered genfunc; so basically we say we want to add a thing to
                                                                                                        ##the EOT queue, and that func has to be genfunc'd
                        q.add(k) 
                    k = genFunc(self.app.runText,self.getEnemyNameAndClass() +' calls back '+ self.getEnemySpecies(str(self.enemyTrainer.active))+'!')
                    q.add(k)
                    q.add(self.app.switchEnemy)
                    q.add(self.enemyTrainer.team[str(self.enemyTrainer.active)].modifierReset)
                    k = genFunc(self.setEnemyActive,x[1])
                    q.add(k)
                    k = genFunc(self.app.runText,self.getEnemyNameAndClass() + ' sends in '+ self.getEnemySpecies(str(x[1]))+'!')
                    q.add(k)
                    q.add(self.app.enemyPokemonSendOut)
                    tempActiveEnemyTrainer = str(x[1])
                    STATUSCONDITION = self.enemyTrainer.team[str(x[1])].statusCondition
                    if STATUSCONDITION != None:
                        q.add(self.app.setEnemyStatus)
                        dict_STATUS = {'badly poisoned':self.hurtByBadPoison,'poisoned':self.hurtByPoison,'burned':self.hurtByBurn}
                        if STATUSCONDITION in ['badly poisoned','poisoned','burned']:
                            self.endOfTurnQueue.add(genFunc(dict_STATUS[STATUSCONDITION],self.enemyTrainer.team[x[1]]))
            elif x[0] == 'attack':
                if x[2] == 'user':
                    TARGNAME = 'enemy'
                    USERNAME = 'user'
                    user = self.userTrainer.team[str(tempActiveUserTrainer)] ##user here refers to the pokemon using the move
                    targ = self.enemyTrainer.team[str(tempActiveEnemyTrainer)]
                    UserFainted = self.faintedMidBattle[0]
                    f = "Foe's "
                    u = ''
                else:
                    TARGNAME = 'user'
                    USERNAME = 'enemy'
                    user = self.enemyTrainer.team[str(tempActiveEnemyTrainer)]
                    targ = self.userTrainer.team[str(tempActiveUserTrainer)]
                    UserFainted = self.faintedMidBattle[1]
                    f = ""
                    u = "Foe's "
                ##
                    ##this is for a successful attack
                    ##should check to see the damage
                    ##if it is >= to pokemon's hp, set damage to pokemon's HP and trigger fainting
                    ##add switching to end of turn if faintws
                    ##also make sure it hits the pokemon that switches in if user switches as their action
                    ##for turn, not curr pokemon.
                if user.statusCondition == 'asleep':
                    if user.sleepCount == 0:
                        k = genFunc(self.app.runText, u + user.name + ' woke up!')
                        user.statusCondition = None
                        q.add(k)
                        q.add(self.app.setUserStatus) ##i'm putting both because it will simply update both to the newest
                        q.add(self.app.setEnemyStatus) ##while I really only need to update one of the two depending on
                                                        ##which was asleep, it ultimately doesn't end up mattering
                    else:
                        k = genFunc(self.app.runText, u + user.name + ' is sleeping soundly.')
                        q.add(k)
                        badFlag = 1
                elif user.statusCondition == 'freeze':
                    if r.uniform(0,1) > 0.8:
                        k = genFunc(self.app.runText, u + user.name + ' is frozen solid!')
                        q.add(k)
                        badFlag = 1
                    else:
                        k = genFunc(self.app.runText, u + user.name + ' thawed out!')
                        q.add(k)
                elif user.statusCondition == 'paralyzed':
                    if r.choice([0,1,2,3]) == 1:
                        k = genFunc(self.app.runText, u + user.name + ' is paralyzed and cannot move!')
                        q.add(k)
                        badFlag = 1
                if user.flinched == True and badFlag != 1:
                    k = genFunc(self.app.runText,u + user.name + ' flinched!')
                    q.add(k)
                    badFlag = 1 ##they can't do their thing
                if not UserFainted and badFlag == 0:

                    print(x)
                    loop = 1
                    if x[1].specifier == 'multihit':
                        loop = r.randint(2,5)
                    elif x[1].specifier == 'twohit':
                        loop = 2
                    if x[1].name in ['Solar Beam'] and user.twoTurnMove == None:
                        k = genFunc(x[1].function,self,user,targ)
                        q.add(k)
                    else:
                        k = genFunc(self.app.runText,u + user.name + ' used ' + x[1].name + '!')
                        q.add(k)
                        loopDamage = 0
                        numberHit = 0
                        for hit in range(0,loop):
                            if x[1].name == 'Brick Break':
                                lrFlag = False
                                if self.lightScreen[targ.trainer] > 0:
                                    self.lightScreen[targ.trainer] = -1
                                    lrFlag = True
                                if self.reflect[targ.trainer] > 0:
                                    self.reflect[targ.trainer] = -1
                                    lrFlag = True
                                if lrFlag:
                                    q.add(genFunc(self.app.runText,'Brick Break broke the defending barriers!'))
                            if loop > 1:
                                q.add(genFunc(self.app.runText,' '))
                            print(loop)
                            print('hit hit')
                            if self.doesMoveHit(x[1],user,targ):
                                numberHit += 1
                                if targ.lastUsedProtect:
                                    k = genFunc(self.app.runText,f + targ.name + ' protected itself!')
                                    q.add(k)
                                    break
                                if x[1].name == 'Fake Out' and not user.switchedInThisTurn:
                                    k = genFunc(self.app.runText,'But it failed!')
                                    q.add(k)
                                    break
                                if x[1].category != 'Status':
                                    damage = self.findDamage(user,targ,x[1])
                                    if damage[1] == 0:
                                        k = genFunc(self.app.runText,'But it had no effect!')
                                        q.add(k)
                                        break
                                    else:
                                        user.lastDamageDealt = damage[0]
                                        print('user last damage: ' + str(user.lastDamageDealt))
                                        if x[1].name in ['Clear Smog','Dark Pulse','Fake Out','Fire Fang','Ice Fang','Rock Slide','Thunder Fang']:
                                            ##These moves have effects, such as flinching or stat drop, that mean that they need to be activated early.
                                            ##There is an early execute setting in the move functions (below) that controls this.
                                            x[1].function(self,user,targ,earlyExecute=True)
                                        E2U = {'user':'enemy','enemy':'user'}
                                        q.add(genFunc(self.app.useMove,x[1].type,E2U[x[2]]))
                                        if damage[0] >= targ.hp-loopDamage:
                                            if x[2]=='user':
                                                k = genFunc(self.app.HPUpdateEnemy,0)
                                                q.add(k)
                                            else:
                                                k = genFunc(self.app.HPUpdateUser,0)
                                                q.add(k)
                                            #k = genFunc(self.app.runText, j + targ.name + ' fainted!')
                                            #q.add(k)
                                            k = genFunc(targ.takeDamage,damage[0])
                                            q.add(k)
                                            if damage[1] == 1:
                                                k = genFunc(self.app.runText,'It was not very effective...')
                                                q.add(k)
                                            elif damage[1] == 2:
                                                k = genFunc(self.app.runText,'It was super effective!')
                                                q.add(k)
                                            if self.criticalHit:
                                                k = genFunc(self.app.runText,'It was a critical hit!')
                                                q.add(k)
                                                self.criticalHit = False
                                                
                                            k = genFunc(x[1].function,self,user,targ) ##this function executes the move's secondary effects
                                            q.add(k)
                                            
                                            if x[2] == 'user':
                                                k = genFunc(self.app.enemyPokemonFaint)
                                                q.add(k)
                                                q.add(targ.modifierReset)
                                                self.faintedMidBattle[1] = True
                                            else:
                                                k = genFunc(self.app.userPokemonFaint)
                                                q.add(k)
                                                q.add(targ.modifierReset)
                                                self.faintedMidBattle[0] = True
                                            break ##need to break out if fainted.
                                        else:
                                            if x[2] == 'user':
                                                k = genFunc(self.app.HPUpdateEnemy,targ.hp-damage[0]-loopDamage)
                                            else:
                                                k = genFunc(self.app.HPUpdateUser,targ.hp-damage[0]-loopDamage)
                                            q.add(k)
                                            k = genFunc(targ.takeDamage,damage[0])
                                            q.add(k)
                                            if damage[1] == 1:
                                                k = genFunc(self.app.runText,'It was not very effective...')
                                                q.add(k)
                                            elif damage[1] == 2:
                                                k = genFunc(self.app.runText,'It was super effective!')
                                                q.add(k)
                                            if x[1].type == 'Fire' and targ.statusCondition == 'freeze':
                                                targ.statusCondition = None
                                                k = genFunc(self.app.runText,f + pokemon.name + " thawed out because of the intense heat!")
                                                q.add(k)
                                                q.add(self.app.setEnemyStatus)
                                        k = genFunc(x[1].function,self,user,targ)
                                        q.add(k)
                                    loopDamage += damage[0]
                                elif x[1].category == 'Status':
                                    if user.taunt:
                                        q.add(genFunc(self.app.runText,u+user.name+" can't use " + x[1].name + " after the taunt!"))
                                        continue
                                    elif x[1].name in ['Spore','Clear Smog','Protect','Taunt']:
                                        x[1].function(self,user,targ,earlyExecute=True) ##some functions must be executed earlier so that their effects are noted
                                        q.add(genFunc(x[1].function,self,user,targ))
                                    else:
                                        if x[1].name in ['Toxic','Thunder Wave','Will-O-Wisp']:
                                            E2U = {'user':'enemy','enemy':'user'}
                                            q.add(genFunc(self.app.useMove,x[1].type,E2U[x[2]]))
                                        k = genFunc(x[1].function,self,user,targ)
                                        q.add(k)
                            else:
                                user.twoTurnMove = None
                                if loop == 1:
                                    k = genFunc(self.app.runText,'But it missed!')
                                    q.add(k)
                                else:
                                    k = genFunc(self.app.runText,'One shot missed!')
                                    q.add(k)
                        if loop >= 2 and not targ.lastUsedProtect:
                            q.add(genFunc(self.app.runText,'Hit ' + str(numberHit) + ' time(s)!'))
            q.add(self.userTrainer.team[str(self.userTrainer.active)].resettables)
            q.add(self.enemyTrainer.team[str(self.enemyTrainer.active)].resettables)
        print('two execute turns')
        print(q)
        self.executeTurn(q)
        self.faintedMidBattle = [False,False]
        self.newUserActive = [False,0]##this refers to the player
        self.newEnemyActive = [False,0]##this refers to the enemy


    def executeTurn(self,q,textWasRunning=False,EOT=False,midEOT=False): ##EOT -> don't call EOT during EOT, midEOT -> don't update GUI if its middle of EOT
        if self.app.taskFinished and not self.app.textRunning and not textWasRunning:
            if len(q.q) == 0:##used for two things. once when executing the main turn, and second when executing the
                             ##knockouts at EOT
                if not EOT:
                    print('going to eot')
                    self.endOfTurn()
                elif not midEOT:
                    if self.userTrainer.team[str(self.userTrainer.active)].twoTurnMove == None:
                        self.app.updateButtons()
                    else:
                        self.app.receiveUserInput(self.userTrainer.team[str(self.userTrainer.active)].twoTurnMove)
                return
            else:
                q.rem()() ##executes whatever q returns
        if textWasRunning:
            k = genFunc(self.executeTurn,q,self.app.textRunning,EOT,midEOT)
            self.app.master.after(200,k)
        else:
            k = genFunc(self.executeTurn,q,self.app.textRunning,EOT,midEOT)
            self.app.master.after(5,k)
            


################################################################################
            ##EOT FUNCS HERE

    def reflectEOT(self,trainer):
        if self.reflect[trainer] == -1:
            self.reflect[trainer] = 0
            return False
        self.lightScreen[trainer] -= 1
        self.reflect[trainer] -= 1
        if self.reflect == 0:
            if trainer == self.enemyTrainer:
                self.app.runText("Foe's reflect wore off!")
            else:
                self.app.runText("Reflect wore off!")
            return False
        else:
            return 0

    def hurtByBurn(self,targ):
        print('start burn')
        self.app.processesComplete = 0
        q = serviceQueue()
        numTasks = 2
        if targ.statusCondition == 'burned' and (targ.pokemonID == self.getUserPokemonID() or targ.pokemonID == self.getEnemyPokemonID()):
            if targ.pokemonID == self.userTrainer.team[str(self.userTrainer.active)].pokemonID:
                j = ''
            else:
                j = "Foe's "
            lostHP = int(targ.stats[0]/8+1)
            q.add(genFunc(self.app.runText,j+targ.name + ' was hurt by burn!'))
            if targ.pokemonID == self.userTrainer.team[str(self.userTrainer.active)].pokemonID:
                q.add(genFunc(self.app.HPUpdateUser,max(0,targ.hp-lostHP)))
            else:
                q.add(genFunc(self.app.HPUpdateEnemy,max(0,targ.hp-lostHP)))
            q.add(genFunc(targ.takeDamage,lostHP))
            self.executeTurn(q,False,True,True)
            if lostHP > targ.hp:
                return (numTasks,genFunc(self.EOTKO,targ))
            else:
                return numTasks
        else:
            return False

    def hurtByBadPoison(self,targ):
        print('start bad poison')
        self.app.processesComplete = 0
        q = serviceQueue()
        numTasks = 2
        if targ.statusCondition == 'badly poisoned' and (targ.pokemonID == self.getUserPokemonID() or targ.pokemonID == self.getEnemyPokemonID()):
            try:
                self.badPoison[str(targ)] += 15/16
            except:
                self.badPoison[str(targ)] = 16/16
            if targ.pokemonID == self.userTrainer.team[str(self.userTrainer.active)].pokemonID:
                j = ''
            else:
                j = "Foe's "
            lostHP = int(self.badPoison[str(targ)]*targ.stats[0]+1)
            q.add(genFunc(self.app.runText,j+targ.name + ' was hurt badly by poison!'))
            if targ.pokemonID == self.userTrainer.team[str(self.userTrainer.active)].pokemonID:
                q.add(genFunc(self.app.HPUpdateUser,max(0,targ.hp-lostHP)))
            else:
                q.add(genFunc(self.app.HPUpdateEnemy,max(0,targ.hp-lostHP)))
            q.add(genFunc(targ.takeDamage,lostHP))
            self.executeTurn(q,False,True,True)
            if lostHP > targ.hp:
                return (numTasks,genFunc(self.EOTKO,targ))
            else:
                return numTasks
        else:
            return False

    def hurtByPoison(self,targ):
        print('start poison')
        self.app.processesComplete = 0
        q = serviceQueue()
        numTasks = 2
        if targ.statusCondition == 'poisoned' and (targ.pokemonID == self.getUserPokemonID() or targ.pokemonID == self.getEnemyPokemonID()):
            if targ.pokemonID == self.userTrainer.team[str(self.userTrainer.active)].pokemonID:
                j = ''
            else:
                j = "Foe's "
            lostHP = int(targ.stats[0]/8+1)
            q.add(genFunc(self.app.runText,j+targ.name + ' was hurt by poison!'))
            if targ.pokemonID == self.userTrainer.team[str(self.userTrainer.active)].pokemonID:
                q.add(genFunc(self.app.HPUpdateUser,max(0,targ.hp-lostHP)))
            else:
                q.add(genFunc(self.app.HPUpdateEnemy,max(0,targ.hp-lostHP)))
            q.add(genFunc(targ.takeDamage,lostHP))
            self.executeTurn(q,False,True,True)
            if lostHP > targ.hp:
                return (numTasks,genFunc(self.EOTKO,targ))
            else:
                return numTasks
        else:
            return False

    def lightScreenEOT(self,trainer):
        if self.lightScreen[trainer] == -1:
            self.lightScreen[trainer] = 0
            return False
        self.lightScreen[trainer] -= 1
        if self.lightScreen[trainer] == 0:
            if trainer == self.enemyTrainer:
                self.app.runText("Foe's light screen wore off!")
            else:
                self.app.runText("Light screen wore off!")
            return False
        else:
            return 0

    def tauntEOT(self,targ):
        targ.tauntCount -= 1
        if targ.tauntCount == 0:
            u = ""
            if targ.pokemonID == self.enemyTrainer.team[str(self.enemyTrainer.active)].pokemonID:
                u = "Foe's "
            self.app.runText(u+targ.name+"'s taunt wore off!")
            targ.taunt = False
            return False
        else:
            return 0

    def trickRoomEOT(self):
        self.trickRoomCount -= 1
        if self.trickRoomCount == 0:
            self.app.runText('The twisted dimensions returned to normal.')
            self.trickRoom = False
            return False
        return 0
        

    def yawnEOT(self,targ): ##it takes one turn for yawn to take effect. flipping it to true effectively flips it
        if targ.pokemonID == self.getUserPokemonID() or targ.pokemonID == self.getEnemyPokemonID():
            if self.yawn[str(targ)] == 1:
                self.yawn[str(targ)] = 0
                return 0
            elif self.yawn[str(targ)] == 0:
                q = serviceQueue()
                j = ''
                if targ.pokemonID == self.getEnemyPokemonID():
                    j = "Foe's "
                q.add(genFunc(self.app.runText,j + targ.name + "'s drowziness caused them to fall asleep!"))
                if targ == self.enemyTrainer.team[str(self.enemyTrainer.active)]:
                    q.add(genFunc(self.app.setEnemyStatus))
                elif targ == self.userTrainer.team[str(self.userTrainer.active)]:
                    q.add(genFunc(self.app.setUserStatus))
                targ.sleepCount = r.randint(2,4)
                targ.statusCondition = 'asleep'
                self.yawn[str(targ)] = -1
                self.executeTurn(q,False,True,True)
                return 1
            elif self.yawn[str(targ)] == -1:
                return False
        else:
            return False

    def wishEOT(self,trainer,ID): ##an identifier is used for this function as otherwise it wouldn't be possible to do it without it causing problems
        if self.wish[trainer][1] != ID or self.wish[trainer][0] == 0: ##if the ID of the current wish != the ID Of this wish, then this is a duplicate leftover and muwst be deleted
            return False ##also gets deleted if wish's effects were executed last turn- i.e. self.wish[trainer][0]==0 as hasnt be decremented yet
        self.wish[trainer][0] -= 1
        if self.wish[trainer][0] == 0 and trainer.team[str(trainer.active)].fainted == False:
            self.app.runText('The wish came true!')
            u = ''
            f = self.app.HPUpdateUser
            if trainer == self.enemyTrainer:
                u = "Foe's "
                f = self.app.HPUpdateEnemy
            if trainer.team[str(trainer.active)].hp == trainer.team[str(trainer.active)]:
                self.app.runText(u+trainer.team[str(trainer.active)].name + "'s HP is already full!")
                self.wish[trainer] = [0,0]
            else:
                p = trainer.team[str(trainer.active)]
                p.hp = min(p.hp+int(p.stats[0]/2),p.stats[0])
                f(p.hp)
                self.wish[trainer] = [0,0]
                return 1
        elif self.wish[trainer][0] == 0 and trainer.team[str(trainer.active)].fainted == True:
            self.app.runText('The wish came true!')
            self.app.runText("But there were no targets to receive the wish's effects...")
            self.wish[trainer] = [0,0]
        return 0
                

    def EOTKO(self,targ):
        self.app.processesComplete = 0
        numTasks = 2
        q = serviceQueue()
        if self.userTrainer.team[str(self.userTrainer.active)] == targ:
            u = True
            j = ''
            self.userTrainer.team[str(self.userTrainer.active)].fainted = True
        else:
            u = False
            j = "Foe's "
            self.enemyTrainer.team[str(self.enemyTrainer.active)].fainted = True
        #q.add(genFunc(self.app.runText,j + targ.name + ' has fainted!'))
        if u:
            q.add(self.app.userPokemonFaint)
        else:
            q.add(self.app.enemyPokemonFaint)
        self.executeTurn(q,False,True,True)
        return numTasks
            

    def endOfTurn(self,i=0,numTasks=0):
        ##OK so what's going on here...
        ##Well I have a series of end of turn functions
        ##The functions will tell me whether or not I need to delete them.
        ##numTasks is the output of an EOT function (these are specially designed as there are a limited
        ##     number of tasks that will need to use this.
        ## BOOL: (i.e. False) indicates the func needs to be removed
        ## INT: indicates the func is running and is doing master.after nonsense. So the endOfTurn() should continue
        ##      to iterate over itself until the number of tasks that are running are completed.
        ## TUPLE: this func needs to call another func urgently and will need to do so immediately after the current
        ##        one has finished. in form (numProcessesStarted, funcToBeExec'd)
        ## LIST: this func needs to call another func. it should be added to the end of the EOTQueue. In form:
        ##       in form [numProcessesStarted, funcToBeExec'd]
        if i == 0:
            self.app.processesComplete = 0
            self.removeList = []
        if i == len(self.endOfTurnQueue.q) and numTasks == self.app.processesComplete:
            self.removeList = self.removeList[::-1]
            for item in self.removeList:
                del self.endOfTurnQueue.q[item]
                #if x == False:
                #    print('CRAP THERES AN ERROR IN ENDOFTURN QUEUE')
                #    print(item)
            print('execing fainted thing')
            self.sendInIfFainted()
            return
        if str(numTasks) == 'False':
            self.removeList.append(i-1)
            k = genFunc(self.endOfTurn,i,self.app.processesComplete)
            self.app.master.after(10,k)
        elif type(numTasks) == int: ##either a number of tasks
            if numTasks == self.app.processesComplete:
                self.app.processesComplete = 0
                numTasks = self.endOfTurnQueue.q[i]()
                k = genFunc(self.endOfTurn,i+1,numTasks)
                self.app.master.after(10,k)
            else:
                k = genFunc(self.endOfTurn,i,numTasks) #previously was i + 1
                self.app.master.after(10,k)
        elif type(numTasks) == tuple: ##or if suddenly another func must be called, (num,func)
            if numTasks[0] == self.app.processesComplete:
                numTasks = numTasks[1]()
                if type(numTasks) == int:
                    k = genFunc(self.endOfTurn,i,numTasks)
                elif type(numTasks) == list:
                    self.endOfTurnQueue.add(numTasks[1])
                    k = genFunc(self.endOfTurn,i+1,numTasks[0])
                else:
                    k = genFunc(self.endOfTurn,i,numTasks)
                self.app.master.after(10,k)
            else:
                k = genFunc(self.endOfTurn,i,numTasks)
                self.app.master.after(10,k)

#############################################################
    ##these functions are run after a turn ends and after EOT to check to see if there are any fainted pokemon

    def sendInIfFainted(self):
        q = serviceQueue()
        if self.userTrainer.team[str(self.userTrainer.active)].fainted:
            q.add(self.app.EOTSwitchButtons)
            q.add(self.checkUserSwitch)
        if self.enemyTrainer.team[str(self.enemyTrainer.active)].fainted:
            self.emergencyEnemySwitch = 0
            while True:
                self.emergencyEnemySwitch = (self.emergencyEnemySwitch+1)%6
                if self.enemyTrainer.team[str(self.emergencyEnemySwitch)] != None and not self.enemyTrainer.team[str(self.emergencyEnemySwitch)].fainted:
                    break
            k = genFunc(self.app.runText,self.getEnemyNameAndClass() + ' has sent out ' + self.enemyTrainer.team[str(self.enemyTrainer.active)].name + '!')
            q.add(k)
            q.add(self.checkEnemySwitch)
        print(q.q)
        self.executeTurn(q,EOT=True)

    def checkUserSwitch(self,reset=0):
        self.app.taskFinished = False
        if not reset and self.emergencyUserSwitch == '':
            self.app.master.after(50,self.checkUserSwitch)
            return
        elif reset:
            self.emergencyUserSwitch = ''
            return
        self.userTrainer.active = self.emergencyUserSwitch
        self.userTrainer.team[str(self.userTrainer.active)].switchedInThisTurn = True
        self.app.runText('I choose you! ' + self.userTrainer.team[str(self.userTrainer.active)].name + '!')
        self.app.throwStartPokeball()
        k = genFunc(self.checkUserSwitch,1)
        self.app.master.after(50,k)

    def setUserSwitch(self,switch):
        self.app.disableButtons()
        self.emergencyUserSwitch = switch

    def checkEnemySwitch(self,reset=0):
        self.app.taskFinished = False
        if not reset and self.emergencyEnemySwitch == '':
            self.app.master.after(50,checkEnemySwitch)
            return
        else:
            self.enemyTrainer.active = self.emergencyEnemySwitch
            self.enemyTrainer.team[str(self.enemyTrainer.active)].switchedInThisTurn = True
            self.emergencyEnemySwitch = ''
            self.app.master.after(200)
            self.app.taskFinished = False
            self.app.enemyPokemonSendOut()
            self.emergencyEnemySwitch = ''

#############################################################
        ##functions here are for damage

    def findDamage(self,user,target,move):
        combinedModifiers = self.combinedModifiers(user,target,move)
        typeModifiers = self.typeModifiers(user,target,move)
        if typeModifiers[0] == 0:
            return (0,0)
        L = int(user.level)
        P = int(move.power)
        if move.name == 'Punishment':
            for mod in target.modifiers:
                if mod > 0:
                    P += 20 * mod
        if move.name == 'Electro Ball': ##different modifiers depneding ons peed ratio
            electroBallDict = {3:120,2:80,1:60,0:40} ##here are the modifiers for floor(ratio)
            electroBallRatio = int(user.stats[5]/target.stats[5]) ##here is floor(ratio)
            if electroBallRatio in electroBallDict: ##this my good sir is the check for the electroballratiodict as it might not be in dict
                P = electroBallDict[electroBallRatio]
            else:
                P = 150 ##if it gets here... well my friend, that enemy pokemon will be f r i e d
        
        if move.category == 'Physical':
            A = user.stats[1]
            D = target.stats[2]
        elif move.category == 'Special':
            A = user.stats[3]
            D = target.stats[4]
        damage = int(int(((((2 * L)/5 + 2) * P * A/D * combinedModifiers)/50 + 2)) * typeModifiers[0] * r.uniform(0.85,1.00))
        print(damage)
        return (damage,typeModifiers[1])
    
    def combinedModifiers(self,user,target,move):
        ## In Pokemon, there are a lot of modifiers that we need to account for.
        ## These modifiers include type advantages, stat boosts/decreases (i.e.  attack x2, defense x0.5)
        ## and ability modifiers from abilities such as huge power.
        ## FINISH THIS
            ## Currently this does not take into account abilities
            ## It should check to see if the ability is a damage modifying ability
            ## If it is, the ability should be checked for the modifier and the appropriate modifier should be applied

        Modifier = 1
        
        ##physical/special mods
        if move.category == 'Physical':
            Modifier = Modifier * stages[str(user.modifiers[1])]
            if move.name not in ['Chip Away']:
                Modifier = Modifier / stages[str(target.modifiers[2])]
        else:
            Modifier = Modifier * stages[str(user.modifiers[3])] / stages[str(target.modifiers[4])]

        ##Move specific changes
        if move.name == 'Facade' and (user.statusCondition == 'poisoned' or user.statusCondition == 'burned' or user.statusCondition == 'paralyzed' or user.statusCondition == 'badly poisoned'):
            Modifier = Modifier * 2
        if move.name == 'Venoshock' and (target.statusCondition == 'poisoned' or target.statusCondition == 'badly poisoned'):
            Modifier = Modifier * 2

        ##misc
        if user.statusCondition == 'burned' and move.category == 'Physical':
            Modifier = Modifier/2

        return Modifier

    def typeModifiers(self,user,target,move):
        ## This returns data in the form (modifier,isSuperEffective)
        ## Modifier is a floating point number, isSuperEffective is a boolean though will be an integer (2) if no damage is dealt
        ##dependent on types
        Modifier = 1
        superEffective,notVeryEffective = False,False
        for Type in target.types:
            if move.type in immune[Type]:
                return (0,0)
            elif move.type in weakness[Type]:
                Modifier = Modifier * 2
                superEffective = True
            elif move.type in resistance[Type]:
                Modifier = Modifier / 2
                notVeryEffective = True
        if move.type == 'Ground' and target.magnetRise:
            return (0,0)
        
        if move.category == 'Special' and self.lightScreen[target.trainer] > 0:
            Modifier = Modifier/2
        elif move.category == 'Physical' and self.reflect[target.trainer] > 0:
            Modifier = Modifier/2

        chance = 16
        if move.name in ['Blaze Kick','Shadow Claw','Slash','Stone Edge']:
            chance = 8
        if r.randint(0,chance) == 0:
            self.criticalHit = True
            Modifier = Modifier * 2
        
        if move.type in user.types:
            Modifier = Modifier * 1.5
        if superEffective and notVeryEffective:
            return (Modifier,-1)
        elif superEffective and not notVeryEffective:
            return (Modifier,2)
        elif not superEffective and notVeryEffective:
            return (Modifier,1)
        elif not superEffective and not notVeryEffective:
            return (Modifier,-1)
        

class serviceQueue:
    def __init__(self):
        self.q = []
        self.id = -1
    def rem(self):
        x = self.q[0]
        del self.q[0]
        return x
    def add(self,obj):
        self.q.append(obj)
        self.id += 1
        return self.id
    def searchAndDestroy(self,obj):
        count = 0
        for x in self.q:
            if x == obj:
                del self.q[count]
                return True
            count += 1
        return False
    def empty(self):
        self.q = []

class move:
    def __init__(self,name,pokemon):
        global moveInfo
        functions = {
            #A
            'Acrobatics':self.doesNothing,
            'Aerial Ace':self.doesNothing,
            'Amnesia':self.amnesia,
            'Aqua Jet':self.doesNothing,
            'Aqua Tail':self.doesNothing,
            'Aura Sphere':self.doesNothing,

            #B
            'Blaze Kick':self.blazeKick,
            'Brick Break':self.doesNothing,
            'Bone Rush':self.doesNothing,

            #C
            'Calm Mind':self.calmMind,
            'Crunch':self.crunch,
            'Chip Away':self.doesNothing,
            'Clear Smog':self.clearSmog,
            'Close Combat':self.closeCombat,

            #D
            'Dark Pulse':self.darkPulse,
            'Discharge':self.discharge,
            'Double Team':self.doubleTeam,
            'Dual Chop':self.doesNothing,
            'Dragon Dance':self.dragonDance,
            'Dragon Pulse':self.doesNothing,
            'Drain Punch':self.drainPunch,
            
            #E
            'Earthquake':self.doesNothing,
            'Electro Ball':self.doesNothing,
            'Energy Ball':self.energyBall,
            'Extreme Speed':self.doesNothing,
            
            #F
            'Facade':self.doesNothing,
            'Fake Out':self.fakeOut,
            'Fire Fang':self.fireFang,
            'Fire Punch':self.firePunch,
            'Flash Cannon':self.flashCannon,

            #G
            'Giga Drain':self.gigaDrain,
            'Gunk Shot':self.gunkShot,

            #I
            'Ice Fang':self.iceFang,
            'Ice Punch':self.icePunch,
            'Iron Tail':self.ironTail,
            'Iron Defense':self.ironDefense,

            #L
            'Light Screen':self.lightScreen,

            #M
            'Mach Punch':self.doesNothing,
            'Magical Leaf':self.doesNothing,
            'Magnet Rise':self.magnetRise,
            'Metal Claw':self.metalClaw,
            'Moonblast':self.moonblast,

            #P
            'Protect':self.protect,
            'Psychic':self.psychic,
            'Punishment':self.doesNothing,

            #R
            'Reflect':self.reflect,
            'Rock Slide':self.rockSlide,
            'Rock Blast':self.doesNothing,

            #S
            'Screech':self.screech,
            'Shadow Ball':self.shadowBall,
            'Shadow Claw':self.doesNothing,
            'Slash':self.doesNothing,
            'Sludge Bomb':self.sludgeBomb,
            'Solar Beam':self.solarBeam,
            'Spore':self.spore,
            'Stone Edge':self.doesNothing,
            'Superpower':self.superpower,
            'Swords Dance':self.swordsDance,
            'Synthesis':self.synthesis,
            
            #T
            'Tackle':self.doesNothing,
            'Taunt':self.taunt,
            'Thunder':self.thunder,
            'Thunderbolt':self.thunderbolt,
            'Thunder Fang':self.thunderFang,
            'Thunder Punch':self.thunderPunch,
            'Thunder Wave':self.thunderWave,
            'Toxic':self.toxic,
            'Trick Room':self.trickRoom,

            #V
            'Venoshock':self.doesNothing,

            #W
            'Will-O-Wisp':self.willOWisp,
            'Wish':self.wish,
            
            #Y
            'Yawn' : self.yawn,

            #Z
            'Zap Cannon' : self.zapCannon
            }
        
        moveSpecifier = {'Bone Rush' : 'multihit','Dual Chop' : 'twohit','Rock Blast':'multihit'}
        self.name = name
        self.type = moveInfo[name]['type']
        self.category = moveInfo[name]['category']
        self.description = moveInfo[name]['description']
        self.power = moveInfo[name]['power']
        self.accuracy = moveInfo[name]['accuracy']
        self.function = functions[self.name]
        self.priority = moveInfo[name]['priority']
        try:
            self.specifier = moveSpecifier[self.name]
        except KeyError:
            self.specifier = 'regular'
        self.secondCall = False
        self.failedExecution = False
        self.tauntDidntWork = False

    def statChange(self,arena,targ,stat,modifier,dontSayIfNothingHappens=False):
        x = targ.changeModifier(stat,modifier)
        if x == 'ALLOK':
            if modifier > 0:
                h = 'rose'
            elif modifier < 0:
                h = 'fell'
            d = {1:'',2:' sharply',3:' drastically',-1:'',-2:' harshly'}
            u = ''
            if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                u = "Foe's "
            return arena.app.runText(u + targ.name + "'s " + stat + " " + h + d[modifier]+'!')
        else:
            if modifier > 0:
                h = 'higher'
            elif modifier < 0:
                h = 'lower'
            u = ''
            if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                u = "foe's "
            if not dontSayIfNothingHappens:
                arena.app.runText("But " + u + targ.name + "'s " + stat + " can't go any " + h + "!")

    def activate(self):
        exec(self.function)
        
    ##FUNCTIONS FOR MOVE EXECUTION BELOW

    def doesNothing(self,arena,user,targ):
        arena.app.taskFinished = True

    ##A
        
    def amnesia(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Special Defense',2)
        arena.app.taskFinished = True

    ##B

    def blazeKick(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            if targ.types[1].lower() != 'fire' and targs.types[0].lower() != 'fire' and targ.statusCondition == None:
                targ.statusCondition = 'burned'
                u = ''
                f = self.setUserStatus
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                    f = self.setEnemyStatus
                arena.app.runText(u + targ.name + ' was burned!')
                f()
                self.endOfTurnQueue.add(arena.hurtByBurn,targ)
        arena.app.taskFinished = True

    ##C

    def calmMind(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Special Attack',1)
        self.statChange(arena,user,'Special Defense',1)
        arena.app.taskFinished = True

    def clearSmog(self,arena,user,targ,earlyExecute=False):
        arena.app.taskFinished = False
        if earlyExecute:
            targ.modifiers = [0,0,0,0,0,0]
            targ.evasion = 0
            targ.accuracy = 0
        else:
            u = ''
            if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                u = "Foe's "        
            arena.app.runText(u + targ.name + ' had their stat changes reset!')
        arena.app.taskFinished = True

    def closeCombat(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Defense',-1)
        self.statChange(arena,user,'Special Defense',-1)
        arena.app.taskFinished = True

    def crunch(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.8:
            x = self.statChange(arena,targ,'defense',-1,True)
        arena.app.taskFinished = True

    ##D

    def darkPulse(self,arena,user,targ,earlyExecute=False):
        if earlyExecute:
            if r.uniform(0,1) > 0.8:
                targ.flinched = True
        arena.app.taskFinished = True

    def discharge(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.7:
            if targ.statusCondition == None and targ.types[1].lower() != 'electric' and targ.types[0].lower() != 'electric':
                targ.statusCondition == 'paralyzed'
                u = ''
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                arena.app.runText(u + targ.name + " was paralyzed!")
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    arena.app.setEnemyStatus()
                elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                    arena.app.setUserStatus()
        arena.app.taskFinished = True

    def doubleTeam(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Evasion',2)
        arena.app.taskFinished = True

    def dragonDance(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Attack',1)
        self.statChange(arena,user,'Speed',1)
        arena.app.taskFinished = True

    def drainPunch(self,arena,user,targ):
        arena.app.taskFinished = False
        u = ''
        f = arena.app.HPUpdateUser
        if user.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
            u = "Foe's "
            f = arena.app.HPUpdateEnemy
        if user.hp < user.stats[0]:
            arena.app.runText(u + user.name + ' regained some HP!')
            print(user.lastDamageDealt/2+1)
            f(min(user.stats[0],user.hp+int(user.lastDamageDealt/2+1)),updateInGui=True)
        else:
            arena.app.taskFinished = True

    ##E

    def energyBall(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            x = self.statChange(arena,targ,'special defense',-1,True)
        arena.app.taskFinished = True

    ##F

    def fakeOut(self,arena,user,targ,earlyExecute=False):
        if earlyExecute:
            targ.flinched = True
        arena.app.taskFinished = True

    def fireFang(self,arena,user,targ,earlyExecute=False):
        arena.app.taskFinished = False
        if earlyExecute:
            if r.uniform(0,1) > 0.9:
                targ.flinched = True
        else:
            if r.uniform(0,1) > 0.9:
                if targ.types[1].lower() != 'fire' and targs.types[0].lower() != 'fire' and targ.statusCondition == None:
                    targ.statusCondition = 'burned'
                    u = ''
                    f = self.setUserStatus
                    if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                        u = "Foe's "
                        f = self.setEnemyStatus
                    arena.app.runText(u + targ.name + ' was burned!')
                    f()
                    self.endOfTurnQueue.add(arena.hurtByBurn,targ)
            arena.app.taskFinished = True
        arena.app.taskFinished = True

    def firePunch(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            if targ.types[1].lower() != 'fire' and targs.types[0].lower() != 'fire' and targ.statusCondition == None:
                targ.statusCondition = 'burned'
                u = ''
                f = self.setUserStatus
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                    f = self.setEnemyStatus
                arena.app.runText(u + targ.name + ' was burned!')
                f()
                self.endOfTurnQueue.add(arena.hurtByBurn,targ)
        arena.app.taskFinished = True

    def flashCannon(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            x = targ.changeModifier('special defense',-1)
            if x == 'ALLOK':
                u = ''
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                #arena.app.runText(u + targ.name + "'s special defense fell!")
        arena.app.taskFinished = True

    ##G

    def gigaDrain(self,arena,user,targ):
        arena.app.taskFinished = False
        u = ''
        f = arena.app.HPUpdateUser
        if user.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
            u = "Foe's "
            f = arena.app.HPUpdateEnemy
        if user.hp < user.stats[0]:
            arena.app.runText(u + user.name + ' regained some HP!')
            f(min(user.stats[0],user.hp+int(user.lastDamageDealt/2+1)),updateInGui=True)
        else:
            arena.app.taskFinished = True

    def gunkShot(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.7:
            if targ.types[0].lower() not in ['poison','steel'] and targ.types[1].lower() not in ['poison','steel'] and targ.statusCondition == None:
                targ.statusCondition = 'poisoned'
                u = ''
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    u = "Foe's "
                arena.app.runText(u + targ.name + ' was poisoned!')
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    arena.app.setEnemyStatus()
                elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                    arena.app.setUserStatus()
                arena.endOfTurnQueue.add(genFunc(arena.hurtByPoison,targ))
        arena.app.taskFinished = True

    ##I

    def iceFang(self,arena,user,targ,earlyExecute=False):
        arena.app.taskFinished = False
        if earlyExecute:
            if r.uniform(0,1) > 0.9:
                targ.flinched = True
        else:
            if r.uniform(0,1) > 0.9:
                if targ.types[1].lower() != 'ice' and targs.types[0].lower() != 'ice' and targ.statusCondition == None:
                    targ.statusCondition = 'freeze'
                    u = ''
                    x = self.setUserStatus
                    if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                        u = "Foe's "
                        x = self.setEnemyStatus
                    arena.app.runText(u + targ.name + ' was frozen solid!')
                    x()
        arena.app.taskFinished = True

    def icePunch(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            if targ.types[1].lower() != 'ice' and targs.types[0].lower() != 'ice' and targ.statusCondition == None:
                targ.statusCondition = 'freeze'
                u = ''
                x = self.setUserStatus
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                    x = self.setEnemyStatus
                arena.app.runText(u + targ.name + ' was frozen solid!')
                x()
        arena.app.taskFinished = True

    def ironTail(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.7:
            x = targ.changeModifier('defense',-1)
            if x == 'ALLOK':
                u = ''
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                arena.app.runText(u + targ.name + "'s defense fell!")
        arena.app.taskFinished = True

    def ironDefense(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Defense',2)
        arena.app.taskFinished = True

    ##L

    def lightScreen(self,arena,user,targ):
        arena.app.taskFinished = False
        if arena.lightScreen[user.trainer] > 0:
            arena.app.runText('But a light screen is already in effect!')
            arena.app.taskFinished = True
            return
        arena.app.runText('A wondrous wall of light appeared that is weakening special attacks!')
        arena.lightScreen[user.trainer] = 6
        arena.endOfTurnQueue.add(genFunc(arena.lightScreenEOT,user.trainer))
        arena.app.taskFinished = True
        

    ##M

    def magnetRise(self,arena,user,targ):
        arena.app.taskFinished = False
        targ.magnetRise = True
        u = "Foe's "
        if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
            u = ""
        arena.app.runText(u + targ.name + " has started floating in the air!")
        arena.app.taskFinished = True

    def metalClaw(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            x = self.statChange(arena,user,'attack',1,True)
        arena.app.taskFinished = True

    def moonblast(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.7:
            self.statChange(arena,targ,'Special Attack',-1,True)
        arena.app.taskFinished = True

    ##P

    def protect(self,arena,user,targ,earlyExecute=False):
        arena.app.taskFinished = False
        if earlyExecute:
            if r.uniform(0,1) > 1 - (0.5) ** user.protectCount:
                user.lastUsedProtect = True
                user.protectCount += 1
            else:
                user.lastUsedProtect = False
        else:
            if not user.lastUsedProtect: ##if it satisifies this, then protect failed
                arena.app.runText('But it failed!')
        arena.app.taskFinished = True

    def psychic(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            self.statChange(arena,targ,'Special Defense',-1,True)
        arena.app.taskFinished = True

    def punishment(self,arena,user,targ):
        arena.app.taskFinished = True

    ##R

    def reflect(self,arena,user,targ):
        arena.app.taskFinished = False
        if arena.reflect[user.trainer] > 0:
            arena.app.runText('But a reflect is already in effect!')
            arena.app.taskFinished = True
            return
        arena.app.runText('A wondrous wall of light appeared that is weakening physical attacks!')
        arena.reflect[user.trainer] = 6
        arena.endOfTurnQueue.add(genFunc(arena.reflectEOT,user.trainer))
        arena.app.taskFinished = True

    def rockSlide(self,arena,user,targ,earlyExecute=False):
        if earlyExecute:
            if r.uniform(0,1) > 0.7:
                targ.flinched = True
        arena.app.taskFinished = True

    ##S

    def screech(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,targ,'Defense',-2)
        arena.app.taskFinished = True

    def shadowBall(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.8:
            x = self.statChange(arena,targ,'special defense',-1,True)
        arena.app.taskFinished = True

    def sludgeBomb(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.7:
            if targ.types[0].lower() not in ['poison','steel'] and targ.types[1].lower() not in ['poison','steel'] and targ.statusCondition == None:
                targ.statusCondition = 'poisoned'
                u = ''
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    u = "Foe's "
                arena.app.runText(u + targ.name + ' was poisoned!')
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    arena.app.setEnemyStatus()
                elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                    arena.app.setUserStatus()
                arena.endOfTurnQueue.add(genFunc(arena.hurtByPoison,targ))
        arena.app.taskFinished = True

    def solarBeam(self,arena,user,targ):
        arena.app.taskFinished = False
        if user.twoTurnMove == None:
            if user.pokemonID == arena.userTrainer.team[str(arena.userTrainer.active)].pokemonID:
                u = ""
                ID = 'user'
            else:
                u = "Foe's "
                ID = 'enemy'
            count = 0
            for MOVE in user.moves:
                if MOVE[0].name == 'Solar Beam':
                    if ID == 'enemy':
                        user.twoTurnMove = ['attack',MOVE[0],ID]
                    else:
                        user.twoTurnMove = ['attack',count,ID]
                    break
                count += 1
            print(user.twoTurnMove)
            arena.app.runText(u + user.name + ' is absorbing light!')
        else:
            user.twoTurnMove = None
        arena.app.taskFinished = True

    def spore(self,arena,user,targ,earlyExecute=False):
        arena.app.taskFinished = False
        if earlyExecute:
            if targ.statusCondition == None:
                targ.statusCondition = 'asleep'
            else:
                self.failedExecution = True
        else:
            if not self.failedExecution:
                u = ''
                f = arena.app.setUserStatus
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    u = "Foe's "
                    f = arena.app.setEnemyStatus
                arena.app.runText(u + targ.species + ' fell asleep!')
                targ.sleepCount = r.randint(2,4)
                f()
            else:
                arena.app.runText('But it had no effect!')
        arena.app.taskFinished = True

    def superpower(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Attack',-1)
        self.statChange(arena,user,'Defense',-1)
        arena.app.taskFinished = True

    def swordsDance(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Attack',2)
        arena.app.taskFinished = True

    def synthesis(self,arena,user,targ):
        arena.app.taskFinished = False
        u = ''
        f = arena.app.HPUpdateUser
        if user.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
            u = "Foe's "
            f = arena.app.HPUpdateEnemy
        if user.hp < user.stats[0]:
            arena.app.runText(u + user.name + ' regained some HP!')
            f(min(user.stats[0],user.hp+int(0.5*user.stats[0])),updateInGui=True)
        else:
            arena.app.runText(u + user.name + "'s HP is already full!")
            arena.app.taskFinished = True

    ##T

    def taunt(self,arena,user,targ,earlyExecute=False):
        arena.app.taskFinished = False
        if targ.tauntCount == 0 and earlyExecute:
            targ.taunt = True
            self.tauntDidntWork = True
            targ.tauntCount = 4
        else:
            if targ.tauntDidntWork == True:
                arena.app.runText('But it had no effect!')
                self.tauntDidntWork = False
            else:
                u = "Foe's "
                if user == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    u = ''
                arena.app.runText(u + targ.name + ' fell for the taunt!')
                arena.endOfTurnQueue.add(genFunc(arena.tauntEOT,targ))
        arena.app.taskFinished = True

    def thunder(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.7:
            if targ.statusCondition == None and targ.types[1].lower() != 'electric' and targ.types[0].lower() != 'electric':
                targ.statusCondition = 'paralyzed'
                u = ''
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                arena.app.runText(u + targ.name + " was paralyzed!")
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    arena.app.setEnemyStatus()
                elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                    arena.app.setUserStatus()
        arena.app.taskFinished = True

    def thunderbolt(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            if targ.statusCondition == None and targ.types[1].lower() != 'electric' and targ.types[0].lower() != 'electric':
                targ.statusCondition = 'paralyzed'
                u = ''
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                arena.app.runText(u + targ.name + " was paralyzed!")
                if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                    arena.app.setEnemyStatus()
                elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                    arena.app.setUserStatus()
        arena.app.taskFinished = True

    def thunderFang(self,arena,user,targ,earlyExecute=False):
        arena.app.taskFinished = False
        if earlyExecute:
            if r.uniform(0,1) > 0.9:
                targ.flinched = True
        else:
            if r.uniform(0,1) > 0.9:
                if targ.statusCondition == None and targ.types[1].lower() != 'electric' and targ.types[0].lower() != 'electric':
                    targ.statusCondition = 'paralyzed'
                    u = ''
                    f = arena.app.setUserStatus
                    if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                        u = "Foe's "
                        arena.app.setEnemyStatus
                    arena.app.runText(u + targ.name + " was paralyzed!")
                    f()
        arena.app.taskFinished = True
            
        
    def thunderPunch(self,arena,user,targ):
        arena.app.taskFinished = False
        if r.uniform(0,1) > 0.9:
            if targ.statusCondition == None and targ.types[1].lower() != 'electric' and targ.types[0].lower() != 'electric':
                targ.statusCondition = 'paralyzed'
                u = ''
                f = arena.app.setUserStatus
                if targ.pokemonID == arena.enemyTrainer.team[str(arena.enemyTrainer.active)].pokemonID:
                    u = "Foe's "
                    arena.app.setEnemyStatus
                arena.app.runText(u + targ.name + " was paralyzed!")
                f()
        arena.app.taskFinished = True
                                  

    def thunderWave(self,arena,user,targ):
        arena.app.taskFinished = False
        if targ.statusCondition == None and targ.types[0].lower() not in ['ground','electric'] and targ.types[1].lower() not in ['ground','electric']:
            targ.statusCondition = 'paralyzed'
            u = ''
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                u = "Foe's "
            arena.app.runText(u + targ.name + ' was paralyzed!')
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                arena.app.setEnemyStatus()
            elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                arena.app.setUserStatus()
        else:
            arena.app.runText('But it had no effect!')
        arena.app.taskFinished = True

    def toxic(self,arena,user,targ):
        arena.app.taskFinished = False
        if targ.types[0].lower() not in ['poison','steel'] and targ.types[1].lower() not in ['poison','steel'] and targ.statusCondition == None:
            targ.statusCondition = 'badly poisoned'
            u = ''
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                u = "Foe's "
            arena.app.runText(u + targ.name + ' was badly poisoned!')
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                arena.app.setEnemyStatus()
            elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                arena.app.setUserStatus()
            arena.endOfTurnQueue.add(genFunc(arena.hurtByBadPoison,targ))
        else:
            arena.app.runText('But it had no effect!')
        arena.app.taskFinished = True

    def trickRoom(self,arena,user,targ):
        arena.app.taskFinished = False
        if not arena.trickRoom:
            arena.trickRoom = True
            arena.trickRoomCount = 6
            arena.endOfTurnQueue.add(arena.trickRoomEOT)
            u = ''
            if user == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                u = "Foe's "
            arena.app.runText(u + user.name + ' twisted the dimensions!')
        else:
            arena.app.runText('But nothing happened!')
        arena.app.taskFinished = True

    ##W

    def willOWisp(self,arena,user,targ):
        arena.app.taskFinished = False
        if targ.types[0].lower() not in ['fire'] and targ.types[1].lower() not in ['fire'] and targ.statusCondition == None:
            u = ''
            f = arena.app.setUserStatus
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                u = "Foe's "
                f = arena.app.setEnemyStatus
            arena.app.runText(u + targ.name + ' was burned!')
            targ.statusCondition = 'burned'
            f()
            arena.endOfTurnQueue.add(genFunc(arena.hurtByBurn,targ))
        else:
            arena.app.runText('But it had no effect!')
        arena.app.taskFinished = True

    def wish(self,arena,user,targ):
        arena.app.taskFinished = False
        if arena.wish[user.trainer][0] == 0:
            arena.app.runText('A wish was made to the heavens...')
            t = str(time.time())
            arena.wish[user.trainer] = [2,t]
            arena.endOfTurnQueue.add(genFunc(arena.wishEOT,user.trainer,t))
        else:
            arena.app.runText('But it failed!')
        arena.app.taskFinished = True

    ##Y

    def yawn(self,arena,user,targ):
        arena.app.taskFinished = False
        if targ.statusCondition != None:
            arena.app.runText('But it had no effect!')
            arena.app.taskFinished = True
            return
        if user == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
            j = "Foe's "
            u = ''
        else:
            j = ''
            u = "the foe's "
        arena.app.runText(j + user.name + ' made ' + u + targ.name + ' drowzy.')
        arena.yawn[str(targ)] = 1
        arena.endOfTurnQueue.add(genFunc(arena.yawnEOT,targ))
        arena.app.taskFinished = True

    ##Z

    def zapCannon(self,arena,user,targ):
        arena.app.taskFinished = False
        if targ.types[0].lower() not in ['ground','electric'] and targ.types[1].lower() not in ['ground','electric']:
            targ.statusCondition = 'paralyzed'
            u = ''
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                u = "Foe's "
            arena.app.runText(u + targ.name + ' was paralyzed!')
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                arena.app.setEnemyStatus()
            elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                arena.app.setUserStatus()
        arena.app.taskFinished = True




########################################################
    def leechSeed(self,arena):
        pass

    def vineWhip(self,arena,user,targ):
        arena.app.taskFinished=True
        ##MOVE FUNCTIONS SHOULD RETURN A TUPLE
        ##The tuple should contain an ordered set of commands that the program can add to the service queue
        arena

    def growl(self,arena,user,targ):
        arena.app.taskFinished = False
        x = targ.changeModifier('attack',-1)
        if x == 'ALLOK':
            arena.app.runText(targ.name + "'s attack fell!")
        else:
            arena.app.runText('But ' + targ.name + "'s attack can't go any lower!")
        arena.app.taskFinished = True
