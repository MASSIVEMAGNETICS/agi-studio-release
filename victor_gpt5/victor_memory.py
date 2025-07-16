import numpy as np
import pickle
import os
import re
import hashlib
from collections import deque
from datetime import datetime
from typing import Dict, Any, List, Tuple

# --- Vector Store (FAISS replacement for simplicity) ---
class SimpleVectorStore:
    """A simple, numpy-based vector store."""
    def __init__(self, dim: int):
        self.dim = dim
        self.vectors = np.zeros((0, dim), dtype=np.float32)
        self.metadata = []

    def add(self, vectors: np.ndarray, metadata: List[Dict]):
        if self.vectors.shape[0] == 0:
            self.vectors = vectors
        else:
            self.vectors = np.vstack([self.vectors, vectors])
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, k: int) -> List[Tuple[Dict, float]]:
        if self.vectors.shape[0] == 0:
            return []
        # Cosine similarity
        norm_query = query_vector / np.linalg.norm(query_vector)
        norm_db = self.vectors / np.linalg.norm(self.vectors, axis=1, keepdims=True)
        similarities = norm_db @ norm_query.T

        # Get top k results
        # Handle case where k > number of items
        num_items = len(similarities)
        k = min(k, num_items)

        top_k_indices = np.argsort(similarities)[-k:][::-1]

        return [(self.metadata[i], similarities[i]) for i in top_k_indices]

# --- Main Memory System ---
class VictorMemory:
    """Manages the AGI's memory across different temporalities."""
    def __init__(self, config: Dict[str, Any], privacy_core):
        self.config = config['memory']
        self.privacy_core = privacy_core

        # 1. Short-term "timeline" memory
        self.timeline = deque(maxlen=self.config['short_term_max_size'])

        # 2. Long-term semantic "vector" memory
        self.vector_store = SimpleVectorStore(dim=self.config['vector_dim'])

        # 3. Causal "graph" memory (conceptual, simple implementation)
        self.graph = {} # node_id -> {content: {}, connections: []}

        self.autosave_path = self.config['long_term_db_path']
        self.load()

    def add_interaction(self, user_input: str, ai_response: str, embedding: np.ndarray):
        """Adds a full user-AI interaction to memory."""
        timestamp = datetime.utcnow().isoformat()

        # Scrub for privacy before storing
        scrubbed_user = self.privacy_core.scrub(user_input)
        scrubbed_ai = self.privacy_core.scrub(ai_response)

        interaction_id = hashlib.sha256(f"{timestamp}{scrubbed_user}".encode()).hexdigest()

        memory_entry = {
            'id': interaction_id,
            'type': 'interaction',
            'timestamp': timestamp,
            'user_input': scrubbed_user,
            'ai_response': scrubbed_ai,
            'embedding': embedding
        }

        # Add to all memory systems
        self.timeline.append(memory_entry)
        self.vector_store.add(embedding.reshape(1, -1), [memory_entry])
        self._add_to_graph(memory_entry)

        print(f"[Memory] Added interaction {interaction_id}")

    def _add_to_graph(self, entry: Dict):
        """Adds an entry to the graph, trying to link it to recent events."""
        node_id = entry['id']
        self.graph[node_id] = {'content': entry, 'connections': []}

        # Naive causal link: connect to the previous timeline event
        if len(self.timeline) > 1:
            prev_entry = self.timeline[-2]
            prev_id = prev_entry['id']
            if prev_id in self.graph:
                self.graph[prev_id]['connections'].append(node_id)

    def retrieve_relevant_memories(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """Retrieves memories relevant to a query from the vector store."""
        results = self.vector_store.search(query_embedding, k)
        return [meta for meta, score in results]

    def get_short_term_context(self, num_recent: int = 5) -> str:
        """Constructs a context string from recent interactions."""
        context = ""
        recent_interactions = list(self.timeline)[-num_recent:]
        for entry in recent_interactions:
            context += f"User: {entry['user_input']}\nVictor: {entry['ai_response']}\n"
        return context.strip()

    def save(self):
        """Saves the long-term memory systems to disk."""
        try:
            os.makedirs(os.path.dirname(self.autosave_path), exist_ok=True)
            memory_state = {
                'vector_store_vectors': self.vector_store.vectors,
                'vector_store_metadata': self.vector_store.metadata,
                'graph': self.graph
            }
            with open(self.autosave_path, 'wb') as f:
                pickle.dump(memory_state, f)
            print(f"[Memory] Saved long-term memory to {self.autosave_path}")
        except Exception as e:
            print(f"Error saving memory: {e}")

    def load(self):
        """Loads long-term memory from disk."""
        if not os.path.exists(self.autosave_path):
            print("[Memory] No existing memory file found. Starting fresh.")
            return
        try:
            with open(self.autosave_path, 'rb') as f:
                memory_state = pickle.load(f)
            self.vector_store.vectors = memory_state['vector_store_vectors']
            self.vector_store.metadata = memory_state['vector_store_metadata']
            self.graph = memory_state['graph']
            print(f"[Memory] Loaded long-term memory from {self.autosave_path}")
        except Exception as e:
            print(f"Error loading memory: {e}. Starting fresh.")
            self.__init__(self.config, self.privacy_core) # Re-initialize
