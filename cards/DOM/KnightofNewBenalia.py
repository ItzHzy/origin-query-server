from enumeratedTypes import *
from combatFunctions import *
from gameElements import *
from gameActions import *


class KnightofNewBenalia(Card):
    def __init__(self, game, player, key):
        super(KnightofNewBenalia, self).__init__(game, player, key)

        self.manaCost = {ManaType.WHITE: 1, ManaType.GENERIC: 1}

        self.characteristics[Layer.BASE] = ("Knight of New Benalia", 3, 1, [], {
                                            Type.CREATURE, Subtype.HUMAN, Subtype.KNIGHT}, {Color.WHITE})

        self.updateCharacteristics()
