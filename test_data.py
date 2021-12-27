
class Product:
    def __init__(self, product_id, product_name, brand_id, category_id, model_year, list_price):
        self.product_id = product_id
        self.product_name = product_name
        self.brand = self.brand_from_id(brand_id)
        self.category = self.category_from_id(category_id)
        self.model_year = model_year
        self.list_price = list_price

    def brand_from_id(self, brand_id):
        brands = ['None',
                  'Electra',
                  'Haro',
                  'Heller',
                  'Pure Cycles',
                  'Cross',
                  'Strider',
                  'Sun Bicycles',
                  'Surly',
                  'Trek']
        return brands[int(brand_id)]

    def category_from_id(self, category_id):
        categories = ['None',
                      'Children Bicycles',
                      'Comfort Bicycles',
                      'Cruisers Bicycles',
                      'Cyclocross Bicycles',
                      'Electric Bikes',
                      'Mountain Bikes',
                      'Road Bikes']
        return categories[int(category_id)]

    def __str__(self):
        return f'{self.product_id}, {self.product_name}, {self.brand}, {self.category}, {self.model_year}, {self.list_price}'


prod_file_lines = []
with open('data_prod.txt') as f:
    prod_file_lines = f.readlines()

prods = []
for line in prod_file_lines:
    elems = line[:-2].split(',')
    prods.append(Product(elems[0], elems[1], elems[2], elems[3], elems[4], elems[5]))

for prod in prods:
    print(prod)


class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self.order_list = []

    def __str__(self):
        ret = ''
        if len(self.order_list) > 0:
            ret = prods[self.order_list[0]-1].product_name
        return f'order_list: {ret}'

order_file_lines = []
with open('data_orders.txt') as f:
    order_file_lines = f.readlines()

orders = [Order(i) for i in range(1, 1617)]
for line in order_file_lines:
    elems = line[:-2].split(',')
    print(int(elems[0]))
    for i in range(int(elems[3])):
        orders[int(elems[0])].order_list.append(int(elems[2]))

for order in orders:
    print(order)
