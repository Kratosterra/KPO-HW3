import ast
import time

from agents.managment.working_documents import Documents
from agents.performers.cooker import Cooker
from agents.performers.equipment import Equipment
from agents.proceses.order import Order
from agents.storage.storage import Storage
from agents.visitor.visitor import Visitor
from osbrain import Agent
from osbrain import run_agent


class Supervisor(Agent):
    """
    Управляющий агент (супервизор) управляет другими агентами для выполнения заказов посетителей.
    Запускает процесс создания нового заказа. На основании запроса от агента посетителя создает агента заказа,
    а после выполнения заказа контролирует уничтожение агента заказа. Взаимодействует с агентом склада.
    «Приказывает» ему зарезервировать для каждого экземпляра сделанного блюда (напитка) из определенного заказа
    заданный объем конкретного продукта. Создает и уничтожает всех прочих агентов.
    """

    # Обьект документа
    docs = ""
    # Агент-склада, созданный менеджером
    storage_agent = ""
    # Агенты-поваров, созданные менеджером
    cook_agents = dict()
    # Агенты-оборудование, созданные менеджером
    equipment_agents = dict()
    # Агенты-посетителей, созданные менеджером
    visitor_agents = dict()
    # Агенты-заказы, созданные менеджером
    orders = dict()

    def __init__(self, name='', host=None, serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        # Получаем документы и начинаем рабочий день.
        self.docs = Documents()
        self.docs.get_all_documents()
        # Обявляем наличие подписочных сообщений
        self.bind('SYNC_PUB', alias='supervisor', handler=self.on_message)
        self.bind('SYNC_PUB', alias='supervisor_orders', handler=self.on_message)
        # Начинаем день
        self.start_day()

    def start_day(self):
        """
        Начинает день на предприятии, запуская работу с клиентами и создания агентов.
        """
        self.log_info("День начался. Начинаю работу!")
        # Начинаем с того, что создаем агент склада, надо же как-то работать.
        self.log_info("Создаю агента хранилища!")
        self.storage_agent = run_agent("Storage", base=Storage, safe=False)
        # Создаем агентов-поваров
        self.log_info("Создаю агентов работников!")
        for i in self.docs.cookers["cookers"]:
            agt = run_agent(f"Cook_id:{i['cook_id']}", base=Cooker)
            # Добавляем агента в словарь по его имени
            self.cook_agents[f"Cook_id:{i['cook_id']}"] = agt
        # Создаем агентов-оборудования
        self.log_info("Создаю агентов оборудования!")
        for i in self.docs.equipment["equipment"]:
            agt = run_agent(f"Equip_id:{i['equip_id']}", base=Equipment)
            # Добавляем агента в словарь по его имени
            self.equipment_agents[f"Equip_id:{i['equip_id']}"] = agt
        # Проходимся по посетителям и создаём их агентов
        for visitor in self.docs.visitors_orders["visitors_orders"]:
            agt = run_agent(f"Visitor:{visitor['vis_name']}", base=Visitor)
            self.log_info(f"Создал {visitor['vis_name']}!")

            # Подключаем агента к рассылкам от менеджера используя хэндлер в классе посетителя
            agt.connect(self.addr('supervisor'), handler='on_reply_from_supervisor')

            # Подключаем менджера к сообщениям от самого посетитетя используя хэндлер тут
            self.connect(agt.addr(str(agt.get_attr('name'))), handler=self.on_message_from_visitor)

            self.log_info(f"Подключил {visitor['vis_name']}!")
            # Заставляем посетителя начать заказывать
            agt.begin_make_order()
            # Добавляем агента в словарь по его имени
            self.visitor_agents[f"Visitor:{visitor['vis_name']}"] = agt
        # Продолжаем обслуживание, пока все клиенты не уйдут на основе сообщений от агентов.
        return

    def on_message(self, message):
        self.log_info('Получил сообщение: %s' % message)

    def on_message_from_visitor(self, message):
        self.log_info('Получил от посетителя: %s' % message)

        command_list = message.split()
        if command_list[0] == "Menu":
            self.send(self.addr('supervisor'), f'{command_list[1]} Menu {self.docs.menu["menu_dishes"]}')
        elif command_list[0] == "Order":
            di = message[len(command_list[0]) + len(command_list[1]) + 2:]
            di = di.replace("'", '"')
            di = ast.literal_eval(di)
            dishes = []
            for dish in di:
                for pos in self.docs.menu["menu_dishes"]:
                    if dish["menu_dish"] == pos["menu_dish_id"]:
                        for dish_card in self.docs.cooking_flow_cards["dish_cards"]:
                            if pos["menu_dish_card"] == dish_card["card_id"]:
                                dishes.append(dish_card)
            is_order_possible = True
            flag = False
            for dish_card in dishes:
                for operation in dish_card['operations']:
                    for product in operation['oper_products']:
                        flag = True
                        if self.storage_agent.is_running():
                            is_order_possible = is_order_possible and self.storage_agent.check_product(
                                product['prod_type'],
                                float(product['prod_quantity']))
            if is_order_possible and flag:
                self.send(self.addr('supervisor'), f"{command_list[1]} Order YES")
                self.log_info(f"Начинаю создание заказа для {command_list[1]}")
                self.log_info(f"Работаем со складом над продуктами!")
                self.storage_agent.use_products(dishes)
                self.create_new_order(command_list[1], dishes)
            else:
                self.send(self.addr('supervisor'), f"{command_list[1]} Order NO")
                self.log_info(f"Заказ делать не будем, отказ!")
        else:
            self.send(self.addr('supervisor'), f"{command_list[1]} Команда не распознана!")

    def on_message_from_order(self, message):
        self.log_info('Получил от заказа: %s' % message)

    def on_message_from_equipment(self, message):
        self.log_info('Получил от оборудования: %s' % message)

    def destroy_all_agents(self):
        """
        Удалить всех агентов
        """
        self.storage_agent.kill()
        for agent in self.cook_agents:
            agent.kill()

        for agent in self.equipment_agents:
            agent.kill()
        for agent in self.visitor_agents:
            agent.kill()
        for agent in self.orders:
            agent.kill()
        pass

    def create_new_order(self, name_visitor_agent, order: list):
        """
        Создать новый заказ.
        :param order: Заказ в виде обычного представления в виде листа
        """
        self.log_info("Создаю заказ!")
        ord = run_agent(f"Order:{name_visitor_agent[8:]}", base=Order, safe=False)
        ord.set_attr(vis_ord_dishes=order)
        self.connect(ord.addr(str(ord.get_attr('name'))), handler=self.on_message_from_order)
        ord.connect(self.addr('supervisor_orders'), handler='on_reply_from_supervisor')
        self.log_info("Подключил заказ к информационной системе!")
        self.log_info("Приказываю заказу начать исполнение!")
        ord.start_execution()
        self.orders[f"Order:{name_visitor_agent[8:]}"] = ord
        pass
