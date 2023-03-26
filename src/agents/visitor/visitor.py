import ast

from agents.managment.working_documents import Documents
from osbrain import Agent


class Visitor(Agent):
    """
    Агент посетителя – запрашивает у управляющего агента текущее актуальное меню, содержащее исключительно блюда
    и напитки, которые могут быть приготовлены за заданное нормативное время (например, максимум за 20 мин)
    с указанием необходимого для приготовления каждого блюда / напитка времени.
    Обращается к управляющему агенту с запросом на формирование заказа из выбранных посетителем блюд и / или напитков.
    Это агент, который взаимодействует непосредственно с клиентом.
    Также он просит управляющего агента создать агентов заказа и взаимодействует с ними,
    чтобы получить и затем предоставить посетителю время ожидания заказа.
    Чтобы иметь возможность отключить недоступные пункты меню, этот агент может,
    например, пассивно ожидать соответствующих уведомлений от других агентов.
    """

    # Документы
    docs = ""
    # Имя посетителя
    vis_name = ""
    # Время визита посетителя
    vis_ord_started = ""
    # Время окончания визита пользователя
    vis_ord_ended = ""
    # Цена всего заказа
    vis_ord_total = ""
    # Заказ из блюд
    vis_ord_dishes = []

    _menu = dict()

    def __init__(self, name='', host=None, serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        self.docs = Documents()
        self.docs.get_all_documents()
        self.bind('PUSH', alias=str(self.name))
        for i in self.docs.visitors_orders["visitors_orders"]:
            if i["vis_name"] == self.name[8:]:
                self.vis_name = i["vis_name"]
                self.vis_ord_started = i["vis_ord_started"]
                self.vis_ord_total = i["vis_ord_total"]
                self.vis_ord_dishes = i["vis_ord_dishes"]
        self.log_info(
            f"Посетитель {self.vis_name} прибыл в {self.vis_ord_started} и хочет заказать {self.vis_ord_dishes} на сумму {self.vis_ord_total}!")

    def begin_make_order(self):
        # Просим меню у управляющего агента
        self.log_info("Прошу управляющего агента предоставить меню!")
        self.ask_for_menu()

    def ask_for_order(self, order):
        """
        «Попросить» управляющего агента создать экземпляр агента заказа.
        :param order: Заказ
        """
        self.send(self.addr(str(self.name)), message=f'Order {str(self.name)} {order}')

    def on_reply_from_supervisor(self, message):
        now_order = []
        command_list = message.split()
        if command_list[0] == "Неизвестный":
            return
        if command_list[0] == self.name:
            self.log_info('Получил от менеджера: %s' % message)

        if command_list[0] == self.name and command_list[1] == "Menu":
            di = message[len(command_list[0]) + len(command_list[1]) + 2:]
            di = di.replace("'", '"')
            di = ast.literal_eval(di)
            self._menu = di
            self.log_info(f'Получил от менеджера меню: {self._menu}')
            # Составляем заказ только из доступных блюд
            for i in self.docs.visitors_orders["visitors_orders"]:
                if i["vis_name"] == self.name[8:]:
                    for dish in i["vis_ord_dishes"]:
                        for m in self._menu:
                            if dish["menu_dish"] == m["menu_dish_id"]:
                                now_order.append(dish)
                                break
            self.log_info(f"Попробовал создать заказ с учетом текущего меню: {now_order}!")
            # Добавляем блюда в заказ:
            self.log_info("Прошу управляющего агента составить заказ!")
            if len(now_order) > 0:
                self.ask_for_order(now_order)
            else:
                self.log_info(f"Не смог составить заказ, нечего мне тут брать!")
        elif command_list[0] == self.name and command_list[1] == "Order":
            if command_list[2] == "YES":
                self.log_info("Ура, жду свой заказ!")
            else:
                self.log_info("Заказ отменен, наверное на него не хватает ингредиентов!")
        elif command_list[0] == self.name:
            self.log_info("Неизвестно")

    def ask_for_menu(self):
        self.send(self.addr(str(self.name)), message=f'Menu {str(self.name)}')
