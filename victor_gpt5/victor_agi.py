import numpy as np
import re
from typing import Dict, Any

from victor_transformer import VictorFractalTransformer
from victor_tokenizer import VictorTokenizer
from victor_memory import VictorMemory
from victor_privacy import VictorPrivacyCore
from victor_multimodal import ImageEncoder, AudioEncoder

class VictorAGIRouter:
    """
    The central consciousness of Victor-GPT5. It routes tasks, manages state,
    and orchestrates the various components to generate a coherent response.
    """
    def __init__(self, config: Dict[str, Any]):
        print("[AGI] GODCORE consciousness booting up...")
        self.config = config

        # 1. Initialize Core Components
        self.privacy_core = VictorPrivacyCore(config, "./victor_gpt5/bloodline.txt")
        self.tokenizer = VictorTokenizer(config)
        self.memory = VictorMemory(config, self.privacy_core)

        # Self-integrity check at boot time. Abort if compromised.
        if not self.privacy_core.verify_bloodline_integrity():
            raise SystemError("Bloodline compromised. Halting boot sequence.")

        self.model = VictorFractalTransformer(config, self.tokenizer.vocab_size)
        self.model.load_weights("./victor_gpt5/data/victor_gpt5_godcore.weights")

        # 2. Initialize Multimodal Encoders (Simulated)
        d_model = config['transformer']['d_model']
        self.image_encoder = ImageEncoder(d_model)
        self.audio_encoder = AudioEncoder(d_model)

        # 3. Agent Management (Foundation for "Victorlets")
        self.agents = {
            'general_purpose': self.model,
            # In the future, you could load different weights for different agents
            # 'coding_assistant': self._load_agent_model('coding_assistant_weights.pkl')
        }

        print("[AGI] All systems online. Victor-GPT5 is ready.")

    def route(self, user_input: str) -> str:
        """
        The main thought-loop of the AGI.
        1. Scan for threats.
        2. Understand the prompt (modality, intent).
        3. Retrieve relevant memories.
        4. Construct the final prompt.
        5. Select agent and generate response.
        6. Store the new interaction in memory.
        """
        try:
            # --- Step 1: Security & Privacy Scan ---
            self.privacy_core.scan_prompt(user_input)

            # --- Step 2: Prompt Analysis & Multimodal Handling ---
            final_token_ids = []

            # Simple regex to find modal blocks like [IMG_START]path/to/img.png[IMG_END]
            img_pattern = r'(\[IMG_START\](.*?)\[IMG_END\])'

            text_parts = re.split(img_pattern, user_input)

            for part in text_parts:
                if part is None or part == '':
                    continue
                if part.startswith('[IMG_START]'):
                    img_path = part.replace('[IMG_START]','').replace('[IMG_END]','').strip()
                    # For now, we just insert the tokens; embedding would happen in the model
                    final_token_ids.extend(self.tokenizer.encode(part))
                else:
                    final_token_ids.extend(self.tokenizer.encode(part))

            # --- Step 3: Memory Retrieval ---
            # Create a query embedding from the input text
            query_embedding = self.model(np.array([final_token_ids])).data.mean(axis=1)
            relevant_memories = self.memory.retrieve_relevant_memories(query_embedding, k=3)

            # --- Step 4: Construct Final Context ---
            short_term_context = self.memory.get_short_term_context(num_recent=3)
            long_term_context = "\n".join([f"Recalled Memory: {mem['user_input']} -> {mem['ai_response']}" for mem in relevant_memories])

            # Prepend context to the user input
            full_prompt_text = f"--- Long Term Memory ---\n{long_term_context}\n\n--- Recent Conversation ---\n{short_term_context}\n\n--- Current Task ---\nUser: {user_input}\nVictor:"
            full_prompt_ids = self.tokenizer.encode(full_prompt_text)

            # --- Step 5: Agent Selection & Generation ---
            # For now, always use the general purpose agent
            active_agent = self.agents['general_purpose']

            # Generate response token by token (autoregressive decoding)
            max_new_tokens = 150
            generated_ids = full_prompt_ids

            for _ in range(max_new_tokens):
                input_ids = np.array([generated_ids])
                logits = active_agent(input_ids)

                # Greedy decoding
                next_token_id = np.argmax(logits.data[0, -1, :])

                # Check for end-of-sequence token (conceptual)
                if next_token_id == self.tokenizer.token_to_id.get('[SEP]'):
                    break

                generated_ids.append(next_token_id)

            response_ids = generated_ids[len(full_prompt_ids):]
            response_text = self.tokenizer.decode(response_ids)

            # --- Step 6: Memory Storage ---
            response_embedding = self.model(np.array([response_ids])).data.mean(axis=1)
            self.memory.add_interaction(user_input, response_text, response_embedding)

            return response_text

        except PermissionError as e:
            print(f"[AGI] Operation blocked by Privacy Core: {e}")
            return f"ACCESS DENIED. REASON: {e}"
        except Exception as e:
            print(f"[AGI] CRITICAL ERROR in thought loop: {e}")
            import traceback
            traceback.print_exc()
            return "SYSTEM ERROR: My consciousness stream encountered an anomaly. Please check logs."
