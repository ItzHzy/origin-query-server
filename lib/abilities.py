from uuid import uuid1

class Ability():
    def __init__(self, game, source, allowedZones, isManaAbility, keywordName):
        self.source = source
        self.keywordName = keywordName
        self.abilityID = 'A-' + str(uuid1())
        self.isManaAbility = isManaAbility
        self.allowedZones = allowedZones
        self.specialTypes = set() # Ex. Variable

    def getAllowedZones(self):
        return self.allowedZones

    def isKeyword(self):
        if self.keywordName is None:
            return False
        return self.keywordName


class ActivatedAbility(Ability):
    def __init__(self, game, source, cost, effect, allowedZones, isManaAbility=False, keywordName=None):
        super(ActivatedAbility, self).__init__(game, source, allowedZones, isManaAbility, keywordName)
        self.cost = cost # cost[0] is a mana cost, cost[1] is for other costs
        self.effect = effect
        self.rulesText = effect.rulesText
        self.isActive = False 

    def getCost(self):
        return self.cost

    def getEffect(self):
        return self.effect


class TriggeredAbility(Ability):
    # argDict {1: None, 
    #          3: self }
    #   check the arg at index in the evaluated function and see if its equal to the value 
    def __init__(self, game, source, triggerFunction, argDict, effect, allowedZones, isManaAbility=False, keywordName=None):
        super(TriggeredAbility, self).__init__(game, source, allowedZones, isManaAbility, keywordName)
        self.triggerFunction = triggerFunction
        self.rulesText = effect.rulesText
        self.argDict = argDict
        self.effect = effect
        self.isActive = False