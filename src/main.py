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
    agent = run_agent("Supervisor", base=Supervisor)
    # Отключаем систему
    server.shutdown()
