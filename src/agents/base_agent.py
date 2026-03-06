# src/agents/base_agent.py
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import hashlib
import time

class BaseAgent(ABC):
    """
    Base class for all SentinelAI agents
    Provides common functionality for logging, metrics, and communication
    """
    
    def __init__(self, agent_id: str, agent_name: str, version: str = "1.0.0"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.version = version
        self.status = "initialized"
        self.created_at = datetime.utcnow()
        self.last_active = self.created_at
        self.metrics = {}
        self.config = {}
        
        # Setup logging
        self.logger = logging.getLogger(f"sentinelai.{agent_name}")
        self.logger.setLevel(logging.INFO)
        
        # Performance tracking
        self.processing_times = []
        self.total_processed = 0
        self.error_count = 0
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - must be implemented by each agent
        """
        pass
    
    def log_event(self, event_type: str, details: Dict[str, Any] = None):
        """
        Log agent events for audit trail and monitoring
        """
        event = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(event))
        
        # In production, also send to centralized logging
        self._send_to_monitoring(event)
    
    def _send_to_monitoring(self, event: Dict[str, Any]):
        """
        Send event to monitoring system (Prometheus, etc.)
        For now, just log
        """
        # Future: Push to Prometheus, Grafana, etc.
        pass
    
    def measure_time(self, func):
        """
        Decorator to measure function execution time
        """
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            self.processing_times.append(duration)
            # Keep only last 100 measurements
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)
            
            return result
        return wrapper
    
    def get_avg_processing_time(self) -> float:
        """Get average processing time"""
        if not self.processing_times:
            return 0
        return sum(self.processing_times) / len(self.processing_times)
    
    def update_metrics(self, **kwargs):
        """Update agent metrics"""
        self.metrics.update(kwargs)
        self.metrics["last_update"] = datetime.utcnow().isoformat()
    
    def health_check(self) -> Dict[str, Any]:
        """Return agent health status"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "status": self.status,
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
            "last_active": self.last_active.isoformat(),
            "total_processed": self.total_processed,
            "error_count": self.error_count,
            "avg_processing_time_ms": self.get_avg_processing_time() * 1000,
            "metrics": self.metrics
        }
    
    def save_state(self, filepath: str):
        """Save agent state to disk"""
        state = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "metrics": self.metrics,
            "config": self.config,
            "total_processed": self.total_processed,
            "created_at": self.created_at.isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Load agent state from disk"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.metrics = state.get("metrics", {})
        self.config = state.get("config", {})
        self.total_processed = state.get("total_processed", 0)
