
import unittest
import numpy as np
import sys
import os

# Ensure victor_kernel can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from victor_transformer import FractalSelfAttention
from victor_kernel import OmegaTensor

class TestFractalSelfAttention(unittest.TestCase):
    def test_mask_expansion(self):
        """
        Test that mask expansion works correctly for multiple heads.
        Regression test for: mask is (B, 1, N, N) -> need to expand for heads
        """
        # Setup
        B = 2
        n_heads = 4
        d_model = 16
        N = 10
        fractal_depth = 1

        # Initialize FractalSelfAttention
        attn = FractalSelfAttention(d_model=d_model, n_heads=n_heads, fractal_depth=fractal_depth)

        # Input tensor (B, N, C)
        x = OmegaTensor(np.random.randn(B, N, d_model), requires_grad=False)

        # Mask (B, 1, N, N)
        # Let's say we mask out the last token
        mask = np.ones((B, 1, N, N))
        # Some mask values are 0 (masked)
        mask[:, :, :, -1] = 0

        # This calls __call__ which contains the issue
        # It should not raise IndexError
        try:
            output = attn(x, mask)
        except IndexError as e:
            self.fail(f"FractalSelfAttention raised IndexError with mask: {e}")
        except Exception as e:
            self.fail(f"FractalSelfAttention raised unexpected exception: {e}")

        # Basic shape check
        self.assertEqual(output.shape, (B, N, d_model))

if __name__ == "__main__":
    unittest.main()
