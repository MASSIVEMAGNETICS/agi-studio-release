from core.node_base import NodeBase

class LanguageModel(NodeBase):
    def run(self, input_data):
        prompt = input_data.get("prompt", "Say something!")
        # You’d plug in your GPT, LLama, or Victor model here
        output = f"Echo: {prompt}"  # replace with actual model call
        self.outputs = {"text": output}
        self.log_event(f"Generated output: {output}")
        return self.outputs
