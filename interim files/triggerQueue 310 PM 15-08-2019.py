class eventsQueue: ## This is going to be used to store the triggers that need to processed each turn.
    def __init__(self,size,arena,EOTQueue=True):
        ## format: [['cause','function'],['cause','function']]
        self.events = []
        self.arena = arena
        if EOTQueue:
            self.events = [['self.arena.weather==None',None]] ## by default, reserve space 0 for weather

    def addTrigger(self,cause,function):
        self.events.append([cause,function])
        ## Trigger types:
        ## 't1pkmn=xyz'
        ## 't2pkmn=xyz'
        ## 'weather=None/Rainy/Cloudy/Etc,'
        ##
        ## Function standards:
        ## tXpkmn: function(self,whichPokemonIsIt,<otherArgs>). The desired function should be passed as a string
        ##         into the trigger.

    def evalTriggers(self):
        count = 0
        tempEvents = tuple(self.events)
        for trigger in tempEvents:
            if 'weather' in trigger[0]:
                if 'Rainy' in trigger[0]:
                    self.arena.rainyWeather()
                elif 'Sandstorm' in trigger[0]:
                    self.arena.sandstormWeather()
                elif 'Sunny' in trigger[0]:
                    self.arena.sunnyWeather()
                elif 'Snowy' in trigger[0]:
                    self.arena.snowyWeather()
            elif 'pkmn' in trigger[0]:
                if eval(trigger[0]):
                    exec(trigger[1])
                else:
                    del self.events[count]
                    count -= 1
            count += 1

        
