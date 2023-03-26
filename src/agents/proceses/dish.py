from osbrain import Agent


class Dish(Agent):
    """
    Агент блюда / напитка – содержит списки созданных управляющим агентом агентов процесса,
    операций и агентов продуктов для приготовления конкретного блюда / напитка из заказа посетителя.
    Уничтожается, когда данное блюдо / напиток приготовлено, а заказ выполнен.
    """

    # ID блюда по технологической карте
    card_id = 0
    # Название блюда
    dish_name = ""
    # Описание блюда
    card_descr = ""
    # Время, затрачиваемое по технологической карте на блюдо
    card_time = 0.0
    # Тип оборудования используемый поварами
    equip_type = 0
    # Операции для создания блюда
    operations = []
    # Продукты для создания блюда
    products = []
    # Завершено ли создание блюда
    is_completed = False

    def __init__(self, id_card, name_dish, description, time_card, type_equip, name='', host=None,
                 serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        card_id = id_card
        dish_name = name_dish
        card_descr = description
        card_time = time_card
        equip_type = type_equip

    def destroy(self):
        """
        Разрушает себя при соблюдении is_completed
        """
        pass
