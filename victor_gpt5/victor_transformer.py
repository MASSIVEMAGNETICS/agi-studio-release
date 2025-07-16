import numpy as np
from typing import Dict, Any, List, Optional

# Assumes victor_kernel.py is in the same path
from victor_kernel import OmegaTensor, relu, softmax, MatMul, Add, Mul, Sum, Reshape

# --- Base Module Class ---
class Module:
    """Base class for all neural network modules."""
    def __init__(self):
        self._parameters: Dict[str, OmegaTensor] = {}

    def parameters(self) -> List[OmegaTensor]:
        params = []
        for name, param in self._parameters.items():
            params.append(param)

        # Recursively get params from submodules
        for attr_name in self.__dict__:
            attr = self.__dict__[attr_name]
            if isinstance(attr, Module):
                params.extend(attr.parameters())
        return params

    def __setattr__(self, key, value):
        if isinstance(value, OmegaTensor):
            self._parameters[key] = value
        elif isinstance(value, Module):
            # This is a submodule
            pass
        super().__setattr__(key, value)

    def zero_grad(self):
        for p in self.parameters():
            p.zero_grad()

# --- Core Building Blocks ---
class Linear(Module):
    """A standard fully-connected layer."""
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        # Kaiming He initialization
        self.weight = OmegaTensor(
            np.random.randn(in_features, out_features) * np.sqrt(2.0 / in_features),
            requires_grad=True
        )
        if bias:
            self.bias = OmegaTensor(np.zeros(out_features), requires_grad=True)
        else:
            self.bias = None

    def __call__(self, x: OmegaTensor) -> OmegaTensor:
        output = x.matmul(self.weight)
        if self.bias is not None:
            output = output + self.bias
        return output

class LayerNorm(Module):
    """Layer normalization."""
    def __init__(self, normalized_shape: int, eps: float = 1e-5):
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.gamma = OmegaTensor(np.ones(normalized_shape), requires_grad=True)
        self.beta = OmegaTensor(np.zeros(normalized_shape), requires_grad=True)

    def __call__(self, x: OmegaTensor) -> OmegaTensor:
        mean = x.data.mean(axis=-1, keepdims=True)
        var = x.data.var(axis=-1, keepdims=True)

        x_norm = (x - OmegaTensor(mean)) * OmegaTensor((var + self.eps) ** -0.5)
        return self.gamma * x_norm + self.beta

class Dropout:
    """Dropout layer."""
    def __init__(self, p: float = 0.5):
        self.p = p
        self.is_training = True

    def __call__(self, x: OmegaTensor) -> OmegaTensor:
        if not self.is_training or self.p == 0:
            return x
        mask = (np.random.rand(*x.shape) > self.p) / (1.0 - self.p)
        return x * OmegaTensor(mask)

# --- The Fractal Attention Mechanism ---
class FractalSelfAttention(Module):
    """
    A recursive, fractal self-attention mechanism.
    This implementation simplifies the fractal concept into a recursive refinement loop.
    A true fractal would involve hierarchical partitioning of the sequence.
    """
    def __init__(self, d_model: int, n_heads: int, fractal_depth: int):
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.fractal_depth = fractal_depth

        self.qkv_proj = Linear(d_model, d_model * 3)
        self.out_proj = Linear(d_model, d_model)

    def __call__(self, x: OmegaTensor, mask: Optional[np.ndarray] = None) -> OmegaTensor:
        # Initial projection
        B, N, C = x.shape
        qkv = self.qkv_proj(x).reshape(B, N, 3, self.n_heads, self.d_k)
        q, k, v = qkv.data.transpose(2, 0, 1, 3, 4) # 3, B, N, n_heads, d_k

        q = OmegaTensor(q.transpose(0, 2, 1, 3).reshape(B*self.n_heads, N, self.d_k))
        k = OmegaTensor(k.transpose(0, 2, 1, 3).reshape(B*self.n_heads, N, self.d_k))
        v = OmegaTensor(v.transpose(0, 2, 1, 3).reshape(B*self.n_heads, N, self.d_k))

        # Recursive/Iterative Refinement
        for _ in range(self.fractal_depth):
            attn_scores = q.matmul(k.transpose(0, 2, 1)) * (self.d_k ** -0.5)

            if mask is not None:
                # attn_scores is (B*n_heads, N, N)
                # mask is (B, 1, N, N) -> need to expand for heads
                head_mask = np.repeat(mask, self.n_heads, axis=0)
                attn_scores.data[head_mask == 0] = -1e9

            attn_probs = softmax(attn_scores, axis=-1)
            context = attn_probs.matmul(v)

            # For the next iteration, refine Q with the context
            # This is a simplified refinement step
            q = (q + context) * 0.5

        # Final context
        context = context.reshape(B, self.n_heads, N, self.d_k).transpose(0, 2, 1, 3).reshape(B, N, C)

        return self.out_proj(context)

# --- Mixture of Experts ---
class MoeLayer(Module):
    """A simple Mixture-of-Experts layer."""
    def __init__(self, d_model: int, d_ff: int, n_experts: int):
        super().__init__()
        self.n_experts = n_experts
        self.gate = Linear(d_model, n_experts)
        self.experts = [
            Linear(d_model, d_ff) for _ in range(n_experts)
        ]
        self.expert_outputs = [
            Linear(d_ff, d_model) for _ in range(n_experts)
        ]
        # Add experts to parameters
        for i, expert in enumerate(self.experts):
            self.__setattr__(f"expert_fc1_{i}", expert)
        for i, expert_out in enumerate(self.expert_outputs):
            self.__setattr__(f"expert_fc2_{i}", expert_out)


    def __call__(self, x: OmegaTensor) -> OmegaTensor:
        B, N, C = x.shape
        gate_logits = self.gate(x)
        gate_probs = softmax(gate_logits, axis=-1) # (B, N, n_experts)

        final_output = OmegaTensor(np.zeros_like(x.data))

        # This is a simplified, non-parallel version.
        # In a real system, this would use parallel expert execution.
        for i in range(self.n_experts):
            expert_in = relu(self.experts[i](x))
            expert_out = self.expert_outputs[i](expert_in)

            # Weight expert output by gate probability
            gating = gate_probs.data[:, :, i].reshape(B, N, 1)
            final_output += expert_out * OmegaTensor(gating)

        return final_output

# --- The Transformer Block ---
class TransformerBlock(Module):
    """A single block of the Victor Fractal Transformer."""
    def __init__(self, d_model: int, n_heads: int, d_ff: int, fractal_depth: int, n_experts:int, dropout: float):
        super().__init__()
        self.attention = FractalSelfAttention(d_model, n_heads, fractal_depth)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.moe = MoeLayer(d_model, d_ff, n_experts)
        self.dropout = Dropout(dropout)

    def __call__(self, x: OmegaTensor, mask: Optional[np.ndarray] = None) -> OmegaTensor:
        # Attention -> Add & Norm
        attn_out = self.attention(x, mask)
        x = self.norm1(x + self.dropout(attn_out))

        # MoE -> Add & Norm
        moe_out = self.moe(x)
        x = self.norm2(x + self.dropout(moe_out))
        return x

# --- The Full Model ---
class VictorFractalTransformer(Module):
    """The complete Victor-GPT5 GODCORE model."""
    def __init__(self, config: Dict[str, Any], vocab_size: int):
        super().__init__()
        self.config = config['transformer']
        self.vocab_size = vocab_size

        d_model = self.config['d_model']
        n_layers = self.config['n_layers']
        n_heads = self.config['n_heads']
        d_ff = self.config['d_ff']
        fractal_depth = self.config['fractal_depth']
        n_experts = self.config['moe_experts']
        dropout = self.config['dropout']
        self.context_window = self.config['context_window']

        self.token_embedding = OmegaTensor(
            np.random.randn(vocab_size, d_model) * 0.02,
            requires_grad=True
        )
        self.position_embedding = OmegaTensor(
            np.random.randn(self.context_window, d_model) * 0.02,
            requires_grad=True
        )

        self.layers = [
            TransformerBlock(d_model, n_heads, d_ff, fractal_depth, n_experts, dropout)
            for _ in range(n_layers)
        ]
        # Add layers to parameters
        for i, layer in enumerate(self.layers):
            self.__setattr__(f"layer_{i}", layer)

        self.output_norm = LayerNorm(d_model)
        self.output_head = Linear(d_model, vocab_size)

    def __call__(self, token_ids: np.ndarray, mask: Optional[np.ndarray] = None) -> OmegaTensor:
        B, N = token_ids.shape
        assert N <= self.context_window, "Input sequence exceeds context window"

        # Embeddings
        tok_embed = OmegaTensor(self.token_embedding.data[token_ids])
        pos_embed = OmegaTensor(self.position_embedding.data[:N])
        x = tok_embed + pos_embed

        # Transformer Blocks
        for layer in self.layers:
            x = layer(x, mask)

        # Output Head
        x = self.output_norm(x)
        logits = self.output_head(x)
        return logits

    def save_weights(self, path: str):
        """Saves all model parameters to a file."""
        with open(path, 'wb') as f:
            pickle.dump([p.data for p in self.parameters()], f)
        print(f"Model weights saved to {path}")

    def load_weights(self, path: str):
        """Loads model parameters from a file."""
        if not os.path.exists(path):
            print(f"Warning: Weight file not found at {path}. Initializing with random weights.")
            return
        with open(path, 'rb') as f:
            weights = pickle.load(f)

        params = self.parameters()
        if len(weights) != len(params):
            raise ValueError(f"Mismatched number of parameters. Expected {len(params)}, got {len(weights)}")

        for p, w in zip(params, weights):
            p.data = w
        print(f"Model weights loaded from {path}")
