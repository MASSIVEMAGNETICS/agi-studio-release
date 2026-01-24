import numpy as np
import os
from typing import Any, Optional, Tuple, List
from victor_kernel import OmegaTensor
from victor_transformer import TransformerBlock, Linear, Module

class BaseEncoder(Module):
    """Base class for a modality-specific encoder."""
    def __init__(self, output_dim):
        super().__init__()
        self.output_dim = output_dim

    def encode(self, data: Any) -> OmegaTensor:
        """Encodes raw data into a tensor embedding."""
        raise NotImplementedError

class ImageEncoder(BaseEncoder):
    """
    A simple Vision Transformer (ViT) based image encoder.
    """
    def __init__(self, output_dim: int, patch_size: int = 16, d_model: int = 256, n_layers: int = 2):
        super().__init__(output_dim)
        self.patch_size = patch_size
        self.d_model = d_model
        self.output_dim = output_dim

        # Patch embedding: linear projection of flattened patches
        # Input channels assumed to be 3 (RGB)
        patch_dim = patch_size * patch_size * 3
        self.patch_projection = Linear(patch_dim, d_model)

        # Positional embedding (learnable, fixed max size)
        # Assuming max image size 224x224 -> (224/16)^2 = 196 patches
        max_patches = (224 // patch_size) ** 2
        self.position_embedding = OmegaTensor(
            np.random.randn(max_patches + 1, d_model) * 0.02, # +1 for CLS token if we used it, but here we just use patches
            requires_grad=True
        )

        # Transformer blocks
        # Config: n_heads=4, d_ff=d_model*4, fractal_depth=1, n_experts=1, dropout=0.1
        self.blocks = [
            TransformerBlock(d_model=d_model, n_heads=4, d_ff=d_model*4, fractal_depth=1, n_experts=1, dropout=0.1)
            for _ in range(n_layers)
        ]
        for i, block in enumerate(self.blocks):
            self.__setattr__(f"block_{i}", block)

        # Final projection to output_dim
        self.output_projection = Linear(d_model, output_dim)

        print(f"[Multimodal] ImageEncoder initialized (Real ViT: patch_size={patch_size}, d_model={d_model}).")

    def encode(self, image_path_or_data: Any) -> OmegaTensor:
        """
        Encodes an image into a sequence of embeddings.
        Args:
            image_path_or_data: path to image (str) or numpy array (H, W, 3).
        """
        image_data = None

        # Handle file path
        if isinstance(image_path_or_data, str):
            try:
                from PIL import Image
                img = Image.open(image_path_or_data).convert('RGB')
                img = img.resize((224, 224)) # Resize to standard size
                image_data = np.array(img) / 255.0 # Normalize to [0, 1]
            except ImportError:
                print(f"[Multimodal] Warning: PIL not installed. Cannot load image from path '{image_path_or_data}'.")
                raise
            except Exception as e:
                print(f"[Multimodal] Error loading image: {e}")
                raise
        elif isinstance(image_path_or_data, np.ndarray):
            image_data = image_path_or_data
            # Basic validation
            if len(image_data.shape) == 3:
                # Expected H, W, C
                if np.issubdtype(image_data.dtype, np.integer):
                    image_data = image_data.astype(np.float32) / 255.0
                elif image_data.max() > 1.0:
                    image_data = image_data / 255.0 # Normalize if likely in 0-255 range
            else:
                 raise ValueError(f"Expected image data of shape (H, W, 3), got {image_data.shape}")
        else:
            raise TypeError("Input must be a file path string or numpy array.")

        # Ensure correct shape for patching
        H, W, C = image_data.shape
        if H % self.patch_size != 0 or W % self.patch_size != 0:
            # Simple resize/crop logic or error. For now, strict error or padding is better.
            # We'll rely on user providing correct size or resizing logic above.
            # If came from np array, might not be 224x224.
            # Let's crop to nearest multiple
            H_new = (H // self.patch_size) * self.patch_size
            W_new = (W // self.patch_size) * self.patch_size
            image_data = image_data[:H_new, :W_new, :]
            H, W = H_new, W_new

        # Patchify
        # (H, W, C) -> (H//P, P, W//P, P, C) -> (H//P * W//P, P*P*C)
        h_patches = H // self.patch_size
        w_patches = W // self.patch_size
        num_patches = h_patches * w_patches

        patches = image_data.reshape(h_patches, self.patch_size, w_patches, self.patch_size, C)
        patches = patches.transpose(0, 2, 1, 3, 4)
        patches = patches.reshape(num_patches, -1) # (N, P*P*C)

        x = OmegaTensor(patches)

        # Projection
        x = self.patch_projection(x) # (N, d_model)

        # Add position embedding
        # Truncate or interpolate pos embedding if needed. Here we just take up to N.
        if num_patches > self.position_embedding.shape[0]:
             # Raise warning or truncate input?
             # For now, just slice and hope for best (or crash if too small)
             print(f"[Multimodal] Warning: Image too large, truncating to {self.position_embedding.shape[0]} patches.")
             # Slice x using OmegaTensor slicing to preserve gradient if x had history (it doesn't here, but good practice)
             x = x[:self.position_embedding.shape[0]]
             num_patches = self.position_embedding.shape[0]

        # We need to add batch dimension for TransformerBlock?
        # TransformerBlock expects (B, N, C). Here we have (N, C).
        # We can treat this as batch size 1.
        x = x.reshape(1, num_patches, self.d_model)

        # Add Pos Embed
        # Use slicing to preserve gradient on position_embedding
        pos_slice = self.position_embedding[:num_patches]
        pos = pos_slice.reshape(1, num_patches, self.d_model)
        x = x + pos

        # Transformer Blocks
        for block in self.blocks:
            x = block(x)

        # x is (1, N, d_model)

        # Final projection to output_dim.
        # We return sequence of embeddings (per patch) or global?
        # The BaseEncoder says "output a sequence of embeddings".
        # But previous simulation returned (16, output_dim).

        x = self.output_projection(x) # (1, N, output_dim)

        # Remove batch dim
        x = x.reshape(num_patches, self.output_dim)

        return x

class AudioEncoder(BaseEncoder):
    """
    Placeholder for an audio encoder (e.g., a Wav2Vec model).
    This module would take an audio waveform and output embeddings.
    """
    def __init__(self, output_dim: int):
        super().__init__(output_dim)
        print("[Multimodal] AudioEncoder initialized (simulation mode).")

    def encode(self, audio_waveform: np.ndarray) -> OmegaTensor:
        """Simulates encoding audio into embeddings."""
        # Real implementation: Use a model to process the waveform.
        print(f"[Multimodal] 'Encoding' audio of shape: {audio_waveform.shape}")
        # Simulate one token per 1600 audio samples (e.g., at 16kHz)
        num_tokens = len(audio_waveform) // 1600
        simulated_embedding = np.random.randn(num_tokens, self.output_dim)
        return OmegaTensor(simulated_embedding)
