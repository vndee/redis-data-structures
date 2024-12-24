import logging
from typing import Any, Dict, Optional, Set

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class Graph(RedisDataStructure):
    """A Redis-backed directed graph implementation using adjacency lists.

    This class implements a directed graph where vertices can store data and edges
    can connect any two vertices. The implementation uses Redis Hashes to store
    vertex data and adjacency lists, providing O(1) operations for most graph
    operations.

    Features:
    - O(1) vertex and edge operations
    - Vertex data storage
    - Weighted edges
    - Thread-safe operations
    - Persistent storage
    """

    def add_vertex(self, key: str, vertex: str, data: Any = None) -> bool:
        """Add a vertex to the graph.

        Args:
            key (str): The Redis key for this graph
            vertex (str): The vertex identifier
            data (Any, optional): Data to associate with the vertex

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store vertex data
            vertex_key = f"{key}:vertex:{vertex}"
            if data is not None:
                self.connection_manager.execute("hset", vertex_key, "data", self.serialize(data))

            # Initialize empty adjacency list if it doesn't exist
            adj_key = f"{key}:adj:{vertex}"
            if not self.connection_manager.execute("exists", adj_key):
                self.connection_manager.execute("hset", adj_key, "_initialized", "1")

            return True
        except Exception:
            logger.exception("Error adding vertex")
            return False

    def add_edge(self, key: str, from_vertex: str, to_vertex: str, weight: float = 1.0) -> bool:
        """Add a directed edge between vertices.

        Args:
            key (str): The Redis key for this graph
            from_vertex (str): Source vertex
            to_vertex (str): Destination vertex
            weight (float, optional): Edge weight, defaults to 1.0

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure both vertices exist
            if not self.vertex_exists(key, from_vertex) or not self.vertex_exists(key, to_vertex):
                return False

            # Add edge to adjacency list
            adj_key = f"{key}:adj:{from_vertex}"
            self.connection_manager.execute("hset", adj_key, to_vertex, str(weight))
            return True
        except Exception:
            logger.exception("Error adding edge")
            return False

    def remove_vertex(self, key: str, vertex: str) -> bool:
        """Remove a vertex and all its edges from the graph.

        Args:
            key (str): The Redis key for this graph
            vertex (str): The vertex to remove

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove vertex data and adjacency list
            vertex_key = f"{key}:vertex:{vertex}"
            adj_key = f"{key}:adj:{vertex}"

            # Remove incoming edges from other vertices
            pattern = f"{key}:adj:*"
            for adj_list_key in self.connection_manager.execute("scan_iter", match=pattern):
                self.connection_manager.execute("hdel", adj_list_key, vertex)

            # Remove vertex's own data and adjacency list
            self.connection_manager.execute("delete", vertex_key, adj_key)
            return True
        except Exception:
            logger.exception("Error removing vertex")
            return False

    def remove_edge(self, key: str, from_vertex: str, to_vertex: str) -> bool:
        """Remove an edge from the graph.

        Args:
            key (str): The Redis key for this graph
            from_vertex (str): Source vertex
            to_vertex (str): Destination vertex

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            adj_key = f"{key}:adj:{from_vertex}"
            return bool(self.connection_manager.execute("hdel", adj_key, to_vertex))
        except Exception:
            logger.exception("Error removing edge")
            return False

    def get_vertex_data(self, key: str, vertex: str) -> Optional[Any]:
        """Get data associated with a vertex.

        Args:
            key (str): The Redis key for this graph
            vertex (str): The vertex to get data for

        Returns:
            Optional[Any]: Vertex data if it exists, None otherwise
        """
        try:
            vertex_key = f"{key}:vertex:{vertex}"
            data = self.connection_manager.execute("hget", vertex_key, "data")
            return self.deserialize(data) if data else None
        except Exception:
            logger.exception("Error getting vertex data")
            return None

    def get_neighbors(self, key: str, vertex: str) -> Dict[str, float]:
        """Get all neighbors of a vertex with their edge weights.

        Args:
            key (str): The Redis key for this graph
            vertex (str): The vertex to get neighbors for

        Returns:
            Dict[str, float]: Dictionary mapping neighbor vertices to edge weights
        """
        try:
            adj_key = f"{key}:adj:{vertex}"
            neighbors = self.connection_manager.execute("hgetall", adj_key)

            # Filter out initialization flag and convert weights to float
            return {k: float(v) for k, v in neighbors.items() if k != "_initialized"}
        except Exception:
            logger.exception("Error getting neighbors")
            return {}

    def get_vertices(self, key: str) -> Set[str]:
        """Get all vertices in the graph.

        Args:
            key (str): The Redis key for this graph

        Returns:
            Set[str]: Set of all vertex identifiers
        """
        try:
            vertices = set()

            # Get vertices from vertex data keys
            vertex_pattern = f"{key}:vertex:*"
            for vertex_key in self.connection_manager.execute("scan_iter", match=vertex_pattern):
                vertex = vertex_key.split(":")[-1]
                vertices.add(vertex)

            # Get vertices from adjacency list keys
            adj_pattern = f"{key}:adj:*"
            for adj_key in self.connection_manager.execute("scan_iter", match=adj_pattern):
                vertex = adj_key.split(":")[-1]
                vertices.add(vertex)

            return vertices
        except Exception:
            logger.exception("Error getting vertices")
            return set()

    def vertex_exists(self, key: str, vertex: str) -> bool:
        """Check if a vertex exists in the graph.

        Args:
            key (str): The Redis key for this graph
            vertex (str): The vertex to check

        Returns:
            bool: True if vertex exists, False otherwise
        """
        try:
            vertex_key = f"{key}:vertex:{vertex}"
            adj_key = f"{key}:adj:{vertex}"
            return bool(
                self.connection_manager.execute("exists", vertex_key)
                or self.connection_manager.execute("exists", adj_key),
            )
        except Exception:
            logger.exception("Error checking vertex existence")
            return False

    def get_edge_weight(self, key: str, from_vertex: str, to_vertex: str) -> Optional[float]:
        """Get the weight of an edge between two vertices.

        Args:
            key (str): The Redis key for this graph
            from_vertex (str): Source vertex
            to_vertex (str): Destination vertex

        Returns:
            Optional[float]: Edge weight if edge exists, None otherwise
        """
        try:
            adj_key = f"{key}:adj:{from_vertex}"
            weight = self.connection_manager.execute("hget", adj_key, to_vertex)
            return float(weight) if weight else None
        except Exception:
            logger.exception("Error getting edge weight")
            return None

    def clear(self, key: str) -> bool:
        """Remove all vertices and edges from the graph.

        Args:
            key (str): The Redis key for this graph

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all keys related to this graph
            vertex_pattern = f"{key}:vertex:*"
            adj_pattern = f"{key}:adj:*"

            # Delete all vertex data and adjacency lists
            keys_to_delete = []
            for pattern in [vertex_pattern, adj_pattern]:
                keys_to_delete.extend(self.connection_manager.execute("scan_iter", match=pattern))

            if keys_to_delete:
                self.connection_manager.execute("delete", *keys_to_delete)
            return True
        except Exception:
            logger.exception("Error clearing graph")
            return False
