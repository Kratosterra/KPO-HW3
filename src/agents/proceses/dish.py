import datetime

from agents.managment.working_documents import Documents
from agents.proceses.process import Process
from osbrain import Agent, run_agent


class Dish(Agent):
    """
    Агент блюда / напитка – содержит списки созданных управляющим агентом агентов процесса,
    операций и агентов продуктов для приготовления конкретного блюда / напитка из заказа посетителя.
    Уничтожается, когда данное блюдо / напиток приготовлено, а заказ выполнен.
    """

    # Документы
    docs = ""
    # ID блюда по технологической карте
    card_id = 0
    # Название блюда
    dish_name = ""
    # Описание блюда
    card_descr = ""
    # Время, затрачиваемое по технологической карте на блюдо
    card_time = 0.0
    # Завершено ли создание блюда
    is_completed = False
    dish_card = dict()

    def __init__(self, name='', host=None,
                 serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        self.docs = Documents()
        self.docs.get_all_documents()
        self.log_info("Я блюдо, и я рад этому!")

    def start_execution(self):
        """
        Начинает изготовление блюда
        """
        self.log_info(f"Начинаю свое приготовление по карточке {self.dish_card}")
        self.card_id = self.dish_card["card_id"]
        self.dish_name = self.dish_card["dish_name"]
        self.card_descr = self.dish_card["card_descr"]
        self.card_time = self.dish_card["card_time"]
        self.log_info(f"Я представляю \"{self.dish_name}\" по описанию я \"{self.card_descr}\"!")
        self.log_info(f"Приступаю к созданию процесса который займет {self.card_time} минут!")
        process = run_agent(f"Process:{self.name}", base=Process)
        process.set_attr(operations=self.dish_card["operations"])
        process.set_attr(proc_started=str(datetime.datetime.utcnow()))
        process.set_attr(ord_dish=int(self.name[12:-2]) * int(self.name[-1:]) * 11)
        process.set_attr(proc_id=int(self.name[12:-2]) * int(self.name[-1:]))
        self.log_info(f"Начинаю исполнение процесса!")
        process.execute_operations()
