from enumeratedTypes import *
import json
import asyncio
import functools
from server1 import sio

# TODO: Add indexing options for deck


def commandToField(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.COMMAND_ZONE]
    newZone = game.zones[control][Zone.FIELD]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def commandToHand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.COMMAND_ZONE]
    newZone = game.zones[own][Zone.HAND]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def commandToStack(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.COMMAND_ZONE]
    newZone = game.zones[control][Zone.STACK]

    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)


def graveToField(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[control][Zone.FIELD]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def graveToHand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[own][Zone.HAND]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def graveToStack(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[control][Zone.STACK]

    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)


def graveToDeck(game, card, indexToInsert):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[own][Zone.DECK]

    card.reset()
    oldZone.remove(card)
    newZone.insert(indexToInsert, card)
    game.applyModifiers(card)


def graveToExile(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[control][Zone.EXILE]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def addToField(game, card):
    newZone = game.zones[card.controller][Zone.FIELD]
    newZone.add(card)
    game.applyModifiers(card)


def fieldToField(game, card, player):
    control = card.controller
    oldZone = card.currentZone
    newZone = game.zones[control][Zone.HAND]

    oldZone.remove(card)
    newZone.add(card)


def fieldToHand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.HAND]

    oldZone.remove(card)
    if not card.isToken:

        card.reset()
        newZone.add(card)
        game.applyModifiers(card)


def fieldToGrave(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.GRAVE]

    oldZone.remove(card)
    if not card.isToken:

        card.reset()
        newZone.add(card)
        game.applyModifiers(card)


def fieldToDeck(game, card, indexToInsert):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.HAND]

    oldZone.remove(card)
    if not card.isToken:

        card.reset()
        newZone.insert(indexToInsert, card)
        game.applyModifiers(card)


def fieldToExile(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[control][Zone.EXILE]

    oldZone.remove(card)
    if not card.isToken:

        card.reset()
        newZone.add(card)
        game.applyModifiers(card)


def fieldToCommand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.COMMAND_ZONE]

    oldZone.remove(card)
    if not card.isToken:

        card.reset()
        newZone.add(card)
        game.applyModifiers(card)


def handToField(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[control][Zone.FIELD]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

    abilities = [[ability.abilityID, ability.rulesText]
                 for ability in card.abilities if (Zone.FIELD in ability.allowedZones)]
    types = [str(typ) for typ in card.cardTypes]

    msg1 = {
        "instanceID": card.instanceID,
        "name": card.name,
        "oracle": card.oracle,
        "memID": card.memID,
        "power": card.power,
        "toughness": card.toughness,
        "controller": card.controller.playerID,
        "abilities": abilities,
        "types": types,
        "zone": "field"
    }

    msg2 = {
        "playerID": control.playerID,
        "type": "Hand",
        "num": len(oldZone)
    }

    game.notifyAll("New Object", msg1)
    game.notifyAll("Zone Count Update", msg2)


def handToStack(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[control][Zone.STACK]

    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)


def handToGrave(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[own][Zone.GRAVE]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def handToDeck(game, card, indexToInsert):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[own][Zone.DECK]

    card.reset()
    oldZone.remove(card)
    newZone.insert(indexToInsert, card)
    game.applyModifiers(card)


def handToExile(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[control][Zone.EXILE]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def deckToField(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[control][Zone.FIELD]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def deckToHand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[own][Zone.HAND]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

    abilities = [[ability.abilityID, ability.rulesText]
                 for ability in card.abilities if (Zone.HAND in ability.allowedZones)]
    types = [str(typ) for typ in card.cardTypes]

    msg1 = {
        "playerID": control.playerID,
        "type": "Hand",
        "num": len(newZone)
    }

    msg2 = {
        "playerID": control.playerID,
        "type": "Deck",
        "num": len(oldZone)
    }

    msg3 = {
        "instanceID": card.instanceID,
        "name": card.name,
        "oracle": card.oracle,
        "memID": card.memID,
        "power": card.power,
        "toughness": card.toughness,
        "controller": card.controller.playerID,
        "abilities": abilities,
        "types": types,
        "zone": "hand"
    }

    game.notifyAll("Zone Count Update", msg1)
    game.notifyAll("Zone Count Update", msg2)
    game.notify("New Object", msg3, control)


def deckToStack(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[control][Zone.STACK]

    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)


def deckToGrave(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[own][Zone.GRAVE]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def deckToExile(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[control][Zone.EXILE]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def addToStack(game, card):
    newZone = game.zones[card.controller][Zone.STACK]
    newZone.insert(0, card)
    game.applyModifiers(card)


def stackToField(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[control][Zone.FIELD]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)


def stackToHand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.HAND]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)


def stackToGrave(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.GRAVE]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)


def stackToDeck(game, card, indexToInsert):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.DECK]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.insert(indexToInsert, card)
        game.applyModifiers(card)


def stackToExile(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[control][Zone.EXILE]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)


def stackToCommand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.COMMAND_ZONE]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)


def exileToField(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.EXILE]
    newZone = game.zones[control][Zone.FIELD]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def exileToHand(game, card):
    control = card.controller
    own = card.owner
    oldZone = game.zones[control][Zone.EXILE]
    newZone = game.zones[own][Zone.HAND]

    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)


def exileToStack(game, card):
    control = card.controller
    oldZone = game.zones[control][Zone.EXILE]
    newZone = game.zones[control][Zone.STACK]

    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)
