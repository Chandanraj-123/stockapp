"""
Logger Configuration for Stock Market Dashboard
Enterprise-grade structured logging
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "asctime"
            ):
                try:
                    # Ensure the value is JSON serializable
                    json.dumps(value)
                    extra_fields[key] = value
                except (TypeError, ValueError):
                    extra_fields[key] = str(value)
        
        if extra_fields:
            log_data["extra"] = extra_fields
        
        return json.dumps(log_data)


class StructuredLogger:
    """Structured logger with custom levels and handlers"""
    
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "TRACE": 5,  # Custom level below DEBUG
    }
    
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        log_file: Optional[str] = None,
        use_json: bool = True,
        include_timestamp: bool = True,
        extra_context: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVELS.get(level.upper(), logging.INFO))
        self.extra_context = extra_context or {}
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if use_json:
            console_handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_dir = Path(log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            if use_json:
                file_handler.setFormatter(JSONFormatter())
            else:
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _add_context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add context to log record"""
        context = {**self.extra_context}
        if extra:
            context.update(extra)
        return context
    
    def trace(self, message: str, **kwargs):
        self.logger.log(self.LEVELS["TRACE"], message, extra=self._add_context(kwargs))
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=self._add_context(kwargs))
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=self._add_context(kwargs))
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=self._add_context(kwargs))
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=self._add_context(kwargs))
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, extra=self._add_context(kwargs))
    
    def exception(self, message: str, **kwargs):
        self.logger.exception(message, extra=self._add_context(kwargs))


def setup_logging(
    service_name: str,
    level: str = "INFO",
    log_dir: str = "/workspace/Chandanraj-123__stockapp/logs",
    use_json: bool = True
) -> StructuredLogger:
    """
    Setup logging for a service
    
    Args:
        service_name: Name of the service
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        use_json: Use JSON formatting
    
    Returns:
        Configured StructuredLogger
    """
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = StructuredLogger(
        name=service_name,
        level=level,
        log_file=f"{log_dir}/{service_name}.log",
        use_json=use_json,
        extra_context={"service": service_name}
    )
    
    return logger


# Global logger instance (can be overridden per service)
logger = None


def get_logger() -> StructuredLogger:
    """Get the global logger instance"""
    global logger
    if logger is None:
        logger = setup_logging("stockapp")
    return logger
