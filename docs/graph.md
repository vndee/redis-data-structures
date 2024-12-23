# Graph

A Redis-backed directed graph implementation using adjacency lists. Perfect for representing relationships between entities, social networks, dependency graphs, and other connected data structures. The implementation uses Redis Hashes to store vertex data and adjacency lists, providing O(1) operations for most graph operations.

## Features

- O(1) vertex and edge operations
- Vertex data storage
- Weighted edges
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations

## Operations

| Operation        | Time Complexity | Description |
|-----------------|----------------|-------------|
| `add_vertex`    | O(1)          | Add a vertex with optional data |
| `add_edge`      | O(1)          | Add a weighted edge between vertices |
| `remove_vertex` | O(V + E)      | Remove a vertex and all its edges |
| `remove_edge`   | O(1)          | Remove an edge between vertices |
| `get_neighbors` | O(1)          | Get all neighbors of a vertex |
| `get_vertices`  | O(V)          | Get all vertices in the graph |

Where V is the number of vertices and E is the number of edges.

## Basic Usage

```python
from redis_data_structures import Graph

# Initialize graph
graph = Graph(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Add vertices with data
graph.add_vertex('my_graph', 'v1', {'name': 'Vertex 1', 'value': 42})
graph.add_vertex('my_graph', 'v2', {'name': 'Vertex 2', 'value': 84})

# Add weighted edges
graph.add_edge('my_graph', 'v1', 'v2', weight=1.5)

# Get vertex data
data = graph.get_vertex_data('my_graph', 'v1')

# Get neighbors with weights
neighbors = graph.get_neighbors('my_graph', 'v1')

# Remove vertex (and all its edges)
graph.remove_vertex('my_graph', 'v1')

# Clear graph
graph.clear('my_graph')
```

## Example Use Cases

### 1. Social Network

Perfect for representing user relationships with weighted connections.

```python
class SocialNetwork:
    def __init__(self):
        self.graph = Graph(host='localhost', port=6379)
        self.network_key = 'social:network'
    
    def add_user(self, user_id: str, profile: dict):
        """Add a user to the network."""
        return self.graph.add_vertex(self.network_key, user_id, profile)
    
    def add_friendship(self, user1: str, user2: str, strength: float):
        """Create a bidirectional friendship between users."""
        # Add both directions since friendship is mutual
        self.graph.add_edge(self.network_key, user1, user2, strength)
        self.graph.add_edge(self.network_key, user2, user1, strength)
    
    def get_friends(self, user_id: str) -> dict:
        """Get all friends of a user with friendship strengths."""
        return self.graph.get_neighbors(self.network_key, user_id)
    
    def remove_user(self, user_id: str):
        """Remove a user and all their connections."""
        return self.graph.remove_vertex(self.network_key, user_id)

# Usage
network = SocialNetwork()
network.add_user('alice', {'name': 'Alice', 'age': 28})
network.add_user('bob', {'name': 'Bob', 'age': 32})
network.add_friendship('alice', 'bob', 0.8)  # Strong friendship
```

### 2. Dependency Graph

Ideal for managing software dependencies or task dependencies.

```python
class DependencyGraph:
    def __init__(self):
        self.graph = Graph(host='localhost', port=6379)
        self.dep_key = 'dependency:graph'
    
    def add_task(self, task_id: str, task_info: dict):
        """Add a task to the dependency graph."""
        return self.graph.add_vertex(self.dep_key, task_id, task_info)
    
    def add_dependency(self, task: str, depends_on: str, priority: float = 1.0):
        """Add a dependency between tasks."""
        return self.graph.add_edge(self.dep_key, task, depends_on, priority)
    
    def get_dependencies(self, task: str) -> dict:
        """Get all dependencies for a task."""
        return self.graph.get_neighbors(self.dep_key, task)
    
    def remove_task(self, task: str):
        """Remove a task and its dependencies."""
        return self.graph.remove_vertex(self.dep_key, task)

# Usage
deps = DependencyGraph()
deps.add_task('build', {'command': 'make build'})
deps.add_task('test', {'command': 'make test'})
deps.add_dependency('test', 'build', 1.0)  # test depends on build
```

### 3. Knowledge Graph

Perfect for representing connected information with relationships.

```python
class KnowledgeGraph:
    def __init__(self):
        self.graph = Graph(host='localhost', port=6379)
        self.kg_key = 'knowledge:graph'
    
    def add_entity(self, entity_id: str, properties: dict):
        """Add an entity to the knowledge graph."""
        return self.graph.add_vertex(self.kg_key, entity_id, properties)
    
    def add_relationship(self, from_entity: str, to_entity: str, 
                        relationship: str, confidence: float):
        """Add a relationship between entities."""
        edge_data = {'type': relationship, 'confidence': confidence}
        return self.graph.add_edge(self.kg_key, from_entity, to_entity, confidence)
    
    def get_relationships(self, entity: str) -> dict:
        """Get all relationships for an entity."""
        return self.graph.get_neighbors(self.kg_key, entity)

# Usage
kg = KnowledgeGraph()
kg.add_entity('person:john', {'name': 'John', 'type': 'Person'})
kg.add_entity('company:acme', {'name': 'ACME Corp', 'type': 'Company'})
kg.add_relationship('person:john', 'company:acme', 'WORKS_FOR', 0.9)
```

## Best Practices

1. **Key Management**
   - Use descriptive key prefixes: `graph:social`, `graph:deps`, etc.
   - Consider implementing key expiration for temporary graphs
   - Clear graphs that are no longer needed

2. **Error Handling**
   ```python
   try:
       graph.add_vertex('my_graph', 'v1', data)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor graph size to prevent memory issues
   - Implement cleanup strategies for old/unused data
   ```python
   if len(graph.get_vertices('my_graph')) > MAX_VERTICES:
       # Handle graph size limit...
       pass
   ```

4. **Performance**
   - Use batch operations when possible
   - Consider caching frequently accessed vertices/edges
   - Monitor Redis memory usage

## Common Patterns

### 1. Bidirectional Relationships
```python
def add_bidirectional_edge(graph, key, v1, v2, weight=1.0):
    """Add edges in both directions."""
    graph.add_edge(key, v1, v2, weight)
    graph.add_edge(key, v2, v1, weight)
```

### 2. Vertex Data Updates
```python
def update_vertex_data(graph, key, vertex, update_func):
    """Update vertex data atomically."""
    data = graph.get_vertex_data(key, vertex) or {}
    updated_data = update_func(data)
    graph.add_vertex(key, vertex, updated_data)
```

### 3. Graph Traversal
```python
def depth_first_search(graph, key, start_vertex):
    """Perform DFS traversal."""
    visited = set()
    
    def dfs(vertex):
        visited.add(vertex)
        for neighbor in graph.get_neighbors(key, vertex):
            if neighbor not in visited:
                dfs(neighbor)
    
    dfs(start_vertex)
    return visited
```

## Implementation Details

The graph implementation uses Redis data structures efficiently:

1. **Vertex Data Storage**
   - Uses Redis Hashes: `{key}:vertex:{vertex_id}`
   - Stores serialized vertex data
   - O(1) access and updates

2. **Edge Storage**
   - Uses Redis Hashes: `{key}:adj:{vertex_id}`
   - Maps neighbor vertices to edge weights
   - O(1) edge operations

3. **Vertex Management**
   - Combines vertex data and adjacency lists
   - Efficient vertex existence checks
   - Atomic vertex operations

## Performance Considerations

1. **Network Latency**
   - Redis operations are network calls
   - Consider batch operations for better throughput

2. **Memory Usage**
   - Each vertex and edge consumes Redis memory
   - Monitor Redis memory usage
   - Implement cleanup strategies

3. **Scalability**
   - Graph operations are atomic
   - Consider sharding for very large graphs
   - Monitor Redis performance

## Troubleshooting

1. **Graph Always Empty**
   - Check Redis connection
   - Verify key names
   - Check if vertices are being added correctly

2. **Memory Issues**
   - Monitor graph size
   - Implement vertex/edge limits
   - Clear old/unused graphs

3. **Slow Operations**
   - Check network latency
   - Consider batch operations
   - Monitor Redis performance
``` 
