from lib.enumeratedTypes import * # pylint: disable=unused-wildcard-import
from lib.combatFunctions import * # pylint: disable=unused-wildcard-import
from lib.gameElements import * # pylint: disable=unused-wildcard-import
from lib.gameActions import * # pylint: disable=unused-wildcard-import
from lib.abilities import * # pylint: disable=unused-wildcard-import

class BedlamReveler(Card):
    def __init__(self, game, player):
        super().__init__(self, game, player)

        game.addKeywordAbility(Keyword.PROWESS)

        e1 = Effect(self)
        e1.effect = [[discardHand, self.controller], [drawCards, self.controller, 3]]
        e1.rulesText = "When Bedlam Reveler enters the battlefield, discard your hand, then draw three cards."

        a1 = TriggeredAbility(game, etb, {3: self}, e1, set(Zone.FIELD))
        
        self.characteristics[Layer.BASE] = ("Bedlam Reveler", 3, 4, [Keyword.PROWESS, a1], set(Type.CREATURE, Subtype.DEVIL, Subtype.HORROR), set(Color.RED))

        self.updateCharacteristics()