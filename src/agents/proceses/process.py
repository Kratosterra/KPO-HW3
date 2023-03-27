import datetime

from agents.managment.working_documents import Documents
from agents.proceses.operation import Operation
from agents.proceses.process_log import ProcessLog
from osbrain import Agent, run_agent


class Process(Agent):
    """
    !ВЫГРУЖАЕТСЯ В LOG!
    Агент процесса. Агенты, представляющие процесс, выполняемый либо непосредственно человеком (поваром),
    либо устройством (кухонным оборудованием) под контролем человека. Фактически контролирует выполнение процесса,
    состоящего из технологических операций.
    Может предоставить информацию о примерном времени ожидания выполнения процесса.
    Эти агенты фактически выполняют подготовку заказа.
    Они могут обращаться к агентам, представляющим человека (повара, готовящего мясо)
    или устройство (кофеварку, которая готовит эспрессо).
    Их цель – обеспечить выполнение заказов, созданных агентами посетителей с помощью управляющего агента (супервизора),
    чтобы фактически приготовить блюда / напитки с использованием продуктов,
    которые представляют соответствующие агенты продуктов.
    """

    proc_id = 0
    # Документы
    docs = ""
    # Время начала процесса
    proc_started = ""
    ord_dish = 0
    # Время окончания процесса
    proc_ended = ""
    # Активен ли процесс
    proc_active = False,
    # Операции для выполнения процесса
    operations = []
    proc_operations = []
    # Повара
    cookers = []
    # Оборудование
    equipments = []

    def __init__(self, name='', host=None, serializer=None,
                 transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        self.docs = Documents()
        self.docs.get_all_documents()
        self.log_info(f"Приветики, я тут попроцесирую!")

    def execute_operations(self):
        """
        Выполняет операции по приготовлению блюда
        """
        self.log_info(f"Начинаю исполнение операций {self.operations}!")
        num_oper = 1
        for oper in self.operations:
            operation = run_agent(f"Operation:{self.name}:{num_oper}", base=Operation)
            num_oper += 1

        self.proc_ended = str(datetime.datetime.utcnow())
        log = ProcessLog()
        log.log_process(dict(proc_id=self.proc_id, ord_dish=self.ord_dish, proc_started=self.proc_started,
                             proc_ended=self.proc_ended, proc_active=self.proc_active,
                             proc_operations=self.proc_operations))
