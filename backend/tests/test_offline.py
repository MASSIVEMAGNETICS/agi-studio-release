import unittest
from unittest.mock import patch, MagicMock
from backend.nodes.VictorModel import VictorModel

class TestOfflineBackend(unittest.TestCase):
    @patch("socket.socket")
    @patch("backend.nodes.VictorModel.PipelineConfig")
    @patch("backend.nodes.VictorModel.LLM")
    def test_victor_model_offline(self, mock_llm, mock_pipeline_config, mock_socket):
        # Prevent any network access
        mock_socket.side_effect = IOError("Network access is disabled.")

        # Mock PipelineConfig to do nothing
        mock_pipeline_config.return_value = MagicMock()

        # Mock the LLM's generate method
        mock_llm_instance = MagicMock()
        mock_llm_instance.generate.return_value = ["Paris is the capital of France."]
        mock_llm.return_value = mock_llm_instance

        # Initialize VictorModel
        victor_model = VictorModel(node_id="victor_test", config={})

        # Prepare a sample prompt
        prompt = {"prompt": "What is the capital of France?"}

        # Run the model
        output = victor_model.run(prompt)

        # Check for a valid response
        self.assertIn("text", output)
        self.assertEqual(output["text"], "Paris is the capital of France.")
        self.assertNotIn("error", output)

if __name__ == "__main__":
    unittest.main()
