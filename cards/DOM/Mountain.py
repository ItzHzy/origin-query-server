from enumeratedTypes import * 
from combatFunctions import * 
from gameElements import * 
from gameActions import * 
from abilities import * 

class Mountain(Card):
    def __init__(self, game, player):
        super().__init__(self, game, player)

        c1 = (False, ((tap, self)))

        e1 = Effect(self)
        e1.effect = [[addMana, self.controller, Color.RED, 1]]
        e1.rulesText = "T: Add R."

        a1 = ActivatedAbility(game, c1, e1, set(Zone.FIELD), True)

        self.characteristics[Layer.BASE] = ("Mountain", 0, 0, [a1], set(Supertype.BASIC, Type.LAND, Subtype.MOUNTAIN), set(Color.COLORLESS))

        self.updateCharacteristics()