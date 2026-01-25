"""
Database facade for Second Person perspective.

Provides direct access to orchestration.db via OrchestratorDB.
"""

import json
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from infra._orchest._db import OrchestratorDB


class DatabaseFacade:
    """
    Provides direct database queries for orchestration.db.
    
    Tables available:
    - executions: execution records (run_id, cycle, flow_index, status, etc.)
    - logs: detailed execution logs
    - checkpoints: state snapshots (run_id, cycle, inference_count, state_json)
    - run_metadata: run configuration and environment
    """
    
    def __init__(self, db: Optional["OrchestratorDB"]):
        """
        Initialize database facade.
        
        Args:
            db: OrchestratorDB instance
        """
        self._db = db
    
    def query(self, sql: str, params: Tuple = ()) -> List[Dict]:
        """
        Execute raw SQL query (SELECT only for safety).
        
        Args:
            sql: SQL query (must be SELECT)
            params: Query parameters
            
        Returns:
            List of result rows as dicts
        """
        if not self._db:
            return []
        
        # Safety: only allow SELECT
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        
        try:
            import sqlite3
            conn = self._db.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_runs(self) -> List[Dict]:
        """
        List all runs in the database.
        
        Returns:
            List of run metadata dicts
        """
        if not self._db:
            return []
        
        return self.query(
            "SELECT run_id, metadata_json, timestamp FROM run_metadata ORDER BY timestamp DESC"
        )
    
    def get_run_metadata(self, run_id: str) -> Dict:
        """
        Get metadata for a specific run.
        
        Args:
            run_id: The run ID
            
        Returns:
            Metadata dict
        """
        if not self._db:
            return {}
        
        rows = self.query(
            "SELECT metadata_json FROM run_metadata WHERE run_id = ?",
            (run_id,)
        )
        if rows and 'metadata_json' in rows[0]:
            try:
                return json.loads(rows[0]['metadata_json'])
            except:
                return rows[0]
        return {}
    
    def get_executions(
        self, 
        run_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get execution records.
        
        Args:
            run_id: Optional filter by run_id
            limit: Maximum records to return
            
        Returns:
            List of execution records
        """
        if not self._db:
            return []
        
        if run_id:
            return self.query(
                "SELECT * FROM executions WHERE run_id = ? ORDER BY id DESC LIMIT ?",
                (run_id, limit)
            )
        else:
            return self.query(
                "SELECT * FROM executions ORDER BY id DESC LIMIT ?",
                (limit,)
            )
    
    def get_execution_logs(self, execution_id: int) -> List[str]:
        """
        Get logs for a specific execution.
        
        Args:
            execution_id: The execution record ID
            
        Returns:
            List of log content strings
        """
        if not self._db:
            return []
        
        rows = self.query(
            "SELECT log_content FROM logs WHERE execution_id = ?",
            (execution_id,)
        )
        return [row.get('log_content', '') for row in rows]
    
    def get_checkpoints(
        self, 
        run_id: Optional[str] = None,
        cycle: Optional[int] = None
    ) -> List[Dict]:
        """
        Get checkpoints.
        
        Args:
            run_id: Optional filter by run_id
            cycle: Optional filter by cycle
            
        Returns:
            List of checkpoint metadata (without full state)
        """
        if not self._db:
            return []
        
        sql = "SELECT run_id, cycle, inference_count, timestamp FROM checkpoints"
        params: List[Any] = []
        conditions = []
        
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        if cycle is not None:
            conditions.append("cycle = ?")
            params.append(cycle)
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY timestamp DESC LIMIT 100"
        
        return self.query(sql, tuple(params))
    
    def get_checkpoint_state(
        self, 
        run_id: str, 
        cycle: int, 
        inference_count: int = 0
    ) -> Dict:
        """
        Get full state from a specific checkpoint.
        
        Args:
            run_id: Run ID
            cycle: Cycle number
            inference_count: Inference count within cycle
            
        Returns:
            Checkpoint state dict
        """
        if not self._db:
            return {}
        
        rows = self.query(
            "SELECT state_json FROM checkpoints WHERE run_id = ? AND cycle = ? AND inference_count = ?",
            (run_id, cycle, inference_count)
        )
        
        if rows and 'state_json' in rows[0]:
            try:
                return json.loads(rows[0]['state_json'])
            except:
                return {"raw": rows[0]['state_json']}
        return {}
    
    def get_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        if not self._db:
            return []
        
        rows = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        return [row.get('name', '') for row in rows]
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """
        Get schema (columns) for a table.
        
        Args:
            table_name: Table name
            
        Returns:
            List of column info dicts
        """
        if not self._db:
            return []
        
        return self.query(f"PRAGMA table_info({table_name})")
    
    def get_table_count(self, table_name: str) -> int:
        """
        Get row count for a table.
        
        Args:
            table_name: Table name
            
        Returns:
            Row count
        """
        if not self._db:
            return 0
        
        # Sanitize table name
        if not table_name.isidentifier():
            return 0
        
        rows = self.query(f"SELECT COUNT(*) as count FROM {table_name}")
        return rows[0].get('count', 0) if rows else 0

