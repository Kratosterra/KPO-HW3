from agents.managment.working_documents import Documents
from osbrain import Agent


class Cooker(Agent):
    """
    Агент повара – представляет конкретного человека – повара ресторана,
    взаимодействует с ним через кухонный сенсорный терминал, управляет его работой
    (назначает ему выполнение определенной операции,
    отменяет / принимает от него события, связанные с выполнением им операций («приступил к выполнению операции»,
    «выполнил операцию», «отменил выполнение операции» (испорчен продукт в процессе приготовления)).
    """

    # Документы
    docs = ""
    # ID повара
    cook_id = 0
    # Имя повара
    cook_name = ""
    # Активен ли повар
    cook_active = False
    # Оборудование, которое использует повар
    equipment = ""

    def __init__(self, name='', host=None, serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        self.docs = Documents()
        self.docs.get_all_documents()
        for cooker in self.docs.cookers["cookers"]:
            if cooker["cook_id"] == int(self.name[8:]):
                self.cook_id = cooker["cook_id"]
                self.cook_name = cooker["cook_name"]
                self.cook_active = cooker["cook_active"]
        self.log_info(f"Я, id:{self.cook_id} {self.cook_name}, прибыл на работу в состоянии {self.cook_active}!")
