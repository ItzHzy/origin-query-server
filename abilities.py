class Ability():
    def __init__(self, game, allowedZones, isManaAbility, keywordName):

        self.keywordName = keywordName
        self.abilityID = game.getNewAbilityID()
        self.manaAbility = isManaAbility
        self.allowedZones = allowedZones

    def isManaAbility(self):
        return self.manaAbility

    def getAllowedZones(self):
        return self.allowedZones

    def isKeyword(self):
        if self.keywordName is None:
            return False
        return self.keywordName


class ActivatedAbility(Ability):
    def __init__(self, game, cost, effect, allowedZones, isManaAbility=False, keywordName=None):
        super().__init__(self, game, allowedZones, isManaAbility, keywordName)
        self.cost = cost
        self.effect = effect
        self.isActive = False 

    def getCost(self):
        return self.cost

    def getEffect(self):
        return self.effect


class TriggeredAbility(Ability):
    # argDict {1: None, 
    #          3: self }
    #   check the arg at index in the evaluated function and see if its equal to the value 
    def __init__(self, game, triggerFunction, argDict, effect, allowedZones, isManaAbility=False, keywordName=None):
        super().__init__(game, allowedZones, isManaAbility, keywordName)
        self.triggerFunction = triggerFunction
        self.argDict = argDict
        self.effect = effect
        self.isActive = False