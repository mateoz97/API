class Product:
    def __init__(self, id, name, quantity, price):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price

    @staticmethod
    def from_db(row):
        return Product(row[0], row[1], row[2], row[3])
