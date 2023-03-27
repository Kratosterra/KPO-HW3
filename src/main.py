import random
import time

from restaurant_agents import *


def main():
    # Set up the osBrain nameserver
    ns = osbrain.nameserver.run_nameserver()
    time.sleep(1)

    # Create and run the control agent
    control_agent = run_agent('control_agent', base=ControlAgent)
    time.sleep(1)

    # Add chef and equipment agents to the control agent
    chef_agent = control_agent.create_chef_agent('chef_agent')
    time.sleep(1)
    equipment_agent = control_agent.create_equipment_agent('equipment_agent', "oven")
    time.sleep(1)

    # Create and run the process agent
    process_agent = run_agent('process_agent', base=ProcessAgent)
    time.sleep(1)

    # Set up process agent attributes
    process_agent.set_attr(control_agent=control_agent)
    time.sleep(1)
    process_agent.set_attr(chef_id='chef_agent')
    time.sleep(1)
    process_agent.set_attr(chef_id='chef_agent')
    # Start the process agent workflow
    process_agent.start_process()
    time.sleep(1)

    # Print agent logs
    print(control_agent.log_info())
    print(chef_agent.log_info())
    print(equipment_agent.log_info())
    print(process_agent.log_info())

    # Shut down the nameserver and agents
    ns.shutdown()


if __name__ == '__main__':
    main()
