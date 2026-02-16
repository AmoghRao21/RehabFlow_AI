"""
Concurrency management using ThreadPoolExecutor.
Provides thread-safe execution for long-running operations.
"""
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, List
from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class ConcurrencyManager:
    """Manages concurrent task execution."""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize concurrency manager.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers or Config.MAX_WORKERS
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        logger.info(f"ConcurrencyManager initialized with {self.max_workers} workers")
    
    def submit(self, func: Callable, *args, **kwargs) -> Future:
        """
        Submit a function for asynchronous execution.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Future object representing the pending operation
        """
        logger.debug(f"Submitting task: {func.__name__}")
        return self.executor.submit(func, *args, **kwargs)
    
    def map(self, func: Callable, iterable: List[Any]) -> List[Any]:
        """
        Map a function over an iterable concurrently.
        
        Args:
            func: Function to apply
            iterable: Items to process
            
        Returns:
            List of results
        """
        logger.debug(f"Mapping function {func.__name__} over {len(iterable)} items")
        return list(self.executor.map(func, iterable))
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.
        
        Args:
            wait: Whether to wait for pending tasks to complete
        """
        logger.info("Shutting down ConcurrencyManager...")
        self.executor.shutdown(wait=wait)
        logger.info("ConcurrencyManager shut down successfully")


# Global concurrency manager instance
concurrency_manager = ConcurrencyManager()


def submit_task(func: Callable, *args, **kwargs) -> Future:
    """
    Convenience function to submit a task.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Future object
    """
    return concurrency_manager.submit(func, *args, **kwargs)


def map_concurrent(func: Callable, iterable: List[Any]) -> List[Any]:
    """
    Convenience function to map concurrently.
    
    Args:
        func: Function to apply
        iterable: Items to process
        
    Returns:
        List of results
    """
    return concurrency_manager.map(func, iterable)
