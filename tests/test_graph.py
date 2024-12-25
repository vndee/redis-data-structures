from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Graph


@pytest.fixture
def graph() -> Graph:
    """Create a Graph instance for testing."""
    g = Graph("test_graph")
    g.clear()
    yield g
    g.clear()
    g.close()


def test_add_vertex(graph):
    # Test adding vertex without data
    assert graph.add_vertex("v1")
    assert graph.vertex_exists("v1")

    # Test adding vertex with data
    data = {"name": "Vertex 1", "value": 42}
    assert graph.add_vertex("v2", data)
    assert graph.vertex_exists("v2")
    assert graph.get_vertex_data("v2") == data


def test_add_edge(graph):
    # Add vertices first
    graph.add_vertex("v1")
    graph.add_vertex("v2")

    # Test adding edge
    assert graph.add_edge("v1", "v2", 1.5)
    assert graph.get_edge_weight("v1", "v2") == 1.5

    # Test adding edge with default weight
    assert graph.add_edge("v2", "v1")
    assert graph.get_edge_weight("v2", "v1") == 1.0

    # Test adding edge between non-existent vertices
    assert not graph.add_edge("v1", "v3")
    assert not graph.add_edge("v3", "v1")


def test_remove_vertex(graph):
    # Setup test graph
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    graph.add_vertex("v3")
    graph.add_edge("v1", "v2")
    graph.add_edge("v2", "v1")
    graph.add_edge("v2", "v3")

    # Test removing vertex
    assert graph.remove_vertex("v2")
    assert not graph.vertex_exists("v2")

    # Verify edges are removed
    assert not graph.get_edge_weight("v1", "v2")
    assert not graph.get_edge_weight("v2", "v1")
    assert not graph.get_edge_weight("v2", "v3")


def test_remove_edge(graph):
    # Setup test graph
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    graph.add_edge("v1", "v2", 1.5)

    # Test removing edge
    assert graph.remove_edge("v1", "v2")
    assert not graph.get_edge_weight("v1", "v2")

    # Test removing non-existent edge
    assert not graph.remove_edge("v1", "v3")


def test_get_vertex_data(graph):
    # Test with no data
    graph.add_vertex("v1")
    assert graph.get_vertex_data("v1") is None

    # Test with data
    data = {"name": "Vertex 1", "value": 42}
    graph.add_vertex("v2", data)
    assert graph.get_vertex_data("v2") == data

    # Test non-existent vertex
    assert graph.get_vertex_data("v3") is None


def test_get_neighbors(graph):
    # Setup test graph
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    graph.add_vertex("v3")
    graph.add_edge("v1", "v2", 1.5)
    graph.add_edge("v1", "v3", 2.0)

    # Test getting neighbors
    neighbors = graph.get_neighbors("v1")
    assert len(neighbors) == 2
    assert neighbors["v2"] == 1.5
    assert neighbors["v3"] == 2.0

    # Test vertex with no neighbors
    assert len(graph.get_neighbors("v2")) == 0

    # Test non-existent vertex
    assert len(graph.get_neighbors("v4")) == 0


def test_get_vertices(graph):
    # Test empty graph
    assert len(graph.get_vertices()) == 0

    # Add vertices
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    graph.add_vertex("v3")

    # Test getting all vertices
    vertices = graph.get_vertices()
    assert len(vertices) == 3
    assert "v1" in vertices
    assert "v2" in vertices
    assert "v3" in vertices


def test_vertex_exists(graph):
    # Test non-existent vertex
    assert not graph.vertex_exists("v1")

    # Add vertex and test
    graph.add_vertex("v1")
    assert graph.vertex_exists("v1")

    # Remove vertex and test
    graph.remove_vertex("v1")
    assert not graph.vertex_exists("v1")


def test_get_edge_weight(graph):
    # Setup test graph
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    graph.add_edge("v1", "v2", 1.5)

    # Test getting edge weight
    assert graph.get_edge_weight("v1", "v2") == 1.5

    # Test non-existent edge
    assert graph.get_edge_weight("v2", "v1") is None
    assert graph.get_edge_weight("v1", "v3") is None


def test_clear(graph):
    # Setup test graph
    graph.add_vertex("v1", {"data": "value1"})
    graph.add_vertex("v2", {"data": "value2"})
    graph.add_edge("v1", "v2", 1.5)

    # Test clearing graph
    assert graph.clear()
    assert len(graph.get_vertices()) == 0
    assert not graph.vertex_exists("v1")
    assert not graph.vertex_exists("v2")
    assert not graph.get_edge_weight("v1", "v2")


# Error handling tests
def test_add_vertex_error_handling(graph):
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert not graph.add_vertex("v1", {"data": "value"})


def test_add_edge_error_handling(graph):
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert not graph.add_edge("v1", "v2")


def test_remove_vertex_error_handling(graph):
    graph.add_vertex("v1")
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert not graph.remove_vertex("v1")


def test_remove_edge_error_handling(graph):
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    graph.add_edge("v1", "v2")
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert not graph.remove_edge("v1", "v2")


def test_get_vertex_data_error_handling(graph):
    graph.add_vertex("v1", {"data": "value"})
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert graph.get_vertex_data("v1") is None


def test_get_neighbors_error_handling(graph):
    graph.add_vertex("v1")
    graph.add_edge("v1", "v2")
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert len(graph.get_neighbors("v1")) == 0


def test_get_vertices_error_handling(graph):
    graph.add_vertex("v1")
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert len(graph.get_vertices()) == 0


def test_vertex_exists_error_handling(graph):
    graph.add_vertex("v1")
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert not graph.vertex_exists("v1")


def test_get_edge_weight_error_handling(graph):
    graph.add_vertex("v1")
    graph.add_vertex("v2")
    graph.add_edge("v1", "v2", 1.5)
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert graph.get_edge_weight("v1", "v2") is None


def test_clear_error_handling(graph):
    graph.add_vertex("v1")
    with patch.object(graph.connection_manager, "execute", side_effect=RedisError):
        assert not graph.clear()
