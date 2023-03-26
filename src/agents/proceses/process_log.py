import json

from osbrain import Agent


class ProcessLog:
    logs: []

    def __init__(self):
        with open('log/operation_log.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)

        self.logs = data

    def log_process(self, agent: Agent):
        self.logs.append(agent)

        with open('log/operation_log.json', 'w') as f:
            json.dump(self.logs, f)
