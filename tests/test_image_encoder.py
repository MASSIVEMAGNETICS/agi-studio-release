import numpy as np
import sys
import os
import unittest

# Ensure we can import modules from victor_gpt5 directory
# assuming the script is run from repo root
current_dir = os.getcwd()
victor_dir = os.path.join(current_dir, 'victor_gpt5')
if victor_dir not in sys.path:
    sys.path.append(victor_dir)

from victor_gpt5.victor_multimodal import ImageEncoder
from victor_kernel import OmegaTensor

class TestImageEncoder(unittest.TestCase):
    def test_initialization(self):
        print("Testing initialization...")
        encoder = ImageEncoder(output_dim=512)
        self.assertIsInstance(encoder, ImageEncoder)
        self.assertEqual(encoder.output_dim, 512)

    def test_encode_numpy(self):
        print("Testing encoding numpy array...")
        encoder = ImageEncoder(output_dim=512, patch_size=16, d_model=64) # Small d_model for speed

        # 224x224 RGB image
        img = np.random.rand(224, 224, 3).astype(np.float32)

        embedding = encoder.encode(img)

        self.assertIsInstance(embedding, OmegaTensor)

        # Expected patches: (224/16) * (224/16) = 14 * 14 = 196
        expected_shape = (196, 512)
        self.assertEqual(embedding.shape, expected_shape)

    def test_encode_numpy_irregular_shape(self):
        print("Testing encoding irregular numpy array (should be cropped)...")
        encoder = ImageEncoder(output_dim=128, patch_size=16, d_model=32)

        # 100x100 RGB image. 100 is not divisible by 16 (16*6=96). Should crop to 96x96.
        img = np.random.rand(100, 100, 3).astype(np.float32)

        embedding = encoder.encode(img)

        # Expected patches: (96/16) * (96/16) = 6 * 6 = 36
        expected_shape = (36, 128)
        self.assertEqual(embedding.shape, expected_shape)

    def test_backward_pass(self):
        print("Testing backward pass capability...")
        encoder = ImageEncoder(output_dim=10, patch_size=16, d_model=32)

        # Create a small image
        img = np.random.rand(32, 32, 3).astype(np.float32) # 4 patches

        # Run forward
        embedding = encoder.encode(img) # (4, 10)

        # Create a dummy loss
        loss = embedding.sum()

        # Run backward
        loss.backward()

        # Check if patch projection weights have gradients
        self.assertIsNotNone(encoder.patch_projection.weight.grad)
        self.assertTrue(np.any(encoder.patch_projection.weight.grad != 0))

        # Check if position embeddings have gradients (CRITICAL CHECK for the fix)
        self.assertIsNotNone(encoder.position_embedding.grad)
        # We used 4 patches. The first 4 position embeddings should have gradients.
        # The position embedding shape is (max_patches+1, d_model).
        # We need to ensure at least some gradients are non-zero.
        # Note: Depending on optimization, unused embeddings might have 0 grad, but used ones should have grad.
        # The gradient is initialized to zeros. If backward works, it accumulates.

        # We used first 4 patches.
        grad_slice = encoder.position_embedding.grad[:4]
        self.assertTrue(np.any(grad_slice != 0), "Position embeddings did not receive gradients!")

if __name__ == "__main__":
    unittest.main()
