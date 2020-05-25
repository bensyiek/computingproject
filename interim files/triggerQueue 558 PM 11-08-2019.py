class trigger: ## This is going to be used to store the triggers that need to processed each turn.
    def __init__(self,size,arena):
        ## format: [['cause','function'],['cause','function']]
        self.events = [['weather=None',None]]
        self.arena = arena

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
        for trigger in self.events:
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
                exec(trigger[1])

            
