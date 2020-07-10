from enumeratedTypes import * 
from combatFunctions import * 
from gameElements import * 
from gameActions import * 
from abilities import * 

class Forest(Card):
    def __init__(self, game, player):
        super().__init__(self, game, player)

        c1 = (False, ((tap, self)))

        e1 = Effect(self)
        e1.effect = [[addMana, self.controller, Color.GREEN, 1]]
        e1.rulesText = "T: Add G."

        a1 = ActivatedAbility(game, c1, e1, set(Zone.FIELD), True)

        self.characteristics[Layer.BASE] = ("Forest", 0, 0, [a1], set(Supertype.BASIC, Type.LAND, Subtype.FOREST), set(Color.COLORLESS))

        self.updateCharacteristics()