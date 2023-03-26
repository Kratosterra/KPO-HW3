from osbrain import Agent


class Operation(Agent):
    """
    !ВЫГРУЖАЕТСЯ В LOG!
    Агент операции запрашивает управляющего агента зарезервировать агента повара и агента оборудования для выполнения
    операции процесса.
    """

    # ID операции
    oper_id = 0
    # Номер процесса операции
    oper_proc = 0
    # Номер процесса по технологической карте
    oper_card = 0
    # Время начала выполнения операции
    oper_started = ""
    # Время окончания выполнения операции
    oper_ended = ""
    # ID повара, выполняющего операцию
    oper_cooker_id = 0
    # Активно ли выполнения операции
    oper_active = False
    # Агент повара
    cooker = ""
    # Агент оборудования
    equipment = ""

    def __init__(self, name='', host=None, serializer=None, transport=None, attributes=None):
        super().__init__(name, host, serializer, transport, attributes)

    def reserve_cooker_and_equipment(self):
        """
        Запрашивает у управляющего агента повара и оборудование
        """
        pass
