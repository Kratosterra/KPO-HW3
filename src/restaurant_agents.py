import os

import osbrain
import json
from osbrain import run_agent

def load_json_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)


cookers = load_json_data(f'{os.getcwd()}/data/cookers.json')
dish_cards = load_json_data(f'{os.getcwd()}/data/dish_cards.json')
equipment = load_json_data(f'{os.getcwd()}/data/equipment.json')
equipment_types = load_json_data(f'{os.getcwd()}/data/equipment_types.json')
menu_dishes = load_json_data(f'{os.getcwd()}/data/menu_dishes.json')
operation_types = load_json_data(f'{os.getcwd()}/data/operation_types.json')
product_types = load_json_data(f'{os.getcwd()}/data/product_types.json')
products = load_json_data(f'{os.getcwd()}/data/products.json')
visitors_orders = load_json_data(f'{os.getcwd()}/data/visitor_orders.json')


class VisitorAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.order_agent = None
        self.order = None
        self.menu = None

    def on_init(self):
        self.menu = menu_dishes
        self.order = []
        self.order_agent = None

    def add_menu_item(self, menu_item_id):
        for item in self.menu:
            if item['menu_dish_id'] == menu_item_id:
                self.order.append(item)
                return f"Added {item['menu_dish_card']} to the order."
        return f"Menu item with ID {menu_item_id} not found."

    def remove_menu_item(self, menu_item_id):
        for item in self.order:
            if item['menu_dish_id'] == menu_item_id:
                self.order.remove(item)
                return f"Removed {item['menu_dish_card']} from the order."
        return f"Menu item with ID {menu_item_id} not found in the order."

    def disable_menu_item(self, menu_item_id):
        for item in self.menu:
            if item['menu_dish_id'] == menu_item_id:
                item['menu_dish_active'] = False
                return f"Disabled menu item with ID {menu_item_id}."
        return f"Menu item with ID {menu_item_id} not found."

    def enable_menu_item(self, menu_item_id):
        for item in self.menu:
            if item['menu_dish_id'] == menu_item_id:
                item['menu_dish_active'] = True
                return f"Enabled menu item with ID {menu_item_id}."
        return f"Menu item with ID {menu_item_id} not found."

    def request_order_agent(self, manager_agent):
        self.order_agent = run_agent('OrderAgent', base=OrderAgent)
        manager_agent.connect(self.addr(alias='visitor_default'), handler=manager_agent.create_order_agent)
        self.send(manager_agent.addr(alias='manager_default'), self.order_agent.addr(alias='order_default'))

    def cancel_order(self):
        if self.order_agent:
            self.order_agent.shutdown()
            self.order_agent = None
            self.order = []
            return "Order canceled and OrderAgent destroyed."
        else:
            return "No active order to cancel."

    def get_estimated_waiting_time(self):
        if self.order_agent:
            return self.order_agent.get_estimated_waiting_time()
        else:
            return "No active order to get estimated waiting time for."

    def receive_waiting_time(self, message):
        waiting_time = message
        self.send(self.addr(alias='visitor_default'), f"Estimated waiting time: {waiting_time} minutes")


class ControlAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.storage_agent = run_agent('StorageAgent', base=StorageAgent)
        self.visitor_agents = {}
        self.order_agents = {}
        self.dish_agents = {}
        self.process_agents = {}
        self.operation_agents = {}
        self.chef_agents = {}
        self.equipment_agents = {}

    def create_visitor_agent(self, visitor_name):
        visitor_agent = run_agent(visitor_name, base=VisitorAgent)
        self.visitor_agents[visitor_name] = visitor_agent
        return visitor_agent.addr(alias='visitor_default')

    def remove_visitor_agent(self, visitor_name):
        if visitor_name in self.visitor_agents:
            self.visitor_agents[visitor_name].shutdown()
            del self.visitor_agents[visitor_name]

    def create_order_agent(self, visitor_name):
        if visitor_name in self.visitor_agents:
            order_agent = run_agent(f'OrderAgent_{visitor_name}', base=OrderAgent)
            self.order_agents[visitor_name] = order_agent
            return order_agent.addr(alias='order_default')
        else:
            raise ValueError(f"Visitor agent {visitor_name} not found.")

    def remove_order_agent(self, visitor_name):
        if visitor_name in self.order_agents:
            self.order_agents[visitor_name].shutdown()
            del self.order_agents[visitor_name]

    def create_and_reserve_order(self, visitor_name, order):
        order_agent_addr = self.create_order_agent(visitor_name)
        order_agent = self.order_agents[visitor_name]

        order_agent.process_order(self.visitor_agents[visitor_name], order)

        for dish in order:
            dish_id = dish['menu_dish_id']
            dish_agent = self.create_dish_agent(dish_id)
            self.reserve_products_for_dish(dish_agent, dish)

        return order_agent_addr

    def create_dish_agent(self, dish_id):
        dish_agent = run_agent(f'DishAgent_{dish_id}', base=DishAgent)
        self.dish_agents[dish_id] = dish_agent
        return dish_agent

    def remove_dish_agent(self, dish_id):
        if dish_id in self.dish_agents:
            self.dish_agents[dish_id].shutdown()
            del self.dish_agents[dish_id]

    def reserve_products_for_dish(self, dish_agent, dish):
        for operation in dish['operations']:
            for product in operation['oper_products']:
                self.storage_agent.reserve_product(product)

    def create_process_agent(self, process_id):
        process_agent = run_agent(f'ProcessAgent_{process_id}', base=ProcessAgent)
        self.process_agents[process_id] = process_agent
        return process_agent

    def remove_process_agent(self, process_id):
        if process_id in self.process_agents:
            self.process_agents[process_id].shutdown()
            del self.process_agents[process_id]

    def create_operation_agent(self, operation_id):
        operation_agent = run_agent(f'OperationAgent_{operation_id}', base=OperationAgent)
        self.operation_agents[operation_id] = operation_agent
        return operation_agent

    def remove_operation_agent(self, operation_id):
        if operation_id in self.operation_agents:
            self.operation_agents[operation_id].shutdown()
            del self.operation_agents[operation_id]

    def create_chef_agent(self, chef_id):
        chef_agent = run_agent(f'ChefAgent_{chef_id}', base=ChefAgent)
        self.chef_agents[chef_id] = chef_agent
        return chef_agent

    def remove_chef_agent(self, chef_id):
        if chef_id in self.chef_agents:
            self.chef_agents[chef_id].shutdown()
            del self.chef_agents[chef_id]

    def create_equipment_agent(self, equipment_id, equipment_type):
        equipment_agent = run_agent(f'EquipmentAgent_{equipment_id}', base=EquipmentAgent,
                                    attributes={'equipment_type': equipment_type})
        self.equipment_agents[equipment_id] = equipment_agent
        return equipment_agent

    def remove_equipment_agent(self, equipment_id):
        if equipment_id in self.equipment_agents:
            self.equipment_agents[equipment_id].shutdown()
            del self.equipment_agents[equipment_id]

    def get_chef_agent(self, chef_id):
        if chef_id in self.chef_agents:
            return self.chef_agents[chef_id]
        else:
            raise ValueError(f"Chef agent {chef_id} not found.")

    def get_equipment_agent_by_type(self, equipment_type):
        for equipment_id, equipment_agent in self.equipment_agents.items():
            if equipment_agent.get_attr('equipment_type') == equipment_type:
                return equipment_agent
        raise ValueError(f"Equipment agent with type {equipment_type} not found.")


class OrderAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.reserved_resources = None
        self.waiting_times = None
        self.dish_agents = None
        self.visitor_agent = None

    def on_init(self):
        self.visitor_agent = None
        self.dish_agents = {}
        self.waiting_times = {}
        self.reserved_resources = []
        self.bind_handlers()

    def process_order(self, visitor_agent, order):
        self.visitor_agent = visitor_agent
        for dish in order:
            dish_id = dish['menu_dish_id']
            dish_agent = run_agent(f'DishAgent_{dish_id}', base=DishAgent)
            self.dish_agents[dish_id] = dish_agent
            self.estimate_waiting_time(dish_agent)

    def estimate_waiting_time(self, dish_agent):
        dish_agent.connect(self.addr('waiting_time'), handler=self.receive_waiting_time)
        dish_agent.send(self.addr('waiting_time'), 'request_waiting_time')

    def receive_waiting_time(self, message):
        dish_agent, waiting_time = message
        dish_id = dish_agent.get_attr('dish_id')
        self.waiting_times[dish_id] = waiting_time
        self.update_visitor_waiting_time()

    def update_visitor_waiting_time(self):
        total_waiting_time = sum(self.waiting_times.values())
        self.visitor_agent.connect(self.addr('waiting_time_update'), handler=self.visitor_agent.receive_waiting_time)
        self.visitor_agent.send(self.addr('waiting_time_update'), total_waiting_time)

    def reserve_resources(self, dish_agent, resources):
        for resource in resources:
            self.reserved_resources.append(resource)

    def cancel_reservation(self, resource):
        if resource in self.reserved_resources:
            self.reserved_resources.remove(resource)

    def receive_reservation_result(self, message):
        resource_agent, success = message
        if not success:
            self.cancel_reservation(resource_agent.get_attr('resource'))

    def bind_handlers(self):
        self.bind('REP', alias='waiting_time', handler=self.receive_waiting_time)
        self.bind('REP', alias='waiting_time_update', handler=self.update_visitor_waiting_time)


class DishAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.process_agents = None
        self.operation_agents = None
        self.product_agents = None

    def on_init(self):
        self.process_agents = {}
        self.operation_agents = {}
        self.product_agents = {}

    def create_process_agents(self, processes):
        for process in processes:
            process_id = process['process_id']
            process_agent = run_agent(f'ProcessAgent_{process_id}', base=ProcessAgent)
            self.process_agents[process_id] = process_agent

    def create_operation_agents(self, operations):
        for operation in operations:
            operation_id = operation['operation_id']
            operation_agent = run_agent(f'OperationAgent_{operation_id}', base=OperationAgent)
            self.operation_agents[operation_id] = operation_agent

    def create_product_agents(self, products):
        for product in products:
            product_id = product['product_id']
            product_agent = run_agent(f'ProductAgent_{product_id}', base=ProductAgent)
            self.product_agents[product_id] = product_agent

    def process_dish(self, dish):
        self.create_process_agents(dish['processes'])
        self.create_operation_agents(dish['operations'])
        self.create_product_agents(dish['products'])

    def check_dish_status(self):
        for product_agent in self.product_agents.values():
            if not product_agent.get_attr('task_completed'):
                return False
        return True

    def dish_completed(self):
        order_agent = self.get_attr('order_agent')
        order_agent.connect(self.addr('dish_completed'), handler=order_agent.dish_completed)
        order_agent.send(self.addr('dish_completed'), self)
        self.shutdown()

    def request_waiting_time(self):
        waiting_time = 0
        for operation_agent in self.operation_agents.values():
            waiting_time += operation_agent.get_attr('waiting_time')
        return waiting_time

    def bind_handlers(self):
        self.bind('REP', alias='dish_completed', handler=self.dish_completed)


class ProcessAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.operation_agents = None
        self.chef_agents = None
        self.equipment_agents = None

    def on_init(self):
        self.operation_agents = {}
        self.chef_agents = {}
        self.equipment_agents = {}

    def start_process(self):
        control_agent = self.get_attr('control_agent')
        chef_id = self.get_attr('chef_id')
        equipment_type = self.get_attr('equipment_type')

        chef_agent = control_agent.get_chef_agent(chef_id)
        equipment_agent = control_agent.get_equipment_agent_by_type(equipment_type)

        operation_agent = run_agent('operation_agent', base=OperationAgent)
        operation_agent.set_attr(chef_agent=chef_agent)
        operation_agent.set_attr(equipment_agent=equipment_agent)

        operation_agent.connect(chef_agent.addr(), alias='chef_agent', handler=operation_agent.chef_ready)
        operation_agent.connect(equipment_agent.addr(), alias='equipment_agent', handler=operation_agent.equipment_ready)

        operation_agent.send(chef_agent.addr(), 'check_availability')
        operation_agent.send(equipment_agent.addr(), 'check_availability')

    def receive_operation_completion(self, message):
        operation_agent = message
        self.process_completed(operation_agent)

    def process_completed(self, operation_agent):
        # Implement the process completion logic here
        pass

    def bind_handlers(self):
        self.bind('REP', alias='process_completed', handler=self.receive_operation_completion)


class OperationAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.process_agent = None
        self.chef_agent = None
        self.equipment_agent = None

    def on_init(self):
        self.process_agent = None
        self.chef_agent = None
        self.equipment_agent = None
        self.bind_handlers()

    def process_operation(self, process_agent, chef_id, equipment_type):
        self.process_agent = process_agent
        control_agent = self.get_attr('control_agent')

        self.request_chef_agent(chef_id, control_agent)
        self.request_equipment_agent(equipment_type, control_agent)

    def request_chef_agent(self, chef_id, control_agent):
        self.chef_agent = control_agent.chef_agents[chef_id]
        self.chef_agent.connect(self.addr('chef_result'), handler=self.receive_chef_reservation_result)
        self.chef_agent.send(self.addr('chef_result'), 'reserve')

    def receive_chef_reservation_result(self, message):
        chef_agent, success = message
        if not success:
            self.cancel_operation()
        else:
            self.process_agent.reserve_resources(self.chef_agent)

    def request_equipment_agent(self, equipment_type, control_agent):
        self.equipment_agent = None
        for eq in control_agent.equipment_agents.values():
            if eq.get_attr('equipment_type') == equipment_type:
                self.equipment_agent = eq
                break

        if not self.equipment_agent:
            self.cancel_operation()
        else:
            self.equipment_agent.connect(self.addr('equipment_result'), handler=self.receive_equipment_reservation_result)
            self.equipment_agent.send(self.addr('equipment_result'), 'reserve')

    def receive_equipment_reservation_result(self, message):
        equipment_agent, success = message
        if not success:
            self.cancel_operation()
        else:
            self.process_agent.reserve_resources(self.equipment_agent)

    def cancel_operation(self):
        if self.chef_agent:
            self.chef_agent.send(self.addr('chef_result'), 'cancel_reservation')
            self.chef_agent = None

        if self.equipment_agent:
            self.equipment_agent.send(self.addr('equipment_result'), 'cancel_reservation')
            self.equipment_agent = None

        self.process_agent.cancel_reservation(self)

    def operation_completed(self):
        self.process_agent.operation_completed(self)

        if self.chef_agent:
            self.chef_agent.send(self.addr('chef_result'), 'cancel_reservation')
            self.chef_agent = None

        if self.equipment_agent:
            self.equipment_agent.send(self.addr('equipment_result'), 'cancel_reservation')
            self.equipment_agent = None

        self.shutdown()

    def bind_handlers(self):
        self.bind('REP', alias='chef_result', handler=self.receive_chef_reservation_result)
        self.bind('REP', alias='equipment_result', handler=self.receive_equipment_reservation_result)


class StorageAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.product_agents = {}
        self.product_inventory = {}

    def on_init(self):
        self.product_agents = {}
        self.product_inventory = {}
        self.bind_handlers()

    def add_product_agent(self, product_agent):
        self.product_agents[product_agent.get_attr('product_id')] = product_agent

    def remove_product_agent(self, product_agent):
        product_id = product_agent.get_attr('product_id')
        if product_id in self.product_agents:
            del self.product_agents[product_id]

    def reserve_product(self, product):
        product_id = product['product_id']
        quantity = product['oper_product_quantity']

        if product_id in self.product_inventory and self.product_inventory[product_id] >= quantity:
            self.product_inventory[product_id] -= quantity
            return True
        else:
            return False

    def release_product(self, product):
        product_id = product['product_id']
        quantity = product['oper_product_quantity']

        if product_id in self.product_inventory:
            self.product_inventory[product_id] += quantity
        else:
            self.product_inventory[product_id] = quantity

    def check_product_availability(self, product):
        product_id = product['product_id']
        quantity = product['oper_product_quantity']

        if product_id in self.product_inventory and self.product_inventory[product_id] >= quantity:
            return True
        else:
            return False

    def bind_handlers(self):
        self.bind('REP', alias='reserve_product', handler=self.reserve_product)
        self.bind('REP', alias='release_product', handler=self.release_product)
        self.bind('REP', alias='check_product_availability', handler=self.check_product_availability)


class ProductAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.product_id = None
        self.product_type = None
        self.quantity = None
        self.task_completed = False

    def on_init(self):
        self.bind_handlers()

    def create_product(self, product_id, product_type, quantity):
        self.product_id = product_id
        self.product_type = product_type
        self.quantity = quantity

    def consume_product(self, quantity):
        if quantity <= self.quantity:
            self.quantity -= quantity
            if self.quantity == 0:
                self.task_completed = True
        else:
            raise ValueError("Not enough quantity of the product")

    def return_product(self, quantity):
        self.quantity += quantity
        self.task_completed = True

    def get_product_id(self):
        return self.product_id

    def get_product_type(self):
        return self.product_type

    def get_quantity(self):
        return self.quantity

    def bind_handlers(self):
        self.bind('REP', alias='consume_product', handler=self.consume_product)
        self.bind('REP', alias='return_product', handler=self.return_product)
        self.bind('REP', alias='get_product_id', handler=self.get_product_id)
        self.bind('REP', alias='get_product_type', handler=self.get_product_type)
        self.bind('REP', alias='get_quantity', handler=self.get_quantity)


class ChefAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.current_dish = None
        self.busy = False

    def on_init(self):
        self.bind_handlers()

    def prepare_dish(self, dish_agent):
        if not self.busy:
            self.current_dish = dish_agent
            self.busy = True
            self.current_dish.connect(self.addr('dish_completed'), handler=self.dish_completed)
            self.current_dish.send(self.addr('dish_completed'), 'start_preparing')
        else:
            raise ValueError("Chef is already preparing a dish.")

    def dish_completed(self, message):
        dish_agent = message
        self.busy = False
        self.current_dish = None

        # Notify the process agent that the dish is completed
        process_agent = dish_agent.get_attr('process_agent')
        process_agent.connect(self.addr('chef_dish_completed'), handler=process_agent.dish_completed)
        process_agent.send(self.addr('chef_dish_completed'), dish_agent)

    def bind_handlers(self):
        self.bind('REP', alias='prepare_dish', handler=self.prepare_dish)
        self.bind('REP', alias='dish_completed', handler=self.dish_completed)
        self.bind('REP', alias='chef_dish_completed', handler=self.dish_completed)


class EquipmentAgent(osbrain.Agent):
    def __init__(self, name='', host=None, serializer=None, transport=None,
                 attributes=None):
        super().__init__(name, host, serializer, transport, attributes)
        self.equipment_type = self.get_attr('equipment_type')
        self.status = 'free'
        self.current_task = None

    def on_init(self):
        self.bind_handlers()

    def assign_task(self, task):
        if self.status == 'free':
            self.current_task = task
            self.status = 'busy'
            return f"Equipment {self.name} assigned task {task}."
        else:
            return f"Equipment {self.name} is already busy with task {self.current_task}."

    def release(self):
        if self.status == 'busy':
            self.status = 'free'
            task = self.current_task
            self.current_task = None
            return f"Equipment {self.name} released from task {task}."
        else:
            return f"Equipment {self.name} is already free."

    def bind_handlers(self):
        self.bind('REP', alias='assign_task', handler=self.assign_task)
        self.bind('REP', alias='release', handler=self.release)

