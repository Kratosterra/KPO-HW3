import json


class Documents:
    """
    Класс ответственный за хранение и получение документов из JSON
    """

    # Меню ресторана в виде словаря из json
    menu = dict()
    # Технологические карты ресторана в виде словаря из json
    cooking_flow_cards = dict()
    # Справочник типов продуктов / расходников из json
    product_types = dict()
    # Список продуктов / расходников на складе ресторана из json
    storage_info = dict()
    # Справочник типов кухонного оборудования из json
    equipment_types = dict()
    # Перечень кухонного оборудования из json
    equipment = dict()
    # Список поваров из json
    cookers = dict()
    # Справочник типов операций на кухне из json
    operation_types = dict()
    # Список посетителей с заказами из json
    visitors_orders = dict()

    def __init__(self):
        super().__init__()

    def get_all_documents(self):
        """
        Получает все документы
        """
        try:
            self._get_menu()
            self._get_cooking_flow_cards()
            self._get_product_types()
            self._get_storage_info()
            self._get_equipment_types()
            self._get_equipment()
            self._get_cookers()
            self._get_operation_types()
            self._get_visitors_orders()
        except Exception as e:
            print(f"Произошла ошибка при считывании json файлов: {e}")

    def _get_menu(self):
        """
        Получает меню
        """
        with open('data/menu_dishes.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.menu = data

    def _get_cooking_flow_cards(self):
        """
        Получает тех. карты
        """
        with open('data/dish_cards.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.cooking_flow_cards = data

    def _get_product_types(self):
        """
        Получает типы продуктов
        """
        with open('data/product_types.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.product_types = data

    def _get_storage_info(self):
        """
        Получает информацию о складе
        """
        with open('data/products.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.storage_info = data

    def _get_equipment(self):
        """
        Получает информацию об оборудовании
        """
        with open('data/equipment.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.equipment = data

    def _get_equipment_types(self):
        """
        Получает типы оборудования
        """
        with open('data/equipment_type.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.equipment_types = data

    def _get_cookers(self):
        """
        Получает поваров
        """
        with open('data/cookers.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.cookers = data

    def _get_operation_types(self):
        """
        Получает типы операций
        """
        with open('data/operation_types.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.operation_types = data

    def _get_visitors_orders(self):
        """
        Получает заказы и самих посетителей
        """
        with open('data/visitor_orders.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        self.visitors_orders = data
