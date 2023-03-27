from agents.managment.working_documents import Documents
from osbrain import Agent, run_agent

from agents.proceses.dish import Dish


class Order(Agent):
    """
    Агент заказа – подчиняется управляющему агенту, хранит список заказанных посетителем блюд и / или напитков в виде
    списка созданных управляющим агентом агентов блюд / напитков. Эти агенты взаимодействуют с другими типами
    агентов. Они взаимодействуют с управляющим агентом и с агентами продуктов и процессов, чтобы получить необходимые ресурсы и выполнить требуемые процессы для
    выполнения заказа.
    """

    docs = ""
    # Кому принадлижит заказ
    visitor_name = ""
    # Массив блюд
    vis_ord_dishes = []
    # Примерное время ожидания
    time_of_waiting = 0
    # Блюда
    dish_agents = []
    # Возможен ли заказ
    is_possible = False

    def __init__(self, name='', host=None, serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        self.bind('PUSH', alias=str(self.name))
        self.docs = Documents()
        self.docs.get_all_documents()
        self.log_info("Я родился!")

    def on_reply_from_supervisor(self, message):
        """
        Принимает и обрабатывает сообщения от управляющего агента.
        :param message: Сообщение от управляющего агента
        """
        self.log_info(f"Получил от менеджера: {message}")
        pass

    def send_message_to_visitor(self):
        """
        Отправляет агенту посетителя информацию о времени ожидания его заказа.
        """
        pass

    def ask_for_time_of_waiting(self):
        """
        «Просит» агентов процесса предоставить оценку времени ожидания.
        """
        pass

    def on_get_answer_from_process(self, answer):
        """
        Обрабатывает ответ от агентов процессов о времени ожидания готовности блюд / напитков.
        :param answer: Ответ от процессов
        """
        pass

    def start_execution(self):
        self.log_info(f"Начинаю создание блюд по технологическим картам {self.vis_ord_dishes}")
        num_of_dish = 1
        for dish_card in self.vis_ord_dishes:
            dish = run_agent(f"Dish:{self.visitor_name[8:]}:{num_of_dish}", base=Dish)
            dish.set_attr(dish_card=dish_card)
            self.dish_agents.append(dish)
            num_of_dish += 1
        for dish in self.dish_agents:
            dish.start_execution()
        pass

    def is_possible(self):
        return self.is_possible
