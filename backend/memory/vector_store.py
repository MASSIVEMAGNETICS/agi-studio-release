import numpy as np
import pickle

class VectorStore:
    def __init__(self, dim=1536):
        self.vectors = []
        self.meta = []
        self.dim = dim

    def add(self, vector, meta=None):
        assert len(vector) == self.dim
        self.vectors.append(vector)
        self.meta.append(meta)

    def search(self, query_vector, top_k=5):
        arr = np.array(self.vectors)
        sims = arr @ query_vector / (np.linalg.norm(arr, axis=1) * np.linalg.norm(query_vector))
        idx = np.argsort(sims)[::-1][:top_k]
        return [(self.meta[i], float(sims[i])) for i in idx]

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump((self.vectors, self.meta), f)

    def load(self, path):
        with open(path, "rb") as f:
            self.vectors, self.meta = pickle.load(f)
