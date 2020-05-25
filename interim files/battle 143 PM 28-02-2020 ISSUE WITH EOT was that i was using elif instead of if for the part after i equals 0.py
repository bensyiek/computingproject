##CONSIDER ADDING A SLIDING GREY RECTANGLE TO THE TABLET FOR UPDATING POKEMON.
##CAN MAKE IT SO THAT IT DOESN'T REGISTER GO AGAINT UNTIL IT HAS COMPLETELY FINISHED

import random as r
from pkmnData import *


IDAssign = 0

def genFunc(f, *args):
    return lambda *args2: f(*args)

class pokemon:
    def __init__(self,species,level,trainer=False):
        
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
        self.flinched = False
        self.protect = False
        
    def getTrainer(self):
        self.trainer = trainer
        self.trainer.addPokemon(self)

    def resettables(self):
        self.flinched = False
        self.protect = False

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

    def changeModifier(self,modifier,amount):
        modDict = {'HP':0,'ATTACK':1,'DEFENSE':2,'SPECIAL ATTACK':3,'SPECIAL DEFENSE':4,'SPEED':5}
        if modifier.upper() == 'ACCURACY':
            if self.accuracy==6 and amount > 0:
                return 'higher'
            elif self.accuracy==-6 and amount < 0:
                return 'lower'
            else:
                self.accuracy += amount
                return True
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

class move:
    def __init__(self,name,pokemon):
        global moveInfo
        self.name = name
        self.type = moveInfo[name]['type']
        self.category = moveInfo[name]['category']
        self.description = moveInfo[name]['description']
        self.power = moveInfo[name]['power']
        self.accuracy = moveInfo[name]['accuracy']
        self.function = moveInfo[name]['function']
        self.secondCall = False

    def activate(self):
        exec(self.function)

    def tackle(self,arena):
        arena

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
    def __init__(self,name,trainerClass,spriteName):
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
        self.badPoison = {}
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

    def getEnemyNameAndClass(self):
        return self.enemyTrainer.trainerClass + ' ' + self.enemyTrainer.name

    def getEnemySpecies(self):
        return self.enemyTrainer.team[str(self.enemyTrainer.active)].name

    def doesMoveHit(self,move,user):
        if r.uniform(0,100) <= move.accuracy * accStages[str(user.accuracy)]:
            return True
        else:
            return False

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
        if userInput[0] == 'attack' and enemyInput[0] == 'attack': ## need to decide which goes first
            ## first check priority if both are attacks- then if one's priority is higher we do this
            if userInput[1].priority > enemyInput[1].priority: 
                order = (userInput,enemyInput)
            elif userInput[1].priority < enemyInput[1].priority:
                order =(enemyInput,userInput)
            else: ## if here, priority is same (as will be the case for most moves) so must use speed to tie break
                if self.userTrainer.team[str(self.userTrainer.active)].stats[5] > self.enemyTrainer.team[str(self.enemyTrainer.active)].stats[5]:
                    order = (userInput,enemyInput)
                elif self.userTrainer.team[str(self.userTrainer.active)].stats[5] < self.enemyTrainer.team[str(self.enemyTrainer.active)].stats[5]:
                    order = (enemyInput,userInput)
                else: ## speeds are tied so we choose randomly
                    order = tuple(r.shuffle([enemyInput,userInput]))
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
                order = tuple(r.shuffle([enemyInput,userInput]))
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

                    k = genFunc(self.app.runText,r.choice(userSwitchMessages) % self.findActiveName(self.userTrainer))
                    q.add(k)
                    q.add(self.app.switchUser)
                    k = genFunc(self.setUserActive,x[1])
                    q.add(k)
                    k = genFunc(self.app.runText,r.choice(userSendInMessages) % self.findActiveName(self.userTrainer))
                    q.add(k)
                    q.add(self.app.throwStartPokeball)
                    tempActiveUserTrainer = str(x[1])
                elif x[2] == 'enemy':
                    k = genFunc(self.app.runText,self.getEnemyNameAndClass() +' calls back '+ self.getEnemySpecies()+'!')
                    q.add(k)
                    q.add(self.app.switchEnemy)
                    k = genFunc(self.setEnemyActive,x[1])
                    q.add(k)
                    k = genFunc(self.app.runText,self.getEnemyNameAndClass() + ' sends in '+ self.getEnemySpecies()+'!')
                    q.add(k)
                    q.add(self.app.enemyPokemonSendOut)
            elif x[0] == 'attack':
                if x[2] == 'user':
                    user = self.userTrainer.team[str(tempActiveUserTrainer)] ##user here refers to the pokemon using the move
                    targ = self.enemyTrainer.team[str(tempActiveEnemyTrainer)]
                    UserFainted = self.faintedMidBattle[0]
                    f = "Foe's "
                    u = ''
                else:
                    user = self.enemyTrainer.team[str(tempActiveEnemyTrainer)]
                    targ = self.userTrainer.team[str(tempActiveUserTrainer)]
                    UserFainted = self.faintedMidBattle[1]
                    f = ""
                    u = "Foe's "
                ##FINISH THIS SECTION
                    ##this is for a successful attack
                    ##should check to see the damage
                    ##if it is >= to pokemon's hp, set damage to pokemon's HP and trigger fainting
                    ##add switching to end of turn if faintws
                    ##also make sure it hits the pokemon that switches in if user switches as their action
                    ##for turn, not curr pokemon.
                if user.flinched == True:
                    k = genFunc(self.app.runText,u + user.name + ' flinched!')
                    q.add(k)
                    badFlag = 1 ##they can't do their thing
                elif user.statusCondition == 'paralyzed':
                    if r.choice([0,1]) == 1:
                        k = genFunc(self.app.runText, u + self.findActiveName(user) + ' is paralyzed and cannot move!')
                        q.add(k)
                        badFlag = 1
                if not UserFainted and badFlag == 0:
                    ##there are so many problems with this
                    ##for one it assumes it is HPUpdateEnemy that is getting activated
                    ##THIS AINT NECESSARILY TRUE
                    ##also the user attacks themselves??
                    ##ben please fix
                    ##
                    ##hi past ben, i think i've fixed but not sure :P can another future ben check
                    print(x)
                    loop = 1
                    if x[1].specifier == 'multihit':
                        loop = r.randint(2,5)
                    k = genFunc(self.app.runText,u + user.name + ' used ' + x[1].name + '!')
                    q.add(k)
                    if self.doesMoveHit(x[1],user):
                        for hit in range(0,loop):
                            if x[1].category != 'Status':
                                damage = self.findDamage(user,targ,x[1])
                                if damage[1] == 2:
                                    k = genFunc(self.app.runText,'But it had no effect!')
                                    q.add(k)
                                    break
                                else:
                                    E2U = {'user':'enemy','enemy':'user'}
                                    q.add(genFunc(self.app.useMove,x[1].type,E2U[x[2]]))
                                    print(damage[0])
                                    if damage[0] >= targ.hp:
                                        print('bigger than')
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
                                        if x[2] == 'user':
                                            k = genFunc(self.app.enemyPokemonFaint)
                                            q.add(k)
                                            self.faintedMidBattle[1] = True
                                        else:
                                            k = genFunc(self.app.userPokemonFaint)
                                            q.add(k)
                                            self.faintedMidBattle[0] = True
                                        break ##need to break out if fainted.
                                    else:
                                        if x[2] == 'user':
                                            k = genFunc(self.app.HPUpdateEnemy,targ.hp-damage[0])
                                        else:
                                            k = genFunc(self.app.HPUpdateUser,targ.hp-damage[0])
                                        q.add(k)
                                        k = genFunc(targ.takeDamage,damage[0])
                                        q.add(k)
                                    k = genFunc(x[1].function,self,user,targ)
                                    q.add(k)
                                ## FROM HERE!!
                                        ## Need to process the damage being visualized
                                        ## Currently I've got it so that it marks a pokemon being damaged
                                        ## but the pokemon itself doesn't take the damage yet.
                                        ## i.e. need to have it so that I'm doing genfunc(takedamage,damage)
                                        ## then do graphics
                                        ## i think that's it?
                                        ## and add abilities. but that's for later.

                                ## BEN DO WE NEED TABS HERE?
                                    ## Looks like we meet calling damage dealing functions twice.
                            elif x[1].category == 'Status':
                                if x[1].name in ['Toxic']:
                                    E2U = {'user':'enemy','enemy':'user'}
                                    q.add(genFunc(self.app.useMove,x[1].type,E2U[x[2]]))
                                k = genFunc(x[1].function,self,user,targ)
                                q.add(k)
                        if loop >= 2:
                            q.add(genFunc(self.app.runText,'Hit ' + str(loop) + ' times!'))
                    else:
                        k = genFunc(self.app.runText,'But it missed!')
                        q.add(k)
                        break
            q.add(self.userTrainer.team[str(self.userTrainer.active)].resettables)
            q.add(self.enemyTrainer.team[str(self.enemyTrainer.active)].resettables)
        print('two execute turns')
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
                    self.app.updateButtons()
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
    def hurtByBurn(self,targ):
        self.app.processesComplete = 0
        numTasks = 2
        if targ.pokemonID == self.getUserPokemonID() or targ.pokemonID == self.getEnemyPokemonID(): ##if it is then we can assume
            lostHP = int(1/8 * targ.HP)
            if targ == self.userTrainer.team[str(self.userTrainer.active)]:
                self.app.HPUpdateUser(min(0,targ.hp-lostHP))
            else:
                self.app.HPUpdateEnemy(min(0,targ.hp-lostHP))
            self.app.runText(targ.name + ' was hurt by its burn!')
            targ.takeDamage(lostHP)
            if targ.fainted:
                return (numTasks,genFunc(self.EOTKO,targ))
            else:
                return numTasks
        else:
            return False

    def hurtByBadPoison(self,targ):
        print('start poison')
        self.app.processesComplete = 0
        q = serviceQueue()
        numTasks = 2
        if targ.pokemonID == self.getUserPokemonID() or targ.pokemonID == self.getEnemyPokemonID():
            try:
                self.badPoison[str(targ)] += 1/16
            except:
                self.badPoison[str(targ)] = 1/16
            lostHP = int(self.badPoison[str(targ+1)]*targ.stats[0])
            q.add(self.app.runText,targ.name + ' was hurt by poison!')
            if targ == self.userTrainer.team[str(self.userTrainer.active)]:
                q.add(self.app.HPUpdateUser,min(0,targ.hp-lostHP))
            else:
                q.add(self.app.HPUPdateEnemy,min(0,targ.hp-lostHP))
            q.add(targ.takeDamage,lostHP)
            self.executeTurn(q,False,True,True)
            if targ.fainted:
                return (numTasks,genFunc(self.EOTKO,targ))
            else:
                return numTasks
        else:
            return False
            

    def hurtByLeechSeed(self,targ):
        self.app.processesComplete = 0
        numTasks = 2
        if targ.pokemonID == self.getUserPokemonID() or targ.pokemonID == self.getEnemyPokemonID():
            lostHP = int(1/8*targ)
            if targ == self.userTrainer.team[str(self.userTrainer.active)]:
                self.app.HPUpdateUser(min(0,targ.hp-lostHP))
            else:
                self.app.HPUpdateEnemy(min(0,targ.hp-lostHP))
            self.app.runText(targ.name + "'s health was sapped by leech seed!")
            targ.takeDamage(lostHP)
            if targ.fainted:
                return (numTasks,genFunc(self.EOTKO,targ))

    def EOTKO(self,targ):
        self.app.processesComplete = 0
        numTasks = 2
        if self.userTrainer.team[str(self.userTrainer.active)] == targ:
            u = True
            j = ''
        else:
            u = False
            j = "Foe's "
        self.app.runText(j + targ.name + ' has fainted!')
        if u:
            self.app.userPokemonFaint()
        else:
            self.app.enemyPokemonFaint()
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
        ##       in form (numProcessesStarted, funcToBeExec'd)
        print('numtasks: '+str(numTasks))
        print(self.endOfTurnQueue.q)
        print(self.app.processesComplete)
        if i == 0:
            self.app.processesComplete = 0
        elif type(numTasks) == int: ##either a number of tasks
            print('Herro')
            if numTasks == self.app.processesComplete:
                self.app.processesComplete = 0
                print('hoi')
                numTasks = self.endOfTurnQueue.q[i]()
                if str(numTasks) == 'False':
                    self.removeList.append(self.endOfTurnQueue.q[i])
                k = genFunc(self.endOfTurn,i+1,numTasks)
                self.app.master.after(10,k)
            else:
                k = genFunc(self.endOfTurn,i+1,numTasks)
                self.app.master.after(10,k)
        elif type(numTasks) == tuple: ##or if suddenly another func must be called, (num,func)
            if numTasks[0] == self.app.processesComplete:
                numTasks = numTasks[1]()
                if type(numTasks) == int:
                    k = genFunc(self.endOfTurn,i+1,numTasks)
                elif type(numTasks) == list:
                    self.endOfTurnQueue.add(numTasks[1])
                    k = genFunc(self.endOfTurn,i+1,numTasks[0])
                else:
                    k = genFunc(self.endOfTurn,i,numTasks)
                self.app.master.after(10,k)
            else:
                k = genFunc(self.endOfTurn,i,numTasks)
                self.app.master.after(10,k)
        if i == len(self.endOfTurnQueue.q) and numTasks == self.app.processesComplete:
            for item in self.removeList:
                x = self.endOfTurnQueue.searchAndDestroy(item)
                if x == False:
                    print('CRAP THERES AN ERROR IN ENDOFTURN QUEUE')
                    print(item)
            print('execing fainted thing')
            self.sendInIfFainted()
            return

#############################################################
    ##these functions are run after a turn ends and after EOT to check to see if there are any fainted pokemon

    def sendInIfFainted(self):
        q = serviceQueue()
        if self.userTrainer.team[str(self.userTrainer.active)].fainted:
            q.add(self.app.EOTSwitchButtons)
            q.add(self.checkUserSwitch)
        elif self.enemyTrainer.team[str(self.enemyTrainer.active)].fainted:
            self.emergencyEnemySwitch = 0
            while True:
                self.emergencyEnemySwitch = (self.emergencyEnemySwitch+1)%6
                print(self.emergencyEnemySwitch)
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
        self.app.throwStartPokeball()
        k = genFunc(self.checkUserSwitch,1)
        self.app.master.after(50,k)

    def checkEnemySwitch(self,reset=0):
        self.app.taskFinished = False
        if not reset and self.emergencyEnemySwitch == '':
            self.app.master.after(50,checkEnemySwitch)
            return
        else:
            self.enemyTrainer.active = self.emergencyEnemySwitch
            self.emergencyEnemySwitch = ''
            self.app.master.after(200)
            self.app.taskFinished = False
            self.app.enemyPokemonSendOut()
            self.emergencyEnemySwitch = ''

#############################################################
        ##functions here are for damage

    def findDamage(self,user,target,move):
        combinedModifiers = self.combinedModifiers(user,target,move)
        if combinedModifiers[0] == 0:
            return (0,2)
        damage = int(int(((((2 * int(user.level))/5 + 2) * int(move.power) * user.stats[1]/target.stats[2])/50 + 2) * combinedModifiers[0]) * r.uniform(0.95,1.05)) + 1
        print(damage)
        return (damage,combinedModifiers[1])
    
    def combinedModifiers(self,user,target,move):
        ## In Pokemon, there are a lot of modifiers that we need to account for.
        ## These modifiers include type advantages, stat boosts/decreases (i.e.  attack x2, defense x0.5)
        ## and ability modifiers from abilities such as huge power.
        ## FINISH THIS
            ## Currently this does not take into account abilities
            ## It should check to see if the ability is a damage modifying ability
            ## If it is, the ability should be checked for the modifier and the appropriate modifier should be applied
        ## This returns data in the form (modifier,isSuperEffective)
        ## Modifier is a floating point number, isSuperEffective is a boolean though will be an integer (2) if no damage is dealt
        ##dependent on types
        Modifier = 1
        superEffective,notVeryEffective = False,False
        for Type in target.types:
            if move.type in immune[Type]:
                return (0,2)
            elif move.type in weakness[Type]:
                Modifier = Modifier * 2
                superEffective = True
            elif move.type in resistance[Type]:
                Modifier = Modifier * 2
                notVeryEffective = True
        if move.type in user.types:
            Modifier = Modifier * 1.5
        ##physical/special mods
        if move.category == 'Physical':
            Modifier = Modifier * stages[str(user.modifiers[1])] / stages[str(target.modifiers[2])]
        else:
            Modifier = Modifier * stages[str(user.modifiers[3])] / stages[str(target.modifiers[4])]

        return (Modifier,superEffective and not notVeryEffective)
        

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
        functions = {'Amnesia':self.amnesia,'Earthquake':self.earthquake,'Tackle' : self.tackle, 'Toxic' : self.toxic}
        moveSpecifier = {'Bullet Seed' : 'multihit'}#,'Earthquake':'regular','Growl' : 'regular','Tackle' : 'regular'}
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

    def statChange(self,arena,targ,stat,modifier):
        x = targ.changeModifier(stat,modifier)
        if x == 'ALLOK':
            if modifier > 0:
                h = 'rose'
            elif modifier < 0:
                h = 'fell'
            d = {1:'',2:' sharply',3:' drastically'}
            return arena.app.runText(targ.name + "'s " + stat + " " + h + d[modifier]+'!')
        else:
            if modifier > 0:
                h = 'higher'
            elif modifier < 0:
                h = 'lower'
            arena.app.runText("But " + targ.name + "'s " + stat + " can't go any " + h + "!")

    def activate(self):
        exec(self.function)
        
    ##FUNCTIONS FOR MOVE EXECUTION BELOW
    def amnesia(self,arena,user,targ):
        arena.app.taskFinished = False
        self.statChange(arena,user,'Special Defense',2)
        arena.app.taskFinished = True

    def tackle(self,arena,user,targ):
        arena.app.taskFinished = True

    def toxic(self,arena,user,targ):
        arena.app.taskFinished = False
        if targ.types[0].lower() != '1poison' and targ.types[1].lower() != '1poison' and targ.statusCondition == None:
            targ.statusCondition = 'poisoned'
            arena.app.runText(targ.name + ' was badly poisoned!')
            if targ == arena.enemyTrainer.team[str(arena.enemyTrainer.active)]:
                arena.app.setEnemyStatus()
            elif targ == arena.userTrainer.team[str(arena.userTrainer.active)]:
                arena.app.setUserStatus()
            arena.endOfTurnQueue.add(genFunc(arena.hurtByBadPoison,targ))
        else:
            arena.app.runText('But it had no effect!')
        arena.app.taskFinished = True
        
    def earthquake(self,arena,user,targ):
        aren.app.taskFinished = True




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
