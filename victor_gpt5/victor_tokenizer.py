import os
import sentencepiece as spm
from typing import List, Dict, Any

class VictorTokenizer:
    """
    A multimodal, fractal-aware tokenizer for Victor-GPT5.
    It combines a SentencePiece model for text with special control tokens
    for other modalities like images, audio, and code.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config['tokenizer']
        self.model_path = self.config['model_path']
        self.sp = spm.SentencePieceProcessor()
        self._trained = False

        if os.path.exists(self.model_path):
            self.sp.load(self.model_path)
            self._trained = True

        self.special_tokens = self.config['special_tokens']
        self.token_to_id = {token: i for i, token in enumerate(self.special_tokens)}
        self.id_to_token = {i: token for token, i in self.token_to_id.items()}

        if self._trained:
            for i in range(self.sp.get_piece_size()):
                token = self.sp.id_to_piece(i)
                if token not in self.token_to_id:
                    self.token_to_id[token] = len(self.token_to_id)
                    self.id_to_token[len(self.id_to_token)] = token

        # Add special tokens to token_to_id map if not present
        for token in self.special_tokens:
            if token not in self.token_to_id:
                new_id = len(self.token_to_id)
                self.token_to_id[token] = new_id
                self.id_to_token[new_id] = token


    def train(self, text_corpus_path: str):
        """
        Trains the SentencePiece model.
        """
        if self._trained:
            print("Tokenizer already trained. Skipping.")
            return

        model_prefix = self.model_path.replace('.model', '')
        vocab_size = self.config['vocab_size']
        user_defined_symbols = ','.join(self.special_tokens)

        command = (
            f'--input={text_corpus_path} --model_prefix={model_prefix} '
            f'--vocab_size={vocab_size} --model_type=bpe '
            f'--user_defined_symbols={user_defined_symbols}'
        )
        try:
            spm.SentencePieceTrainer.train(command)
            self.sp.load(self.model_path)
            self._trained = True
            print("Tokenizer training complete.")
        except Exception as e:
            print(f"Error training tokenizer: {e}")
            raise

    def encode(self, text: str, encode_special_tokens=True) -> List[int]:
        """
        Encodes a string of text into a list of token IDs.
        Handles special tokens by splitting the text and encoding segments.
        """
        if not self._trained:
            raise RuntimeError("Tokenizer has not been trained or loaded.")

        # Simple recursive segmentation (fractal concept)
        def fractal_encode(segment: str):
            # Base case: segment is a special token
            if encode_special_tokens and segment in self.token_to_id:
                 return [self.token_to_id[segment]]
            # Recursive step: encode with sentencepiece
            return self.sp.encode_as_ids(segment)

        # Naive split by special tokens to handle them correctly
        # A more robust solution would use regex with lookarounds
        import re
        pattern = f"({'|'.join(re.escape(token) for token in self.special_tokens)})"
        parts = re.split(pattern, text)

        encoded_ids = []
        for part in parts:
            if part: # a part could be an empty string
                encoded_ids.extend(fractal_encode(part))

        return encoded_ids


    def decode(self, token_ids: List[int]) -> str:
        """
        Decodes a list of token IDs back into a string.
        """
        if not self._trained:
            raise RuntimeError("Tokenizer has not been trained or loaded.")

        # Filter out special tokens that are handled by the main tokenizer
        sp_ids = []
        decoded_parts = []

        for token_id in token_ids:
            if token_id in self.id_to_token and self.id_to_token[token_id] in self.special_tokens:
                 if sp_ids:
                     decoded_parts.append(self.sp.decode_ids(sp_ids))
                     sp_ids = []
                 decoded_parts.append(self.id_to_token[token_id])
            else:
                 sp_ids.append(token_id)

        if sp_ids:
            decoded_parts.append(self.sp.decode_ids(sp_ids))

        return "".join(decoded_parts)

    @property
    def vocab_size(self):
        return len(self.token_to_id)

    def token_to_id_map(self):
        return self.token_to_id

    def id_to_token_map(self):
        return self.id_to_token

# Example Usage (self-contained test)
if __name__ == '__main__':
    # Create dummy config and corpus for demonstration
    dummy_config = {
        'tokenizer': {
            'model_path': './victor_gpt5/data/victor_tokenizer.model',
            'vocab_size': 100,
            'special_tokens': ['[PAD]', '[UNK]', '[IMG_START]', '[IMG_END]']
        }
    }
    dummy_corpus_path = './victor_gpt5/data/dummy_corpus.txt'
    with open(dummy_corpus_path, 'w') as f:
        f.write("The quick brown fox jumps over the lazy dog.\n")
        f.write("This is a test for the VictorTokenizer.\n")

    tokenizer = VictorTokenizer(dummy_config)

    if not tokenizer._trained:
        print("Training tokenizer...")
        tokenizer.train(dummy_corpus_path)

    print(f"Tokenizer vocab size: {tokenizer.vocab_size}")

    text = "Here is an image: [IMG_START]...data...[IMG_END]. What do you see?"
    encoded = tokenizer.encode(text)
    print(f"Original: {text}")
    print(f"Encoded: {encoded}")

    decoded = tokenizer.decode(encoded)
    print(f"Decoded: {decoded}")

    assert decoded == text
    print("\nVictorTokenizer self-test PASSED.")
