"""
Graph facade for Second Person perspective.

Provides access to graph structure via GraphService.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from services.graph_service import GraphService


class GraphFacade:
    """
    Provides access to graph structure.
    
    Wraps GraphService for querying nodes and edges.
    """
    
    def __init__(self, service: Optional["GraphService"]):
        """
        Initialize graph facade.
        
        Args:
            service: GraphService instance (can be None)
        """
        self._service = service
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Get all nodes in the graph.
        
        Returns:
            List of node dicts
        """
        if not self._service:
            return []
        
        if hasattr(self._service, 'get_nodes'):
            return self._service.get_nodes()
        
        if hasattr(self._service, 'nodes'):
            return list(self._service.nodes.values())
        
        return []
    
    def get_edges(self) -> List[Dict[str, Any]]:
        """
        Get all edges in the graph.
        
        Returns:
            List of edge dicts
        """
        if not self._service:
            return []
        
        if hasattr(self._service, 'get_edges'):
            return self._service.get_edges()
        
        if hasattr(self._service, 'edges'):
            return list(self._service.edges)
        
        return []
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific node by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node dict or None
        """
        if not self._service:
            return None
        
        if hasattr(self._service, 'get_node'):
            return self._service.get_node(node_id)
        
        if hasattr(self._service, 'nodes'):
            return self._service.nodes.get(node_id)
        
        return None
    
    def get_node_by_flow_index(self, flow_index: str) -> Optional[Dict[str, Any]]:
        """
        Get node by flow_index.
        
        Args:
            flow_index: Flow index string (e.g., "1.3")
            
        Returns:
            Node dict or None
        """
        if not self._service:
            return None
        
        if hasattr(self._service, 'get_node_by_flow_index'):
            return self._service.get_node_by_flow_index(flow_index)
        
        # Search through nodes
        for node in self.get_nodes():
            if node.get('flow_index') == flow_index:
                return node
        
        return None
    
    def get_children(self, node_id: str) -> List[str]:
        """
        Get child node IDs.
        
        Args:
            node_id: Parent node ID
            
        Returns:
            List of child node IDs
        """
        if not self._service:
            return []
        
        if hasattr(self._service, 'get_children'):
            return self._service.get_children(node_id)
        
        # Build from edges
        children = []
        for edge in self.get_edges():
            if edge.get('source') == node_id:
                children.append(edge.get('target'))
        return children
    
    def get_parents(self, node_id: str) -> List[str]:
        """
        Get parent node IDs.
        
        Args:
            node_id: Child node ID
            
        Returns:
            List of parent node IDs
        """
        if not self._service:
            return []
        
        if hasattr(self._service, 'get_parents'):
            return self._service.get_parents(node_id)
        
        # Build from edges
        parents = []
        for edge in self.get_edges():
            if edge.get('target') == node_id:
                parents.append(edge.get('source'))
        return parents
    
    def get_ancestors(self, node_id: str) -> List[str]:
        """
        Get all ancestor node IDs (recursive parents).
        
        Args:
            node_id: Node ID
            
        Returns:
            List of ancestor node IDs
        """
        ancestors = []
        visited = set()
        to_visit = self.get_parents(node_id)
        
        while to_visit:
            parent = to_visit.pop(0)
            if parent not in visited:
                visited.add(parent)
                ancestors.append(parent)
                to_visit.extend(self.get_parents(parent))
        
        return ancestors
    
    def get_descendants(self, node_id: str) -> List[str]:
        """
        Get all descendant node IDs (recursive children).
        
        Args:
            node_id: Node ID
            
        Returns:
            List of descendant node IDs
        """
        descendants = []
        visited = set()
        to_visit = self.get_children(node_id)
        
        while to_visit:
            child = to_visit.pop(0)
            if child not in visited:
                visited.add(child)
                descendants.append(child)
                to_visit.extend(self.get_children(child))
        
        return descendants
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get graph summary statistics.
        
        Returns:
            Dict with node_count, edge_count, etc.
        """
        nodes = self.get_nodes()
        edges = self.get_edges()
        
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "root_nodes": len([n for n in nodes if not self.get_parents(n.get('id', ''))]),
            "leaf_nodes": len([n for n in nodes if not self.get_children(n.get('id', ''))])
        }

