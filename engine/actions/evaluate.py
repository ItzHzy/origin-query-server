def isLegal(game, action, **params):
    """Check if a given action and arguments are legal

    Args:
        game (Game): Game object
        action (function): The game action being checked
        params (dict): The other arguments for the game action

    Returns:
        Boolean: True if action is legal, false otherwise
    """
    for rule in game.rules:
        if not rule.isLegal(action, **params):
            return False

    return True


def isReplaced(game, action, **params):
    """Check if a given action and arguments will be replaced

    Args:
        game (Game): Game object
        action (function): The game action being checked
        params (dict): The other arguments for the game action

    Returns:
        Boolean: True if action is replaced, false otherwise
    """

    for replacement in game.replacements:
        if replacement.isActive:
            if replacement.getSource() not in alreadyReplaced:
                if replacement.isReplaced(action, **params):
                    return True

    return False


def evaluate(game, action, alreadyReplaced=[], **params):
    """Important method for the engine. Detailed in LexMagico.md

    Args:
        game (Game): Game object
        action (function): The game action being checked
        alreadyReplaced (list): Holds replacement effects already done, and 
            passed down recursively to other calls to evalute()
        params (dict): The other arguments for the game action

    Returns:
        None
    """

    try:
        for rule in game.rules:
            if not rule.isLegal(action, **params):
                # TODO: return more detailed exception
                raise Exception("Illegal Action")
    except Exception as error:
        print(error)

    else:
        replacementDone = False
        for replacement in game.replacements:
            if replacement.isActive:
                if replacement.getSource() not in alreadyReplaced:
                    if replacement.isReplaced(action, **params):
                        # TODO: implement ordering of replacement effects
                        replacementDone = True

                        # returns (newAction, newParams)
                        newAction = replacement.replace(action, **params)

                        evaluate(game, newAction[0], alreadyReplaced=alreadyReplaced.append(replacement.getSource()), **newAction[1])
                        break

        if not replacementDone:
            # Resolve action
            action(game, **params)

            if action in game.trackers:
                for tracker in game.trackers[action]:
                    # TODO: implement tracker logic
                    tracker.run()

            if action in game.triggers:
                for trigger in game.triggers[action]:
                    if trigger.isActive:
                        if trigger.triggers(action, **params):
                            trigger.getSource().controller.awaitingTriggers.append(trigger.trigger(action, **params))

    return None
