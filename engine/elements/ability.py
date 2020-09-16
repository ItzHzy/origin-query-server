from uuid import uuid1

from consts.zone import Zone


class Ability():
    """Base class for all abilites.

    Attributes:
        game (Game): Game object associated with this ability.
        source (str): InstanceID of the card this ability originates from.
        rulesText (str): Oracle text of this ability
        allowedZones (set(Zone)): Zones where the source needs to be in order to use this ability.
        isManaAbility (bool): Whether or not this ability is a mana ability.
        keyword (Keyword or None): Is set if the ability is a keyword.
        isActive (bool): Whether or not this ability is active.
    """

    def __init__(self, game, source, rulesText, allowedZones, isManaAbility, keyword):
        self.game = game
        self.source = source
        self.rulesText = rulesText
        self.keyword = keyword
        self.abilityID = 'A-' + str(uuid1())
        self.isManaAbility = isManaAbility
        self.allowedZones = allowedZones

        self.isActive = False
        game.GAT[self.abilityID] = self

    def getSource(self):
        return self.game.allCards[self.source]


class ActivatedAbility(Ability):
    """Class for activated abilites.

    Attributes

    """

    def __init__(self, game, source, rulesText, cost, effect, allowedZones={Zone.FIELD}, isManaAbility=False, keyword=None):
        super(ActivatedAbility, self).__init__(game, source, rulesText, allowedZones, isManaAbility, keyword)
        self.cost = cost
        self.effect = effect


class TriggeredAbility(Ability):
    """
    """

    def __init__(self, game, source, rulesText, action, triggerFunc, effect, interveningIf=None, allowedZones={Zone.FIELD}, isManaAbility=False, keyword=None):
        super(TriggeredAbility, self).__init__(game, source, rulesText, allowedZones, isManaAbility, keyword)
        self.action = action
        self.triggerFunc = triggerFunc
        self.effect = effect
        self.interveningIf = interveningIf

        if action.__name__ in game.triggers:
            game.triggers[action].append(self)
        else:
            game.triggers[action] = [self]

    def triggers(self, action, **params):
        """Determines if the action being taken will trigger this ability

        Args: 
            action (function): Action being taken
            params (dict): Parameters for the above action

        Returns:
            Bool: True if action will trigger this ability, False otherwise
        """
        if self.triggerFunc(action, **params):
            if self.interveningIf and self.interveningIf(action, **params):
                return True
        return False

    def trigger(self, action, **params):
        """Returns 
        """
        pass


class RuleAbility():
    pass


class CostChangeAbility():
    pass
