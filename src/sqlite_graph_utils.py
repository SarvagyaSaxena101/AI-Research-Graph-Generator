# src/sqlite_graph_utils.py
import sqlite3
import os
from typing import List, Dict, Any

class SQLiteGraphConnector:
    def __init__(self, db_path: str = "graph.db"):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
            print(f"SQLite connection established to {self.db_path}.")
        except sqlite3.Error as e:
            print(f"Failed to connect to SQLite database: {e}")
            self.conn = None

    def _create_tables(self):
        if not self.conn:
            return

        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES nodes (id),
                FOREIGN KEY (target_id) REFERENCES nodes (id)
            )
        """)
        self.conn.commit()
        print("SQLite tables 'nodes' and 'edges' ensured.")

    def close(self):
        if self.conn:
            self.conn.close()
            print("SQLite connection closed.")

    def _execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[sqlite3.Row]:
        if not self.conn:
            print("No SQLite connection available, skipping query execution.")
            return []
        
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, parameters or {})
            self.conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQLite query execution failed: {e}")
            return []

    def get_or_create_node(self, name: str, node_type: str) -> int:
        # Check if node exists
        query = "SELECT id FROM nodes WHERE name = ?"
        result = self._execute_query(query, (name,))
        if result:
            return result[0]["id"]
        
        # If not, create it
        query = "INSERT INTO nodes (name, type) VALUES (?, ?)"
        self._execute_query(query, (name, node_type))
        # Return the ID of the newly created node
        return self.conn.cursor().lastrowid

    def create_relationship(self, source_name: str, source_type: str, 
                            target_name: str, target_type: str, 
                            relationship_type: str):
        source_id = self.get_or_create_node(source_name, source_type)
        target_id = self.get_or_create_node(target_name, target_type)

        # Check if relationship already exists
        query = "SELECT id FROM edges WHERE source_id = ? AND target_id = ? AND type = ?"
        result = self._execute_query(query, (source_id, target_id, relationship_type))
        if result:
            return # Relationship already exists

        query = "INSERT INTO edges (source_id, target_id, type) VALUES (?, ?, ?)"
        self._execute_query(query, (source_id, target_id, relationship_type))

    def get_all_entities_and_relations(self) -> Dict[str, List[Dict]]:
        nodes_query = "SELECT id, name, type FROM nodes"
        nodes_raw = self._execute_query(nodes_query)
        
        nodes = []
        node_id_to_name = {}
        for n in nodes_raw:
            nodes.append({"id": n["id"], "name": n["name"], "labels": [n["type"]]}) # Neo4j format has 'labels'
            node_id_to_name[n["id"]] = n["name"]

        rels_query = "SELECT source_id, target_id, type FROM edges"
        rels_raw = self._execute_query(rels_query)

        relationships = []
        for r in rels_raw:
            relationships.append({
                "source_id": r["source_id"],
                "target_id": r["target_id"],
                "type": r["type"]
            })
        
        return {"nodes": nodes, "relationships": relationships}

    def clear_graph(self):
        if not self.conn:
            print("No SQLite connection available, cannot clear graph.")
            return
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM edges")
        cursor.execute("DELETE FROM nodes")
        self.conn.commit()
        print("SQLite graph cleared.")

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    db_connector = SQLiteGraphConnector("test_graph.db")
    db_connector.clear_graph()

    # Create nodes
    db_connector.get_or_create_node("ConceptA", "Concept")
    db_connector.get_or_create_node("PersonX", "Person")
    db_connector.get_or_create_node("ConceptB", "Concept")

    # Create relationships
    db_connector.create_relationship("PersonX", "Person", "ConceptA", "Concept", "DISCUSSES")
    db_connector.create_relationship("ConceptA", "Concept", "ConceptB", "Concept", "RELATED_TO")

    # Get all
    graph_data = db_connector.get_all_entities_and_relations()
    print("Nodes:", graph_data["nodes"])
    print("Relationships:", graph_data["relationships"])

    db_connector.close()