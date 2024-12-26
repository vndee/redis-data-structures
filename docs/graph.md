# Graph (Adjacency List)

A Redis-backed directed graph implementation using adjacency lists. Vertices can store arbitrary data and edges can have custom weights. Perfect for social networks, dependency graphs, routing systems, and any application requiring relationship modeling with weighted connections.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `add_vertex` | $O(1)$ | $O(1)$ | Add a vertex with optional data | `HSET` |
| `add_edge` | $O(1)$ | $O(1)$ | Add a weighted edge between vertices | `HSET` |
| `remove_vertex` | $O(n)$ | $O(n)$ | Remove vertex and all connected edges | `DELETE`, `HDEL` |
| `remove_edge` | $O(1)$ | $O(1)$ | Remove an edge | `HDEL` |
| `get_vertex_data` | $O(1)$ | $O(1)$ | Get vertex data | `HGET` |
| `get_neighbors` | $O(1)$ | $O(1)$ | Get all neighbors with edge weights | `HGETALL` |
| `get_vertices` | $O(n)$ | $O(n)$ | Get all vertices | `SCAN` |
| `vertex_exists` | $O(1)$ | $O(1)$ | Check if vertex exists | `EXISTS` |
| `get_edge_weight` | $O(1)$ | $O(1)$ | Get weight of an edge | `HGET` |
| `clear` | $O(n)$ | $O(n)$ | Remove all vertices and edges | `DELETE` |

where:
- $n$ is the number of vertices in the graph

## Basic Usage

```python
from redis_data_structures import Graph

# Initialize graph
graph = Graph("my_graph")

# Add vertices with data
graph.add_vertex("v1", {"name": "Vertex 1", "value": 42})
graph.add_vertex("v2", {"name": "Vertex 2", "value": 43})

# Add weighted edges
graph.add_edge("v1", "v2", weight=1.5)

# Get vertex data
data = graph.get_vertex_data("v1")

# Get neighbors with weights
neighbors = graph.get_neighbors("v1")  # {"v2": 1.5}

# Check edge weight
weight = graph.get_edge_weight("v1", "v2")  # 1.5

# Remove edges and vertices
graph.remove_edge("v1", "v2")
graph.remove_vertex("v1")

# Clear graph
graph.clear()
```

## Advanced Usage

```python
from redis_data_structures import Graph
from typing import Dict, Any, Set, Optional
from datetime import datetime

class SocialNetwork:
    def __init__(self):
        self.graph = Graph("social_network")
    
    def add_user(self, user_id: str, profile: Dict[str, Any]) -> bool:
        """Add a user to the network."""
        profile_data = {
            **profile,
            "joined_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
        return self.graph.add_vertex(user_id, profile_data)
    
    def create_connection(self, user1: str, user2: str, strength: float) -> bool:
        """Create a bidirectional connection between users."""
        if not all([
            self.graph.vertex_exists(user1),
            self.graph.vertex_exists(user2)
        ]):
            return False
            
        return all([
            self.graph.add_edge(user1, user2, strength),
            self.graph.add_edge(user2, user1, strength)
        ])
    
    def get_connections(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all connections for a user with their profiles."""
        connections = {}
        neighbors = self.graph.get_neighbors(user_id)
        
        for neighbor_id, strength in neighbors.items():
            profile = self.graph.get_vertex_data(neighbor_id)
            if profile:
                connections[neighbor_id] = {
                    **profile,
                    "connection_strength": strength
                }
        
        return connections
    
    def get_mutual_connections(self, user1: str, user2: str) -> Set[str]:
        """Find mutual connections between two users."""
        user1_connections = set(self.graph.get_neighbors(user1).keys())
        user2_connections = set(self.graph.get_neighbors(user2).keys())
        return user1_connections & user2_connections
    
    def remove_user(self, user_id: str) -> bool:
        """Remove a user and all their connections."""
        return self.graph.remove_vertex(user_id)

# Usage
network = SocialNetwork()

# Add users
network.add_user("alice", {
    "name": "Alice Smith",
    "age": 28,
    "interests": ["tech", "music"]
})
network.add_user("bob", {
    "name": "Bob Johnson",
    "age": 32,
    "interests": ["sports", "books"]
})

# Create connections
network.create_connection("alice", "bob", 0.8)

# Get connections
alice_connections = network.get_connections("alice")
```

## Example Use Cases

### 1. Dependency Graph Manager

```python
from redis_data_structures import Graph
from typing import Dict, Any, Set, Optional
from datetime import datetime
import json

class DependencyManager:
    def __init__(self):
        self.graph = Graph("dependency_graph")
    
    def add_package(self, package_id: str, metadata: Dict[str, Any]) -> bool:
        """Add a package to the dependency graph."""
        package_data = {
            **metadata,
            "added_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        return self.graph.add_vertex(package_id, package_data)
    
    def add_dependency(self, package: str, depends_on: str, version_spec: str = "*") -> bool:
        """Add a dependency relationship."""
        return self.graph.add_edge(package, depends_on, 1.0)
    
    def get_direct_dependencies(self, package: str) -> Dict[str, Dict[str, Any]]:
        """Get direct dependencies of a package."""
        deps = {}
        for dep_id in self.graph.get_neighbors(package):
            metadata = self.graph.get_vertex_data(dep_id)
            if metadata:
                deps[dep_id] = metadata
        return deps
    
    def get_all_dependencies(self, package: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """Get all dependencies recursively."""
        if visited is None:
            visited = set()
            
        if package in visited:
            return visited
            
        visited.add(package)
        for dep in self.graph.get_neighbors(package):
            self.get_all_dependencies(dep, visited)
            
        return visited
    
    def find_cycles(self) -> list[list[str]]:
        """Find dependency cycles."""
        cycles = []
        visited = set()
        path = []
        
        def dfs(vertex: str):
            if vertex in path:
                cycle_start = path.index(vertex)
                cycles.append(path[cycle_start:])
                return
            
            if vertex in visited:
                return
                
            visited.add(vertex)
            path.append(vertex)
            
            for neighbor in self.graph.get_neighbors(vertex):
                dfs(neighbor)
                
            path.pop()
        
        for vertex in self.graph.get_vertices():
            dfs(vertex)
            
        return cycles

# Usage
deps = DependencyManager()

# Add packages
deps.add_package("app", {
    "name": "MyApp",
    "version": "1.0.0"
})
deps.add_package("db", {
    "name": "Database",
    "version": "2.1.0"
})

# Add dependencies
deps.add_dependency("app", "db")

# Check dependencies
direct_deps = deps.get_direct_dependencies("app")
all_deps = deps.get_all_dependencies("app")
cycles = deps.find_cycles()
```

### 2. Service Mesh Router

```python
from redis_data_structures import Graph
from typing import Dict, Any, List, Optional
from datetime import datetime
import heapq

class ServiceRouter:
    def __init__(self):
        self.graph = Graph("service_mesh")
    
    def register_service(self, service_id: str, metadata: Dict[str, Any]) -> bool:
        """Register a service in the mesh."""
        service_data = {
            **metadata,
            "registered_at": datetime.now().isoformat(),
            "health_check": "healthy",
            "last_ping": datetime.now().isoformat()
        }
        return self.graph.add_vertex(service_id, service_data)
    
    def add_route(self, from_service: str, to_service: str, latency: float) -> bool:
        """Add a route between services with measured latency."""
        return self.graph.add_edge(
            from_service, 
            to_service, 
            weight=latency
        )
    
    def update_latency(self, from_service: str, to_service: str, latency: float) -> bool:
        """Update route latency."""
        return self.graph.add_edge(
            from_service,
            to_service,
            weight=latency
        )
    
    def find_fastest_path(self, start: str, end: str) -> tuple[List[str], float]:
        """Find fastest path between services using Dijkstra's algorithm."""
        distances = {v: float('infinity') for v in self.graph.get_vertices()}
        distances[start] = 0
        previous = {v: None for v in self.graph.get_vertices()}
        pq = [(0, start)]
        
        while pq:
            current_distance, current = heapq.heappop(pq)
            
            if current == end:
                break
                
            if current_distance > distances[current]:
                continue
                
            for neighbor, latency in self.graph.get_neighbors(current).items():
                distance = current_distance + latency
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        path = []
        current = end
        while current:
            path.append(current)
            current = previous[current]
        
        return list(reversed(path)), distances[end]
    
    def get_service_health(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service health information."""
        return self.graph.get_vertex_data(service_id)

# Usage
router = ServiceRouter()

# Register services
router.register_service("auth", {
    "name": "Authentication Service",
    "version": "1.0.0",
    "endpoint": "http://auth:8080"
})
router.register_service("users", {
    "name": "User Service",
    "version": "1.0.0",
    "endpoint": "http://users:8080"
})

# Add routes with latencies
router.add_route("auth", "users", 10.5)  # 10.5ms latency
router.add_route("users", "auth", 10.5)

# Find fastest path
path, latency = router.find_fastest_path("auth", "users")
```

### 3. Knowledge Graph

```python
from redis_data_structures import Graph
from typing import Dict, Any, Set, List
from datetime import datetime
import json

class KnowledgeGraph:
    def __init__(self):
        self.graph = Graph("knowledge_graph")
    
    def add_entity(self, entity_id: str, metadata: Dict[str, Any]) -> bool:
        """Add an entity to the knowledge graph."""
        entity_data = {
            **metadata,
            "added_at": datetime.now().isoformat(),
            "type": metadata.get("type", "unknown")
        }
        return self.graph.add_vertex(entity_id, entity_data)
    
    def add_relationship(
        self, 
        from_entity: str, 
        to_entity: str, 
        relationship_type: str,
        confidence: float = 1.0
    ) -> bool:
        """Add a relationship between entities."""
        relationship = {
            "type": relationship_type,
            "confidence": confidence,
            "created_at": datetime.now().isoformat()
        }
        return self.graph.add_edge(from_entity, to_entity, confidence)
    
    def get_entity_relationships(self, entity_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all relationships for an entity."""
        relationships = {}
        neighbors = self.graph.get_neighbors(entity_id)
        
        for neighbor_id, confidence in neighbors.items():
            target = self.graph.get_vertex_data(self.kg_key, neighbor_id)
            if target:
                relationships[neighbor_id] = {
                    "entity": target,
                    "confidence": confidence
                }
        
        return relationships
    
    def find_path_between_entities(
        self, 
        start: str, 
        end: str, 
        max_depth: int = 5
    ) -> List[tuple[str, float]]:
        """Find a path between entities with confidence scores."""
        def dfs(
            current: str,
            target: str,
            depth: int,
            path: List[tuple[str, float]],
            visited: Set[str]
        ) -> Optional[List[tuple[str, float]]]:
            if depth > max_depth:
                return None
                
            if current == target:
                return path
                
            visited.add(current)
            
            for neighbor, confidence in self.graph.get_neighbors(self.kg_key, current).items():
                if neighbor not in visited:
                    result = dfs(
                        neighbor,
                        target,
                        depth + 1,
                        path + [(neighbor, confidence)],
                        visited
                    )
                    if result:
                        return result
            
            visited.remove(current)
            return None
        
        result = dfs(start, end, 0, [], set())
        return result if result else []

# Usage
kg = KnowledgeGraph()

# Add entities
kg.add_entity("person:john",