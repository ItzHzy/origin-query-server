from gameElements import *
from combatFunctions import *
from gameActions import *
from enumeratedTypes import *


class Island(Card):
    def __init__(self, game, player, key):
        super(Island, self).__init__(game, player, key)

        # AA: {T}: Add {U}

        # C: {T}
        c1 = ({}, [[tap, self]])
        # End

        # E: Add {U}
        e1 = [
            [addMana, self.controller, Color.BLUE, 1]
        ]
        # End

        r1 = f"{{T}}: Add {{U}}."
        a1 = ActivatedAbility(game, self, r1, c1, e1, allowedZones={Zone.FIELD}, isManaAbility=True)
        # End

        self.printed = {
            "name": "Island",
            "power": 0,
            "toughness": 0,
            "abilities": [a1],
            "types": {Supertype.BASIC, Type.LAND, Subtype.ISLAND},
            "colors": {Color.COLORLESS}
        }

        self.update()
