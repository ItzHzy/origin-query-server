import dataset

db = dataset.connect('sqlite:///assets//db.db')

cards_db = db['cards']

cards_db.insert(dict(name='John Doe', age=46, country='China'))