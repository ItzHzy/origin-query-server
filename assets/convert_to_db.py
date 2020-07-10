import dataset
import json

with open('.\\assets\dominaria.json') as fp: 
    cards = json.load(fp) 

db = dataset.connect('sqlite:///assets//db.db')

cards_db = db['cards']

for card in cards:
    oracle_id = card['oracle_id']
    name = card['name']
    fname =  '.\\cards\\' + card['set'].upper() + '\\' + name.replace('\'', '').replace('-', '').replace(' ', '').replace(',', '')
    cards_db.insert(dict(oracle_id=oracle_id, filepath=fname))

print(cards_db.find_one(oracle_id='b2c6aa39-2d2a-459c-a555-fb48ba993373'))