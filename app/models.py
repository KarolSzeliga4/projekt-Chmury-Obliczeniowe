from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

graph = App("neo4j+s://23338107.databases.neo4j.io", "neo4j", "324fTDRNLQgb7NsY1M3iYH2Bl7i-zG2bKIerNjDz_IE")


class Product:
    def __init__(self, product_id=0, product_name='none', brand_id=0, category_id=0, model_year=0, list_price=0):
        self.product_id = product_id
        self.product_name = product_name
        self.brands = ['-',
                  'Electra',
                  'Haro',
                  'Heller',
                  'Pure Cycles',
                  'Cross',
                  'Strider',
                  'Sun Bicycles',
                  'Surly',
                  'Trek']
        self.categories = ['-',
                      'Children Bicycles',
                      'Comfort Bicycles',
                      'Cruisers Bicycles',
                      'Cyclocross Bicycles',
                      'Electric Bikes',
                      'Mountain Bikes',
                      'Road Bikes']
        self.brand = self.brand_from_id(brand_id)
        self.category = self.category_from_id(category_id)
        self.model_year = model_year
        self.list_price = list_price

    def brand_from_id(self, brand_id):
        return self.brands[int(brand_id)]

    def category_from_id(self, category_id):
        return self.categories[int(category_id)]

    def __str__(self):
        return f'{self.product_id}, {self.product_name}, {self.brand}, {self.category}, {self.model_year}, {self.list_price}'


def execute(query):
    with graph.driver.session() as session:
        result = session.read_transaction(execute_query, query)
        return result


def execute_query(tx, query):
    result = tx.run(query)
    return [row for row in result]


def execute_get_product(query, product_id):
    with graph.driver.session() as session:
        result = session.read_transaction(execute_query_get_product, query, str(product_id))
        return result


def execute_query_get_product(tx, query, product_id):
    result = tx.run(query, product_id=product_id)
    return [row for row in result]


def execute_write_product(query, product):
    with graph.driver.session() as session:
        result = session.write_transaction(execute_write_product_query, query, product)
        return result


def execute_write_product_query(tx, query, product):
    # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
    # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
    result = tx.run(query,
                    product_id=product.product_id, product_name=product.product_name,
                    brand=product.brand, category=product.category,
                    model_year=product.model_year, list_price=product.list_price)
    return [row for row in result]


def execute_write_connection(query, id1, id2):
    with graph.driver.session() as session:
        result = session.write_transaction(execute_write_connection_query, query, id1, id2)
        return result


def execute_write_connection_query(tx, query, id1, id2):
    result = tx.run(query, id1=id1, id2=id2)
    return [row for row in result]


def list_all_persons():
    query = (
        "MATCH (p:Person) "
        "RETURN p.name AS name"
    )
    return execute(query)

def list_all_products():
    query = (
        "MATCH (p:product) "
        "RETURN p.product_id AS product_id, p.product_name AS product_name,"
        "p.brand AS brand, p.category AS category,"
        "p.model_year AS model_year, p.list_price AS list_price"
    )
    result = execute(query)
    # prods = [Product(prod['product_id'], prod['product_name'], prod['brand'],
    #                  prod['category'], prod['model_year'], prod['list_price']) for prod in result]
    return result#, prods

def add_product(Product):
    query = (
        "CREATE (p: product "
        "{product_id: $product_id, "
        "product_name: $product_name, "
        "brand: $brand, "
        "category: $category, "
        "model_year: $model_year, "
        "list_price: $list_price}) "
        "RETURN p.product_id as product_id, p.product_name as product_name"
    )
    return execute_write_product(query, Product)


def add_product_connection(id1, id2):
    if id1 != id2:
        query = (
            "MATCH (p1:product), (p2:product) "
            "WHERE p1.product_id = $id1 and p2.product_id = $id2 "
            "CREATE (p1)-[c:_]->(p2) "
            "RETURN type(c)"
        )
        return execute_write_connection(query, str(id1), str(id2))
    return []


def get_connections_of_prod(product_id):
    query = "MATCH (p1:product)-[c:_]-(p2:product) " \
            "WHERE p1.product_id = $product_id " \
            "return p2.product_id as product_id"
    return execute_get_product(query, product_id)


def get_prod(product_id):
    query = (
        "MATCH (p:product) "
        "WHERE p.product_id=$product_id "
        "RETURN p.product_id AS product_id, p.product_name AS product_name,"
        "p.brand AS brand, p.category AS category,"
        "p.model_year AS model_year, p.list_price AS list_price"
    )
    return execute_get_product(query, product_id)


def add_all_products():
    prod_file_lines = []
    with open('data_prod.txt') as f:
        prod_file_lines = f.readlines()

    prods = []
    for line in prod_file_lines:
        elems = line[:-2].split(',')
        prods.append(Product(elems[0], elems[1], elems[2], elems[3], elems[4], elems[5]))

    # for prod in prods:
    #     add_product(prod)

    order_file_lines = []
    with open('data_orders.txt') as f:
        order_file_lines = f.readlines()


    class Order:
        def __init__(self, order_id):
            self.order_id = order_id
            self.order_list = []

        def __str__(self):
            ret = ''
            if len(self.order_list) > 0:
                ret = prods[self.order_list[0] - 1].product_name
            return f'order_list: {ret} ...and {len(self.order_list) - 1} more'

        def connect(self):
            if len(self.order_list) > 1:
                for i in range(len(self.order_list)-1):
                    for j in range(i+1, len(self.order_list)):
                        print(i, self.order_list[i], j, self.order_list[j])
                        add_product_connection(self.order_list[i], self.order_list[j])




    orders = [Order(i) for i in range(1616)]
    for line in order_file_lines:
        elems = line[:-2].split(',')
        orders[int(elems[0])-1].order_list.append(int(elems[2]))

    ## WARNING IT LASTS LONG TIME
    # for order in orders:
    #     order.connect()

def connect(prods_list):
    if len(prods_list) > 1:
        for i in range(len(prods_list)-1):
            for j in range(i+1, len(prods_list)):
                add_product_connection(prods_list[i]['product_id'], prods_list[j]['product_id'])
#
#
# def list_all_locations():
#     query = "MATCH (n:Location) RETURN (n)"
#     return execute(query)
