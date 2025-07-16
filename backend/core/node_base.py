class NodeBase:
    def __init__(self, node_id, config):
        self.node_id = node_id
        self.config = config
        self.inputs = {}
        self.outputs = {}
        self.state = "IDLE"
        self.log = []

    def run(self, input_data=None):
        raise NotImplementedError

    def stop(self):
        self.state = "IDLE"

    def log_event(self, msg):
        self.log.append(msg)
        print(f"[{self.node_id}] {msg}")

    def get_output(self):
        return self.outputs
