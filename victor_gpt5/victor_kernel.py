import numpy as np
import math
from typing import List, Optional, Tuple, Callable

# --- Core Operation Class ---
class Op:
    """Base class for an operation in the computation graph."""
    def __call__(self, *args):
        raise NotImplementedError

    def backward(self, grad_out: np.ndarray) -> Tuple[Optional[np.ndarray], ...]:
        raise NotImplementedError

# --- The OmegaTensor ---
class OmegaTensor:
    """A multi-dimensional array that supports automatic differentiation."""
    def __init__(self, data, requires_grad: bool = False, _creator: Optional[Tuple['Op', List['OmegaTensor']]] = None):
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=np.float32)
        self.data = data
        self.requires_grad = requires_grad
        self.grad: Optional[np.ndarray] = None
        self._creator = _creator

        if self.requires_grad and self._creator is None:
            # For leaf nodes that require gradients
            self.zero_grad()

    @property
    def shape(self) -> Tuple[int, ...]:
        return self.data.shape

    @property
    def dtype(self):
        return self.data.dtype

    def __repr__(self) -> str:
        return f"OmegaTensor({self.data}, requires_grad={self.requires_grad})"

    def set_creator(self, op: Op, *parents: 'OmegaTensor'):
        self._creator = (op, list(parents))

    def zero_grad(self):
        """Resets the gradient of the tensor to zero."""
        self.grad = np.zeros_like(self.data)

    def backward(self, grad_out: Optional[np.ndarray] = None):
        """
        Performs backpropagation starting from this tensor.
        """
        if not self.requires_grad:
            raise RuntimeError("Cannot call .backward() on a tensor that does not require grad.")

        if grad_out is None:
            if self.shape == (): # Scalar
                grad_out = np.array(1.0)
            else:
                raise RuntimeError("grad_out must be specified for non-scalar Tensors.")

        if self.grad is None:
            self.grad = grad_out
        else:
            self.grad += grad_out

        # Topological sort of the graph
        visited = set()
        topo_order = []
        def build_topo(v):
            if v not in visited and v._creator is not None:
                visited.add(v)
                op, parents = v._creator
                for parent in parents:
                    build_topo(parent)
                topo_order.append(v)

        build_topo(self)

        # Backpropagate through the sorted graph
        for v in reversed(topo_order):
            op, parents = v._creator

            if v.grad is None:
                # This can happen if a part of the graph is disconnected
                # from the final loss. We can skip it.
                continue

            grads = op.backward(v.grad)

            for parent, grad in zip(parents, grads):
                if parent.requires_grad and grad is not None:
                    if parent.grad is None:
                        parent.grad = grad
                    else:
                        parent.grad += grad

    # --- Operator Overloading ---
    def __add__(self, other):
        return Add()(self, other if isinstance(other, OmegaTensor) else OmegaTensor(other))

    def __radd__(self, other):
        return Add()(OmegaTensor(other), self)

    def __mul__(self, other):
        return Mul()(self, other if isinstance(other, OmegaTensor) else OmegaTensor(other))

    def __rmul__(self, other):
        return Mul()(OmegaTensor(other), self)

    def __pow__(self, power):
        return Pow(power)(self)

    def __sub__(self, other):
        return Sub()(self, other if isinstance(other, OmegaTensor) else OmegaTensor(other))

    def __rsub__(self, other):
         return Sub()(OmegaTensor(other), self)

    def __neg__(self):
        return Neg()(self)

    def __truediv__(self, other):
        return self/OmegaTensor(other) if not isinstance(other, OmegaTensor) else self * (other ** -1)

    def __rtruediv__(self, other):
        return OmegaTensor(other) / self

    def matmul(self, other):
        return MatMul()(self, other)

    def __matmul__(self, other):
        return self.matmul(other)

    def sum(self, axis=None, keepdims=False):
        return Sum(axis, keepdims)(self)

    def reshape(self, *shape):
        return Reshape(*shape)(self)

    def transpose(self, *axes):
        return Transpose(*axes)(self)


# --- Basic Operations ---
class Add(Op):
    def __call__(self, a: OmegaTensor, b: OmegaTensor) -> OmegaTensor:
        requires_grad = a.requires_grad or b.requires_grad
        out = OmegaTensor(a.data + b.data, requires_grad)
        if requires_grad:
            out.set_creator(self, a, b)
        self.a_shape = a.shape
        self.b_shape = b.shape
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        grad_a = grad_out
        grad_b = grad_out
        # Handle broadcasting
        if self.a_shape != grad_out.shape:
            grad_a = self._unbroadcast(grad_a, self.a_shape)
        if self.b_shape != grad_out.shape:
            grad_b = self._unbroadcast(grad_b, self.b_shape)
        return grad_a, grad_b

    @staticmethod
    def _unbroadcast(grad, shape):
        while len(grad.shape) > len(shape):
            grad = grad.sum(axis=0)
        for i, dim in enumerate(shape):
            if dim == 1:
                grad = grad.sum(axis=i, keepdims=True)
        return grad

class Mul(Op):
    def __call__(self, a: OmegaTensor, b: OmegaTensor) -> OmegaTensor:
        requires_grad = a.requires_grad or b.requires_grad
        out = OmegaTensor(a.data * b.data, requires_grad)
        if requires_grad:
            out.set_creator(self, a, b)
        self.a = a
        self.b = b
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        grad_a = grad_out * self.b.data
        grad_b = grad_out * self.a.data
        # Handle broadcasting
        if self.a.shape != grad_out.shape:
            grad_a = Add._unbroadcast(grad_a, self.a.shape)
        if self.b.shape != grad_out.shape:
            grad_b = Add._unbroadcast(grad_b, self.b.shape)
        return grad_a, grad_b

class Sub(Op):
    def __call__(self, a: OmegaTensor, b: OmegaTensor) -> OmegaTensor:
        requires_grad = a.requires_grad or b.requires_grad
        out = OmegaTensor(a.data - b.data, requires_grad)
        if requires_grad:
            out.set_creator(self, a, b)
        self.a_shape = a.shape
        self.b_shape = b.shape
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        grad_a = grad_out
        grad_b = -grad_out
        if self.a_shape != grad_out.shape:
            grad_a = Add._unbroadcast(grad_a, self.a_shape)
        if self.b_shape != grad_out.shape:
            grad_b = Add._unbroadcast(grad_b, self.b_shape)
        return grad_a, grad_b

class Neg(Op):
    def __call__(self, a: OmegaTensor) -> OmegaTensor:
        out = OmegaTensor(-a.data, a.requires_grad)
        if a.requires_grad:
            out.set_creator(self, a)
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray]:
        return (-grad_out,)

class Pow(Op):
    def __init__(self, power: float):
        self.power = power

    def __call__(self, a: OmegaTensor) -> OmegaTensor:
        out = OmegaTensor(a.data ** self.power, a.requires_grad)
        if a.requires_grad:
            out.set_creator(self, a)
        self.a = a
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray]:
        grad_a = grad_out * (self.power * self.a.data ** (self.power - 1))
        return (grad_a,)

class MatMul(Op):
    def __call__(self, a: OmegaTensor, b: OmegaTensor) -> OmegaTensor:
        requires_grad = a.requires_grad or b.requires_grad
        out = OmegaTensor(a.data @ b.data, requires_grad)
        if requires_grad:
            out.set_creator(self, a, b)
        self.a = a
        self.b = b
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        grad_a = grad_out @ self.b.data.T
        grad_b = self.a.data.T @ grad_out
        return grad_a, grad_b

class Sum(Op):
    def __init__(self, axis=None, keepdims=False):
        self.axis = axis
        self.keepdims = keepdims

    def __call__(self, a: OmegaTensor) -> OmegaTensor:
        out = OmegaTensor(a.data.sum(axis=self.axis, keepdims=self.keepdims), a.requires_grad)
        if a.requires_grad:
            out.set_creator(self, a)
        self.a_shape = a.shape
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray]:
        if not self.keepdims and self.axis is not None:
             grad_out = np.expand_dims(grad_out, self.axis)
        return (np.broadcast_to(grad_out, self.a_shape),)

class Reshape(Op):
    def __init__(self, *shape):
        self.shape = shape

    def __call__(self, a: OmegaTensor) -> OmegaTensor:
        out = OmegaTensor(a.data.reshape(*self.shape), a.requires_grad)
        if a.requires_grad:
            out.set_creator(self, a)
        self.a_shape = a.shape
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray]:
        return (grad_out.reshape(self.a_shape),)

class Transpose(Op):
    def __init__(self, *axes):
        self.axes = axes

    def __call__(self, a: OmegaTensor) -> OmegaTensor:
        out = OmegaTensor(a.data.transpose(*self.axes), a.requires_grad)
        if a.requires_grad:
            out.set_creator(self, a)
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray]:
        # The backward of a transpose is a transpose with the inverse permutation
        inv_axes = np.argsort(self.axes)
        return (grad_out.transpose(*inv_axes),)

# --- Activation Functions ---
class ReLU(Op):
    def __call__(self, a: OmegaTensor) -> OmegaTensor:
        self.mask = a.data > 0
        out = OmegaTensor(a.data * self.mask, a.requires_grad)
        if a.requires_grad:
            out.set_creator(self, a)
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray]:
        return (grad_out * self.mask,)

def relu(x: OmegaTensor) -> OmegaTensor:
    return ReLU()(x)

class Softmax(Op):
    def __init__(self, axis=-1):
        self.axis = axis

    def __call__(self, a: OmegaTensor) -> OmegaTensor:
        # Numerically stable softmax
        max_val = a.data.max(axis=self.axis, keepdims=True)
        e_x = np.exp(a.data - max_val)
        self.out_data = e_x / e_x.sum(axis=self.axis, keepdims=True)
        out = OmegaTensor(self.out_data, a.requires_grad)
        if a.requires_grad:
            out.set_creator(self, a)
        return out

    def backward(self, grad_out: np.ndarray) -> Tuple[np.ndarray]:
        # This is a bit more complex. For dS_i/dx_j = S_i * (delta_ij - S_j)
        # where S is the softmax output.
        # The Jacobian-vector product is grad_out * dS/dx.
        s = self.out_data
        # Reshape for broadcasting
        s_reshaped = np.expand_dims(s, axis=-1)
        # Jacobian
        jacobian = np.diag_ промо(s.ravel()) - np.outer(s, s) # This is slow for large batches
        # Simplified for common case
        grad_a = s * (grad_out - (grad_out * s).sum(axis=self.axis, keepdims=True))
        return (grad_a,)

def softmax(x: OmegaTensor, axis=-1) -> OmegaTensor:
    return Softmax(axis)(x)

def cross_entropy_loss(y_pred: OmegaTensor, y_true: np.ndarray) -> OmegaTensor:
    """
    y_pred: OmegaTensor of shape (batch_size, num_classes) with raw logits
    y_true: numpy array of shape (batch_size,) with integer class labels
    """
    batch_size, num_classes = y_pred.shape

    # Log-softmax for numerical stability
    log_probs = y_pred - y_pred.data.max(axis=1, keepdims=True)
    log_probs = log_probs - OmegaTensor(np.log(np.exp(log_probs.data).sum(axis=1, keepdims=True)))

    # Gather the log probabilities of the true classes
    # This is equivalent to `log_probs[range(batch_size), y_true]`
    true_log_probs = log_probs.data[range(batch_size), y_true]

    # Compute the negative log likelihood
    loss = -OmegaTensor(true_log_probs).sum() / batch_size

    # Monkey-patch backward for this specific loss function for efficiency
    def _backward_fn():
        # The gradient of cross-entropy w.r.t logits is (softmax(logits) - y_one_hot)
        probs = np.exp(log_probs.data)
        grad = probs
        grad[range(batch_size), y_true] -= 1
        grad /= batch_size
        y_pred.backward(grad)

    loss._creator = (None, []) # Mark as a root for custom backward
    loss.backward = _backward_fn # Override default backward

    return loss
