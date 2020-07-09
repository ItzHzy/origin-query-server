from enumeratedTypes import *
from combatFunctions import * 
from gameElements import * 
from gameActions import * 
from abilities import * 

class Plains(Card):
    def __init__(self, game, player):
        super().__init__(self, game, player)

        c1 = (False, ((tap, self)))

        e1 = Effect(self)
        e1.effect = [[addMana, self.controller, Color.WHITE, 1]]
        e1.rulesText = "T: Add W."

        a1 = ActivatedAbility(game, c1, e1, set(Zone.FIELD), True)

        self.characteristics[Layer.BASE] = ("Plains", 0, 0, [a1], set(Supertype.BASIC, Type.LAND, Subtype.PLAINS), set(Color.COLORLESS))

        self.updateCharacteristics()