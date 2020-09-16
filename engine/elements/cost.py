import asyncio

from actions.evaluate import evaluate
from actions.mana import removeMana
from consts.color import Color
from consts.mana import ManaType


class Cost():
    # Only instantiated by addCosts()

    def __init__(self):
        self.manaCost = {}
        self.additional = []

    def canBePaid(self, game, player):
        # Returns True if the cost can be paid by player, False otherwise
        # TODO: implement canBePaid
        return True

    async def pay(self, game, player):

        convertStringToColorEnum = {
            "Color.WHITE": Color.WHITE,
            "Color.BLUE": Color.BLUE,
            "Color.BLACK": Color.BLACK,
            "Color.RED": Color.RED,
            "Color.GREEN": Color.GREEN,
            "Color.COLORLESS": Color.COLORLESS
        }

        if self.manaCost != {}:
            while True:
                player.answer = None

                game.notify("Pay Mana", {
                    "gameID": game.gameID,
                    "status": "PAYING_MANA",
                    "cost": {
                        "ManaType.GENERIC": self.manaCost[ManaType.GENERIC] if ManaType.GENERIC in self.manaCost else 0,
                        "ManaType.WHITE": self.manaCost[ManaType.WHITE] if ManaType.WHITE in self.manaCost else 0,
                        "ManaType.BLUE": self.manaCost[ManaType.BLUE] if ManaType.BLUE in self.manaCost else 0,
                        "ManaType.BLACK": self.manaCost[ManaType.BLACK] if ManaType.BLACK in self.manaCost else 0,
                        "ManaType.RED": self.manaCost[ManaType.RED] if ManaType.RED in self.manaCost else 0,
                        "ManaType.GREEN": self.manaCost[ManaType.GREEN] if ManaType.GREEN in self.manaCost else 0,
                        "ManaType.COLORLESS": self.manaCost[ManaType.COLORLESS] if ManaType.COLORLESS in self.manaCost else 0,
                    }
                }, player)

                while player.answer == None:
                    await asyncio.sleep(0)

                # TODO: implement validation of payment

                for color in player.answer:
                    if player.answer[color] > 0:
                        evaluate(game, removeMana, player, convertStringToColorEnum[color], player.answer[color])

                break

        if self.additional != []:
            for cost in self.additional:
                evaluate(game, **cost)

        return True


def addCosts(game, obj, mainCost, additionalCosts):
    """Used to add up all costs and discounts for a spell or ability

    Args:
        game(Game): Game Object
        obj(Card or Ability): The card or ability being paid
        mainCost(List): List of the forms:
            [True, [mana]] 
            or 
            [False, [[action1, arg11], 
            [action2, arg2], 
            ...]] 
        additionalCosts(List(List)): Lists of the same form as mainCost

    Returns:
        totalCost(Cost): The combined costs and discounts of everything 
    """
    totalCost = Cost()
    totalMana = {}

    if isinstance(mainCost, dict):
        for manaType in mainCost:
            amount = mainCost[manaType]

            if manaType in totalMana:
                totalMana[manaType] += amount
            else:
                totalMana[manaType] = amount

            # If the amount of a manatype is 0 or negative, it is unneeded and can be removed from the list
            if totalMana[manaType] <= 0:
                del totalMana[manaType]
    else:
        for cost in mainCost:
            totalCost.additional.append(cost)

    if additionalCosts != []:
        for addedCost in additionalCosts:
            if not 'action' in addedCost:  # Do if the additional cost is a mana payment
                for manaType in addedCost:
                    amount = mainCost[manaType]

                    if manaType in totalMana:
                        totalMana[manaType] += amount
                    else:
                        totalMana[manaType] = amount

                    # If the amount of a manatype is 0 or negative, it is unneeded and can be removed from the list
                    if totalMana[manaType] <= 0:
                        del totalMana[manaType]
            else:
                totalCost.additional.append(addedCost)

    totalCost.manaCost = totalMana

    return totalCost
