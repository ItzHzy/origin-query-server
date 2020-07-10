import dataset

db = dataset.connect('sqlite:///assets//db.db')

cards_db = db['cards']

def getCardPath(oracle_id):
    cards_db.find_one(oracle_id=oracle_id)['filepath']