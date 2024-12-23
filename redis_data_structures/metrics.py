"""Metrics collection for Redis data structures."""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class OperationMetrics:
    """Metrics for a single operation."""

    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """Get operation duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None


@dataclass
class DataStructureMetrics:
    """Metrics for a data structure instance."""

    name: str
    operations: List[OperationMetrics] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add_operation(self, operation: str) -> OperationMetrics:
        """Start tracking a new operation."""
        metrics = OperationMetrics(operation=operation, start_time=datetime.now())
        with self._lock:
            self.operations.append(metrics)
        return metrics

    def complete_operation(
        self, metrics: OperationMetrics, success: bool = True, error: Optional[str] = None,
    ):
        """Complete tracking of an operation."""
        metrics.end_time = datetime.now()
        metrics.success = success
        metrics.error = error

    def get_stats(self, window: timedelta = timedelta(minutes=5)) -> Dict:
        """Get statistics for operations within time window."""
        now = datetime.now()
        window_start = now - window

        # Filter operations within window
        recent_ops = [op for op in self.operations if op.start_time >= window_start]

        if not recent_ops:
            return {
                "total_operations": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
                "error_count": 0,
            }

        # Calculate statistics
        total_ops = len(recent_ops)
        successful_ops = sum(1 for op in recent_ops if op.success)
        error_ops = sum(1 for op in recent_ops if not op.success)

        durations = [op.duration for op in recent_ops if op.duration is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "total_operations": total_ops,
            "success_rate": (successful_ops / total_ops) * 100,
            "avg_duration_ms": avg_duration,
            "error_count": error_ops,
        }


class MetricsCollector:
    """Global metrics collector for all data structures."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize metrics collector."""
        if not hasattr(self, "initialized"):
            self.metrics: Dict[str, DataStructureMetrics] = {}
            self.initialized = True

    def get_metrics(self, name: str) -> DataStructureMetrics:
        """Get or create metrics for a data structure."""
        if name not in self.metrics:
            with self._lock:
                if name not in self.metrics:
                    self.metrics[name] = DataStructureMetrics(name)
        return self.metrics[name]

    def get_all_stats(self, window: timedelta = timedelta(minutes=5)) -> Dict[str, Dict]:
        """Get statistics for all data structures."""
        return {name: metrics.get_stats(window) for name, metrics in self.metrics.items()}

    def clear_old_metrics(self, max_age: timedelta = timedelta(hours=24)):
        """Clear metrics older than max_age."""
        cutoff = datetime.now() - max_age
        for metrics in self.metrics.values():
            with metrics._lock:
                metrics.operations = [op for op in metrics.operations if op.start_time >= cutoff]


def track_operation(operation: str):
    """Decorator to track operation metrics."""

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            metrics_collector = MetricsCollector()
            metrics = metrics_collector.get_metrics(self.__class__.__name__)
            operation_metrics = metrics.add_operation(operation)

            try:
                result = func(self, *args, **kwargs)
                metrics.complete_operation(operation_metrics, success=True)
                return result
            except Exception as e:
                metrics.complete_operation(operation_metrics, success=False, error=str(e))
                raise

        return wrapper

    return decorator
