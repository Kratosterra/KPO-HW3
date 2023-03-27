import time

import osbrain
from osbrain import run_agent
from osbrain import run_nameserver

from agents.managment.supervisor import Supervisor

# Конфигурация сохранения в json
osbrain.config['SERIALIZER'] = 'json'

if __name__ == '__main__':
    # Запуск системы
    server = run_nameserver()
    # Запуск супервайзера
    agent = run_agent("Supervisor", base=Supervisor, safe=False)
    time.sleep(10)
    agent.log_info("Мы завершили все, расходимся, ребятки!")
    time.sleep(2)
    # Отключаем систему
    server.shutdown(200)
