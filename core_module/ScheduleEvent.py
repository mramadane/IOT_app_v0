class ScheduledEvent:
    def __init__(self, time: float, agent: 'Agent'):
        self.time = time
        self.agent = agent

    def __lt__(self, other: 'ScheduledEvent'):
        return self.time < other.time