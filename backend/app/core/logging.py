import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    # Remove all handlers from root logger
    logging.root.handlers = [InterceptHandler()]
    
    # Set level for root logger
    logging.root.setLevel(settings.LOG_LEVEL)
    
    # Remove all Loguru handlers
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr, 
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level=settings.LOG_LEVEL
    )
    
    # Add file handler
    log_file_path = Path("logs/sepsis_api.log")
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_file_path),
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level=settings.LOG_LEVEL
    )
    
    # Set up other loggers used by dependencies
    for name in ["uvicorn", "uvicorn.access", "fastapi"]:
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False
        
    return logger