from agent_client import AgentClient

class Task:
    @classmethod
    def create(clazz, host):
        agent = AgentClient(host)       
        return agent.start_task()

    @classmethod
    def delete(clazz, host, id):
        agent = AgentClient(host)
        return agent.stop_task(id)
