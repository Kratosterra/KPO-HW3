import json


class ProcessLog:
    logs: []

    def __init__(self):
        with open('log/operation_log.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)

        self.logs = data

    def log_process(self, agent):
        """
        Записывает данные в лог
        :param agent: представление агента в словаре
        """
        self.logs["process_log"].append(agent)

        with open('log/operation_log.json', 'w') as f:
            json.dump(self.logs, f)
