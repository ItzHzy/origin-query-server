from enumeratedTypes import * 
from combatFunctions import * 
from gameElements import * 
from gameActions import * 
from abilities import * 

class Abrade(Card):
    def __init__(self, game, player):
        super().__init__(self, game, player) 

        self.characteristics[Layer.BASE] = ("Abrade", None, None, [], set(Type.INSTANT), set(Color.RED))
        self.isModal = True
        self.maxNumOfChoices = 1

        t1 = TargetRestriction(game, "Target creature")
        t1.cardTypes.append(Type.CREATURE)

        t2 = TargetRestriction(game, "Target artifact")
        t2.cardTypes.append(Type.ARTIFACT)

        self.effects.append([
            ["Abrade deals 3 damage to target creature.", 
                [[dealNonCombatDamage, self, t1, 3]]
                    ],
            ["Destroy target artifact.", 
                [[destroy, self, t2]]
                    ]])

        self.updateCharacteristics()
