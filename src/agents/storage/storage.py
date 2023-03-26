from agents.managment.working_documents import Documents
from osbrain import Agent
import json
import os


class Storage(Agent):
    """
    Агент склада – содержит список активных агентов продуктов, которые ему «подчиняются».
    Содержит таблицу имеющихся на складе продуктов с объемами остатков по каждому из них.
    «Подчиняется» управляющему агенту. «Проверяет», имеется ли в наличии на складе достаточный объем конкретного
    продукта для резервирования под экземпляр блюда / напитка для выполнения определенного заказа.
    Если такая проверка проходит успешно при получении приказа о резервировании от управляющего агента,
    создает агент продукта.
    """

    docs = ""
    active_product_agents = []
    products: []

    def __init__(self, name='', host=None, serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        self.docs = Documents()
        self.docs.get_all_documents()
        self.log_info(f"Склад готов к работе!")
        self.products = self.docs.storage_info["products"]

    def check_product(self, product, mass):
        """
        Проверяет есть ли в наличии требуемый объем продукта.
        Создает объект продукта, если такой объем присутствует.
        :param product: Продукт в виде id в складе
        :param mass: Обьем продукта
        :return: True если есть, False, если нет
        """
        temp = [float(d["prod_item_quantity"]) if product == int(d['prod_item_type']) else 0 for d in
                self.products]

        check = sum(temp) >= mass

        return check

    @staticmethod
    def use_products(dishes: []):
        """
        Использует продукты на создание блюд
        :param dishes: Блюда
        """
        with open("data/products.json", "r") as r:
            data = json.loads(r.read())

        with open("data/products.json", "w") as w:
            products = data['products']
            for dish in dishes:
                for product_op in dish['operations']:
                    for product in product_op['oper_products']:
                        for prod in products:
                            if prod['prod_item_type'] == product['prod_type']:
                                prod['prod_item_quantity'] -= product['prod_quantity']

            json.dump(data, w)
