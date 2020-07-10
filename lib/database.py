import dataset

db = dataset.connect('sqlite:///assets//db.db')

cards_db = db['cards']
