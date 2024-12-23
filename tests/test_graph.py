import unittest
from unittest.mock import patch, MagicMock

from redis.exceptions import RedisError

from redis_data_structures import Graph


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.test_key = "test_graph"
        self.graph.clear(self.test_key)

    def tearDown(self):
        self.graph.clear(self.test_key)
        self.graph.close()

    def test_add_vertex(self):
        # Test adding vertex without data
        assert self.graph.add_vertex(self.test_key, "v1")
        assert self.graph.vertex_exists(self.test_key, "v1")

        # Test adding vertex with data
        data = {"name": "Vertex 1", "value": 42}
        assert self.graph.add_vertex(self.test_key, "v2", data)
        assert self.graph.vertex_exists(self.test_key, "v2")
        assert self.graph.get_vertex_data(self.test_key, "v2") == data

    def test_add_edge(self):
        # Add vertices first
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")

        # Test adding edge
        assert self.graph.add_edge(self.test_key, "v1", "v2", 1.5)
        assert self.graph.get_edge_weight(self.test_key, "v1", "v2") == 1.5

        # Test adding edge with default weight
        assert self.graph.add_edge(self.test_key, "v2", "v1")
        assert self.graph.get_edge_weight(self.test_key, "v2", "v1") == 1.0

        # Test adding edge between non-existent vertices
        assert not self.graph.add_edge(self.test_key, "v1", "v3")
        assert not self.graph.add_edge(self.test_key, "v3", "v1")

    def test_remove_vertex(self):
        # Setup test graph
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        self.graph.add_vertex(self.test_key, "v3")
        self.graph.add_edge(self.test_key, "v1", "v2")
        self.graph.add_edge(self.test_key, "v2", "v1")
        self.graph.add_edge(self.test_key, "v2", "v3")

        # Test removing vertex
        assert self.graph.remove_vertex(self.test_key, "v2")
        assert not self.graph.vertex_exists(self.test_key, "v2")

        # Verify edges are removed
        assert not self.graph.get_edge_weight(self.test_key, "v1", "v2")
        assert not self.graph.get_edge_weight(self.test_key, "v2", "v1")
        assert not self.graph.get_edge_weight(self.test_key, "v2", "v3")

    def test_remove_edge(self):
        # Setup test graph
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        self.graph.add_edge(self.test_key, "v1", "v2", 1.5)

        # Test removing edge
        assert self.graph.remove_edge(self.test_key, "v1", "v2")
        assert not self.graph.get_edge_weight(self.test_key, "v1", "v2")

        # Test removing non-existent edge
        assert not self.graph.remove_edge(self.test_key, "v1", "v3")

    def test_get_vertex_data(self):
        # Test with no data
        self.graph.add_vertex(self.test_key, "v1")
        assert self.graph.get_vertex_data(self.test_key, "v1") is None

        # Test with data
        data = {"name": "Vertex 1", "value": 42}
        self.graph.add_vertex(self.test_key, "v2", data)
        assert self.graph.get_vertex_data(self.test_key, "v2") == data

        # Test non-existent vertex
        assert self.graph.get_vertex_data(self.test_key, "v3") is None

    def test_get_neighbors(self):
        # Setup test graph
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        self.graph.add_vertex(self.test_key, "v3")
        self.graph.add_edge(self.test_key, "v1", "v2", 1.5)
        self.graph.add_edge(self.test_key, "v1", "v3", 2.0)

        # Test getting neighbors
        neighbors = self.graph.get_neighbors(self.test_key, "v1")
        assert len(neighbors) == 2
        assert neighbors["v2"] == 1.5
        assert neighbors["v3"] == 2.0

        # Test vertex with no neighbors
        assert len(self.graph.get_neighbors(self.test_key, "v2")) == 0

        # Test non-existent vertex
        assert len(self.graph.get_neighbors(self.test_key, "v4")) == 0

    def test_get_vertices(self):
        # Test empty graph
        assert len(self.graph.get_vertices(self.test_key)) == 0

        # Add vertices
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        self.graph.add_vertex(self.test_key, "v3")

        # Test getting all vertices
        vertices = self.graph.get_vertices(self.test_key)
        assert len(vertices) == 3
        assert "v1" in vertices
        assert "v2" in vertices
        assert "v3" in vertices

    def test_vertex_exists(self):
        # Test non-existent vertex
        assert not self.graph.vertex_exists(self.test_key, "v1")

        # Add vertex and test
        self.graph.add_vertex(self.test_key, "v1")
        assert self.graph.vertex_exists(self.test_key, "v1")

        # Remove vertex and test
        self.graph.remove_vertex(self.test_key, "v1")
        assert not self.graph.vertex_exists(self.test_key, "v1")

    def test_get_edge_weight(self):
        # Setup test graph
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        self.graph.add_edge(self.test_key, "v1", "v2", 1.5)

        # Test getting edge weight
        assert self.graph.get_edge_weight(self.test_key, "v1", "v2") == 1.5

        # Test non-existent edge
        assert self.graph.get_edge_weight(self.test_key, "v2", "v1") is None
        assert self.graph.get_edge_weight(self.test_key, "v1", "v3") is None

    def test_clear(self):
        # Setup test graph
        self.graph.add_vertex(self.test_key, "v1", {"data": "value1"})
        self.graph.add_vertex(self.test_key, "v2", {"data": "value2"})
        self.graph.add_edge(self.test_key, "v1", "v2", 1.5)

        # Test clearing graph
        assert self.graph.clear(self.test_key)
        assert len(self.graph.get_vertices(self.test_key)) == 0
        assert not self.graph.vertex_exists(self.test_key, "v1")
        assert not self.graph.vertex_exists(self.test_key, "v2")
        assert not self.graph.get_edge_weight(self.test_key, "v1", "v2")

    # Error handling tests
    def test_add_vertex_error_handling(self):
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert not self.graph.add_vertex(self.test_key, "v1", {"data": "value"})

    def test_add_edge_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert not self.graph.add_edge(self.test_key, "v1", "v2")

    def test_remove_vertex_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert not self.graph.remove_vertex(self.test_key, "v1")

    def test_remove_edge_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        self.graph.add_edge(self.test_key, "v1", "v2")
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert not self.graph.remove_edge(self.test_key, "v1", "v2")

    def test_get_vertex_data_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1", {"data": "value"})
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert self.graph.get_vertex_data(self.test_key, "v1") is None

    def test_get_neighbors_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_edge(self.test_key, "v1", "v2")
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert len(self.graph.get_neighbors(self.test_key, "v1")) == 0

    def test_get_vertices_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert len(self.graph.get_vertices(self.test_key)) == 0

    def test_vertex_exists_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert not self.graph.vertex_exists(self.test_key, "v1")

    def test_get_edge_weight_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        self.graph.add_vertex(self.test_key, "v2")
        self.graph.add_edge(self.test_key, "v1", "v2", 1.5)
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert self.graph.get_edge_weight(self.test_key, "v1", "v2") is None

    def test_clear_error_handling(self):
        self.graph.add_vertex(self.test_key, "v1")
        with patch.object(self.graph.connection_manager, "execute", side_effect=RedisError):
            assert not self.graph.clear(self.test_key)


if __name__ == "__main__":
    unittest.main()
