from core.node_base import NodeBase

class PipelineRunner:
    def __init__(self, graph_config):
        self.nodes = {}        # id -> NodeBase instance
        self.edges = []        # (from_id, to_id)
        self.state = "IDLE"
        self.log = []
        self.load_graph(graph_config)

    def load_graph(self, graph_config):
        # graph_config: Dict with nodes/edges, loaded from GUI export/import
        for node_def in graph_config["nodes"]:
            node_class = self._import_node(node_def["type"])
            node = node_class(node_def["id"], node_def.get("config", {}))
            self.nodes[node_def["id"]] = node
        self.edges = graph_config["edges"]

    def _import_node(self, node_type):
        # Dynamic import for built-in/custom/plugin nodes
        import importlib
        return getattr(importlib.import_module(f"nodes.{node_type}"), node_type)

    def run_pipeline(self, input_data={}):
        self.state = "RUNNING"
        # Topological sort: determine execution order from edges
        ordered_nodes = self._topo_sort()
        node_outputs = {}
        for node_id in ordered_nodes:
            node = self.nodes[node_id]
            inputs = {k: node_outputs.get(k) for k in node.inputs.keys()}
            node.state = "RUNNING"
            out = node.run(inputs)
            node_outputs[node_id] = out
            node.state = "IDLE"
        self.state = "IDLE"
        return node_outputs

    def _topo_sort(self):
        # (implement basic DAG topo sort)
        from collections import defaultdict, deque
        in_degree = defaultdict(int)
        graph = defaultdict(list)
        for src, dst in self.edges:
            graph[src].append(dst)
            in_degree[dst] += 1
        queue = deque([nid for nid in self.nodes if in_degree[nid] == 0])
        ordered = []
        while queue:
            nid = queue.popleft()
            ordered.append(nid)
            for nbr in graph[nid]:
                in_degree[nbr] -= 1
                if in_degree[nbr] == 0:
                    queue.append(nbr)
        return ordered

    def stop_pipeline(self):
        for node in self.nodes.values():
            node.stop()
        self.state = "IDLE"
