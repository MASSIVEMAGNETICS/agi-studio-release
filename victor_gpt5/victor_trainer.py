import numpy as np
from typing import Dict, Any, List, Tuple

# Local imports
from victor_kernel import OmegaTensor, cross_entropy_loss
from victor_transformer import VictorFractalTransformer, LoraLayer # LoraLayer conceptual
from victor_tokenizer import VictorTokenizer

# Conceptual LoRA Layer to be injected
class LoraLayer(Module):
    def __init__(self, original_layer, r, alpha):
        super().__init__()
        self.original_layer = original_layer
        in_features, out_features = original_layer.weight.shape
        self.lora_A = OmegaTensor(np.random.randn(in_features, r) * 0.01, requires_grad=True)
        self.lora_B = OmegaTensor(np.zeros((r, out_features)), requires_grad=True)
        self.alpha = alpha
        self.r = r

    def __call__(self, x):
        original_output = self.original_layer(x)
        lora_output = (x @ self.lora_A @ self.lora_B) * (self.alpha / self.r)
        return original_output + lora_output

    def parameters(self):
        return [self.lora_A, self.lora_B]


class VictorTrainer:
    """Handles the training loop for pre-training or fine-tuning."""
    def __init__(self, model: VictorFractalTransformer, tokenizer: VictorTokenizer, config: Dict[str, Any]):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config['trainer']
        self.lr = self.config['learning_rate']

    def _prepare_batch(self, texts: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepares a batch of texts for training."""
        input_ids = [self.tokenizer.encode(text) for text in texts]

        # Simple padding
        max_len = max(len(ids) for ids in input_ids)
        padded_ids = np.zeros((len(input_ids), max_len), dtype=int)
        for i, ids in enumerate(input_ids):
            padded_ids[i, :len(ids)] = ids

        # For language modeling, target is the input shifted by one
        x = padded_ids[:, :-1]
        y = padded_ids[:, 1:]

        return x, y

    def train(self, corpus_path: str):
        """
        Runs a full training loop on a given text corpus.
        """
        print("\n--- [TRAINER] Starting GODCORE Self-Improvement Cycle ---")

        # --- Data Loading ---
        with open(corpus_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        batch_size = self.config['batch_size']
        epochs = self.config['epochs']

        # --- Optimizer (Simple SGD) ---
        params = self.model.parameters()

        for epoch in range(epochs):
            print(f"\n--- Epoch {epoch+1}/{epochs} ---")
            total_loss = 0

            # Simple batching
            for i in range(0, len(lines), batch_size):
                batch_texts = lines[i:i+batch_size]
                if not batch_texts: continue

                # --- Forward Pass ---
                self.model.zero_grad()
                x, y_true = self._prepare_batch(batch_texts)
                logits = self.model(x) # (B, N, V)

                # --- Calculate Loss ---
                # Reshape for cross entropy: (B*N, V) and (B*N,)
                B, N, V = logits.shape
                logits_flat = logits.reshape(B * N, V)
                y_true_flat = y_true.flatten()

                loss = cross_entropy_loss(logits_flat, y_true_flat)

                # --- Backward Pass ---
                loss.backward()

                # --- Update Weights (SGD) ---
                for p in params:
                    if p.grad is not None:
                        p.data -= self.lr * p.grad

                batch_loss = loss.data.item()
                total_loss += batch_loss
                print(f"  Batch {i//batch_size + 1}, Loss: {batch_loss:.4f}")

            avg_loss = total_loss / (len(lines) // batch_size)
            print(f"--- End of Epoch {epoch+1}, Average Loss: {avg_loss:.4f} ---")

        print("\n--- [TRAINER] Self-Improvement Cycle Complete. New knowledge integrated. ---")
        # Save the newly trained weights
        self.model.save_weights("./victor_gpt5/data/victor_gpt5_godcore.weights")
