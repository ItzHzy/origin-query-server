from enumeratedTypes import *  # pylint: disable=unused-wildcard-import
from gameElements import * # pylint: disable=unused-wildcard-import

# TODO: Add indexing options for deck 
def commandToField(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.COMMAND_ZONE]
    newZone = game.zones[control][Zone.FIELD]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def commandToHand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.COMMAND_ZONE]
    newZone = game.zones[own][Zone.HAND]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def commandToStack(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.COMMAND_ZONE]
    newZone = game.zones[control][Zone.STACK]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)

def graveToField(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[control][Zone.FIELD]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def graveToHand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[own][Zone.HAND]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)
    
def graveToStack(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[control][Zone.STACK]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)

def graveToDeck(game, card, indexToInsert):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[own][Zone.DECK]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.insert(indexToInsert, card)
    game.applyModifiers(card)

def graveToExile(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.GRAVE]
    newZone = game.zones[control][Zone.EXILE]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def addToField(game, card):
    newZone = game.zones[card.getController()][Zone.FIELD]
    newZone.add(card)
    game.applyModifiers(card)

def fieldToField(game, card, player):
    control = card.getController()
    oldZone = card.currentZone
    newZone = game.zones[control][Zone.HAND]
    
    oldZone.remove(card)
    newZone.add(card)

def fieldToHand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.HAND]

    oldZone.remove(card)
    if not card.isToken:
        card.clearProperties()
        card.reset()
        newZone.add(card)
        game.applyModifiers(card)

def fieldToGrave(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.GRAVE]

    oldZone.remove(card)
    if not card.isToken:
        card.clearProperties()
        card.reset()
        newZone.add(card)
        game.applyModifiers(card)

def fieldToDeck(game, card, indexToInsert):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.HAND]

    oldZone.remove(card)
    if not card.isToken:
        card.clearProperties()
        card.reset()
        newZone.insert(indexToInsert, card)
        game.applyModifiers(card)

def fieldToExile(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[control][Zone.EXILE]

    oldZone.remove(card)
    if not card.isToken:
        card.clearProperties()
        card.reset()
        newZone.add(card)
        game.applyModifiers(card)

def fieldToCommand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.FIELD]
    newZone = game.zones[own][Zone.COMMAND_ZONE]

    oldZone.remove(card)
    if not card.isToken:
        card.clearProperties()
        card.reset()
        newZone.add(card)
        game.applyModifiers(card)

def handToField(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[control][Zone.FIELD]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def handToStack(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[control][Zone.STACK]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)

def handToGrave(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[own][Zone.GRAVE]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def handToDeck(game, card, indexToInsert):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[own][Zone.DECK]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.insert(indexToInsert, card)
    game.applyModifiers(card)

def handToExile(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.HAND]
    newZone = game.zones[control][Zone.EXILE]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def deckToField(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[control][Zone.FIELD]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def deckToHand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[own][Zone.HAND]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def deckToStack(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[control][Zone.STACK]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)

def deckToGrave(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[own][Zone.GRAVE]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def deckToExile(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.DECK]
    newZone = game.zones[control][Zone.EXILE]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def addToStack(game, card):
    newZone = game.zones[card.getController()][Zone.STACK]
    newZone.insert(0, card)
    game.applyModifiers(card)
        
def stackToField(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[control][Zone.FIELD]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)

def stackToHand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.HAND]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)

def stackToGrave(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.GRAVE]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)

def stackToDeck(game, card, indexToInsert):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.DECK]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.insert(indexToInsert, card)
        game.applyModifiers(card)

def stackToExile(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[control][Zone.EXILE]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)

def stackToCommand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.STACK]
    newZone = game.zones[own][Zone.COMMAND_ZONE]

    oldZone.remove(card)
    if not card.isCopy:
        newZone.add(card)
        game.applyModifiers(card)

def exileToField(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.EXILE]
    newZone = game.zones[control][Zone.FIELD]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def exileToHand(game, card):
    control = card.getController()
    own = card.getOwner()
    oldZone = game.zones[control][Zone.EXILE]
    newZone = game.zones[own][Zone.HAND]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.add(card)
    game.applyModifiers(card)

def exileToStack(game, card):
    control = card.getController()
    oldZone = game.zones[control][Zone.EXILE]
    newZone = game.zones[control][Zone.STACK]

    card.clearProperties()
    card.reset()
    oldZone.remove(card)
    newZone.insert(0, card)
    game.applyModifiers(card)