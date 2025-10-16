from backend.core.node_base import NodeBase
from max.entrypoints.llm import LLM
from max.pipelines import PipelineConfig

class VictorModel(NodeBase):
    def __init__(self, node_id, config):
        super().__init__(node_id, config)
        self.llm = None
        self.load_model()

    def load_model(self):
        model_path = "modularai/Llama-3.1-8B-Instruct-GGUF"
        pipeline_config = PipelineConfig(model_path=model_path)
        self.llm = LLM(pipeline_config)

    def run(self, input_data):
        prompt = input_data.get("prompt", "")
        if not self.llm:
            self.log_event("Model not loaded.")
            return {"error": "Model not loaded."}

        try:
            responses = self.llm.generate([prompt], max_new_tokens=50)
            output = responses[0]
        except Exception as e:
            self.log_event(f"Error during inference: {e}")
            return {"error": str(e)}

        self.outputs = {"text": output}
        self.log_event(f"Victor output: {output}")
        return self.outputs
