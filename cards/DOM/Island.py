from enumeratedTypes import * 
from combatFunctions import * 
from gameElements import * 
from gameActions import *

class Island(Card):
    def __init__(self, game, player, key):
        super(Island, self).__init__(game, player, key)

        c1 = [{}, [[tap, self]]]

        e1 = [[addMana, self.controller, Color.BLUE, 1]]
        
        r1 = f"{{T}}: Add {{U}}."

        a1 = ActivatedAbility(game, self, c1, e1, {Zone.FIELD}, r1, True)

        self.characteristics[Layer.BASE] = ("Island", 0, 0, [a1], {Supertype.BASIC, Type.LAND, Subtype.ISLAND}, {Color.COLORLESS})

        self.updateCharacteristics()