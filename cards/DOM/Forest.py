from enumeratedTypes import * 
from combatFunctions import * 
from gameElements import * 
from gameActions import *

class Forest(Card):
    def __init__(self, game, player, key):
        super(Forest, self).__init__(game, player, key)

        c1 = [{}, [[tap, self]]]

        e1 = [[addMana, self.controller, Color.GREEN, 1]]
        
        r1 = f"{{T}}: Add {{G}}."

        a1 = ActivatedAbility(game, self, c1, e1, {Zone.FIELD}, r1, True)

        self.characteristics[Layer.BASE] = ("Forest", 0, 0, [a1], {Supertype.BASIC, Type.LAND, Subtype.FOREST}, {Color.COLORLESS})

        self.updateCharacteristics()