from agents.managment.working_documents import Documents
from osbrain import Agent


class Equipment(Agent):
    """
    Агент оборудования – представляет конкретную единицу кухонного оборудования (печь, микроволновку и т. д.),
    подчиняется управляющему агенту, который управляет его использованием посредством воздействия на агента повара,
    соответствующего конкретному человеку (повару),
    использующему это оборудование в рамках выполнения назначенной ему определенной операции процесса приготовления
    блюда. / напитка.
    """

    # Документы
    docs = ""
    # Тип оборудования
    equip_id = 0
    equip_type = 0
    # Название оборудования
    equip_name = ""
    # Задействовано ли оборудование
    equip_active = False

    def __init__(self, name='', host=None, serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def on_init(self):
        """
        Занимается получением документов и восстановлением данных агента после создания
        """
        super().on_init()
        self.docs = Documents()
        self.docs.get_all_documents()
        for i in self.docs.equipment["equipment"]:
            if i["equip_id"] == int(self.name[9:]):
                self.equip_id = i["equip_id"]
                self.equip_type = i["equip_type"]
                self.equip_name = i["equip_name"]
                self.equip_active = i["equip_active"]
        self.log_info(
            f"Прибор id:{self.equip_id} {self.equip_name} типа {self.equip_type} в состоянии {self.equip_active}!")
