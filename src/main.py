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
    # Подождем пока асинхронка сделает свое дело
    time.sleep(6)
    agent.log_info("Мы завершили все, расходимся, ребятки! Проверьте ваши логи)")
    time.sleep(2)
    # Отключаем систему
    server.shutdown(200)
