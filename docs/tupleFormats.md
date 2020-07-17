card.effects = ["rules text", [
                [action1, arg1, targetRes1],
                [action2, arg2, targetRes2, arg3]
                ]]

card.mainCosts = [types  ex. "Flashback", cost, indexOfEffect usually 0]

card.additionalCosts = [types ex "Kicker", cost, indexOfEffect usually not 0]

"cost" =    (True, (mana)) 
            or 
            (False, ((action1, TargetRestriction1), 
            (action2, TargetRestriction2), 
            ...))

msg = {
        "type": "State Update",
        "data": {
            "cards": [{
                "instanceID": card.instanceID,
                "type": "New Object",
                "data": {...}
            }],
            "players": [{
                "playerID": control.playerID,
                "type": "Zone Count Update",
                "data": {...}
            }]
        }
    }