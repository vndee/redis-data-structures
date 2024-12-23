# Graph

A Redis-backed directed graph implementation with support for weighted edges. Perfect for social networks, recommendation systems, and any application requiring graph-based data structures.

## Features

- Directed graph with weighted edges
- Vertex data storage with type preservation
- Efficient edge traversal
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import Graph, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create graph with connection manager
graph = Graph(connection_manager=connection_manager)

# Add vertices with data
graph.add_vertex('my_graph', 'v1', {'name': 'Alice', 'age': 30})
graph.add_vertex('my_graph', 'v2', {'name': 'Bob', 'age': 25})

# Add edges with weights
graph.add_edge('my_graph', 'v1', 'v2', weight=0.8)

# Get vertex data
alice = graph.get_vertex_data('my_graph', 'v1')
print(f"Name: {alice['name']}, Age: {alice['age']}")

# Get neighbors
neighbors = graph.get_neighbors('my_graph', 'v1')
for neighbor, weight in neighbors.items():
    print(f"Neighbor: {neighbor}, Weight: {weight}")

# Remove edges and vertices
graph.remove_edge('my_graph', 'v1', 'v2')
graph.remove_vertex('my_graph', 'v1')

# Clear the graph
graph.clear('my_graph')
```

## Advanced Usage

```python
from redis_data_structures import Graph, ConnectionManager
from datetime import datetime, timedelta

# Create connection manager with advanced features
connection_manager = ConnectionManager(
    host='redis.example.com',
    port=6380,
    max_connections=20,
    retry_max_attempts=5,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=timedelta(minutes=5),
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)

# Create graph with connection manager
graph = Graph(connection_manager=connection_manager)

# Store complex types
user_data = {
    'name': 'Charlie',
    'joined': datetime.now(),
    'metadata': {'role': 'admin', 'status': 'active'}
}
graph.add_vertex('social_network', 'user3', user_data)

# Batch operations
vertices = [
    ('user4', {'name': 'David', 'age': 28}),
    ('user5', {'name': 'Eve', 'age': 32})
]
for vertex_id, data in vertices:
    graph.add_vertex('social_network', vertex_id, data)

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. Social Network

```python
from redis_data_structures import Graph, ConnectionManager
from datetime import datetime

class SocialNetwork:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.graph = Graph(connection_manager=self.connection_manager)
        self.graph_key = 'social_network'
    
    def add_user(self, user_id: str, data: dict):
        """Add a user to the network."""
        data['joined'] = datetime.now()
        self.graph.add_vertex(self.graph_key, user_id, data)
    
    def add_friendship(self, user1: str, user2: str, strength: float = 1.0):
        """Create a bidirectional friendship."""
        self.graph.add_edge(self.graph_key, user1, user2, weight=strength)
        self.graph.add_edge(self.graph_key, user2, user1, weight=strength)
    
    def get_friends(self, user_id: str) -> dict:
        """Get user's friends with friendship strength."""
        return self.graph.get_neighbors(self.graph_key, user_id)
    
    def get_user_info(self, user_id: str) -> dict:
        """Get user information."""
        return self.graph.get_vertex_data(self.graph_key, user_id)

# Usage
network = SocialNetwork()
network.add_user('alice', {'name': 'Alice', 'age': 30})
network.add_user('bob', {'name': 'Bob', 'age': 25})
network.add_friendship('alice', 'bob', 0.9)
```

### 2. Recommendation System

```python
from redis_data_structures import Graph, ConnectionManager

class RecommendationSystem:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.graph = Graph(connection_manager=self.connection_manager)
        self.graph_key = 'recommendations'
    
    def add_item(self, item_id: str, data: dict):
        """Add an item to the system."""
        self.graph.add_vertex(self.graph_key, item_id, data)
    
    def add_similarity(self, item1: str, item2: str, score: float):
        """Add similarity score between items."""
        self.graph.add_edge(self.graph_key, item1, item2, weight=score)
    
    def get_recommendations(self, item_id: str, limit: int = 5) -> list:
        """Get similar items sorted by similarity score."""
        neighbors = self.graph.get_neighbors(self.graph_key, item_id)
        sorted_items = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:limit]

# Usage
recommender = RecommendationSystem()
recommender.add_item('book1', {'title': 'Python Programming'})
recommender.add_item('book2', {'title': 'Data Science'})
recommender.add_similarity('book1', 'book2', 0.8)
```

## Best Practices

1. **Connection Management**
   ```python
   # Create a shared connection manager
   connection_manager = ConnectionManager(
       host='localhost',
       max_connections=20,
       retry_max_attempts=5
   )
   
   # Reuse for multiple graphs
   graph1 = Graph(connection_manager=connection_manager)
   graph2 = Graph(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       graph.add_vertex('my_graph', vertex_id, data)
   except Exception as e:
       logger.error(f"Error adding vertex: {e}")
       # Handle error...
   ```

3. **Health Monitoring**
   ```python
   # Regular health checks
   health = connection_manager.health_check()
   if health['status'] != 'healthy':
       logger.warning(f"Connection issues: {health}")
   ```

## Implementation Details

- Uses Redis hashes for vertex data
- Uses Redis sorted sets for edges
- Atomic operations for thread safety
- Connection pooling for performance
- Automatic reconnection with backoff
- Circuit breaker for fault tolerance
- JSON serialization for complex types

## Troubleshooting

1. **Connection Issues**
   ```python
   # Check connection health
   health = connection_manager.health_check()
   print(f"Status: {health['status']}")
   print(f"Latency: {health['latency_ms']}ms")
   ```

2. **Performance Issues**
   ```python
   # Monitor connection pool
   health = connection_manager.health_check()
   print(f"Pool Status: {health['connection_pool']}")
   ```

3. **Memory Usage**
   ```python
   # Monitor vertex count
   vertices = graph.get_vertices('my_graph')
   print(f"Number of vertices: {len(vertices)}")
   ``` 
