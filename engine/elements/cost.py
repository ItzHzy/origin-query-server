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
                        gameActions.evaluate(
                            game, gameActions.removeMana, player, convertStringToColorEnum[color], player.answer[color])

                break

        if self.additional != []:
            for cost in self.additional:
                gameActions.evaluate(game, **cost)

        return True
