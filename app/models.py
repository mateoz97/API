class Product:

    def __init__(self, id, name, quantity, price):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price

    @staticmethod
    def from_db(row):
        return Product(row[0], row[1], row[2], row[3])

class Departaments:
    
    def __init__(self, departament_id, departament_name):
        self.departament_id = departament_id
        self.departament_name = departament_name

    @staticmethod
    def from_db(row):
        return Departaments(row[0], row[1])


class Jobs:
    
    def __init__(self, job_id, job_name):
        self.job_id = job_id
        self.job_name = job_name

    @staticmethod
    def from_db(row):
        return Jobs(row[0], row[1])


class HiredEmployed:
    
    def __init__(self, id, employee_name, date_hired, departament_id, job_id):
        self.id = id
        self.employee_name = employee_name
        self.date_hired = date_hired
        self.departament_id = departament_id
        self.job_id = job_id

    @staticmethod
    def from_db(row):
        return HiredEmployed(
            id=row[0],
            employee_name=row[1],
            date_hired=row[2],
            departament_id=row[3],
            job_id=row[4]
        )