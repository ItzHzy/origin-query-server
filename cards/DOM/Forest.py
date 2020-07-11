from enumeratedTypes import * 
from combatFunctions import * 
from gameElements import * 
from gameActions import * 
from abilities import * 

class Forest(Card):
    def __init__(self, game, player, key):
        super(Forest, self).__init__(game, player, key)

        c1 = (False, ((tap, self)))

        e1 = Effect(self)
        e1.effect = [[addMana, self.controller, Color.GREEN, 1]]
        e1.rulesText = "T: Add G."

        a1 = ActivatedAbility(game, c1, e1, {Zone.FIELD}, True)

        self.characteristics[Layer.BASE] = ("Forest", 0, 0, [a1], {Supertype.BASIC, Type.LAND, Subtype.FOREST}, {Color.COLORLESS})

        self.updateCharacteristics()