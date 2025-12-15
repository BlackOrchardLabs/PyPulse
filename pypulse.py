"""
PyPulse Progress Wrapper
Drop-in replacement for tqdm with desktop widget integration
"""

import time
import sys
import os
from typing import Iterable, Optional, Any, Union
from datetime import datetime, timezone
from pathlib import Path
import atexit
import threading
from pypulse_state import pulse_state

class PulseProgress:
    """
    Iterator wrapper that reports progress to PyPulse widget
    Similar interface to tqdm for easy migration
    """
    
    def __init__(self, 
                 iterable: Optional[Iterable] = None,
                 desc: Optional[str] = None,
                 total: Optional[int] = None,
                 task: Optional[str] = None,
                 step: Optional[str] = None,
                 unit: str = "it",
                 unit_scale: bool = False,
                 leave: bool = True,
                 file: Optional[Any] = None,
                 ncols: Optional[int] = None,
                 mininterval: float = 0.1,
                 maxinterval: float = 10.0,
                 miniters: Optional[int] = None,
                 ascii: Optional[bool] = None,
                 disable: bool = False,
                 unit_divisor: int = 1000,
                 initial: int = 0,
                 colour: Optional[str] = None):
        
        self.iterable = iterable
        self.desc = desc or task or "Processing"
        self.step = step or "1/1"
        self.total = total
        self.unit = unit
        self.unit_scale = unit_scale
        self.leave = leave
        self.file = file or sys.stderr
        self.ncols = ncols
        self.mininterval = mininterval
        self.maxinterval = maxinterval
        self.miniters = miniters
        self.disable = disable
        self.unit_divisor = unit_divisor
        self.initial = initial
        
        # Progress tracking
        self.n = initial
        self.last_print_n = initial
        self.last_print_t = time.time()
        self.start_t = self.last_print_t
        self.last_update_t = self.last_print_t
        
        # Auto-detect total if not provided
        if self.total is None and hasattr(iterable, "__len__"):
            try:
                self.total = len(iterable)
            except (TypeError, AttributeError):
                pass
        
        # Register cleanup
        atexit.register(self.close)
        
        # Start progress reporting
        if not self.disable:
            self._report_progress()
    
    def __iter__(self):
        """Iterate and report progress"""
        if self.disable or self.iterable is None:
            return iter([]) if self.iterable is None else iter(self.iterable)
        
        try:
            for obj in self.iterable:
                yield obj
                self.update(1)
        finally:
            self.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def update(self, n: int = 1):
        """Update progress counter"""
        if self.disable:
            return
        
        self.n += n
        now = time.time()
        
        # Check if we should update display
        if (now - self.last_update_t) >= self.mininterval:
            self._report_progress()
            self.last_update_t = now
    
    def close(self):
        """Clean up and mark as complete"""
        if not self.disable and self.n > 0:
            # Mark task as complete
            pulse_state.complete_task(self.desc)
            
            # Print final progress if leave=True
            if self.leave:
                self._print_final()
    
    def _report_progress(self):
        """Report progress to widget"""
        if self.disable:
            return
        
        # Calculate progress
        if self.total:
            progress = self.n / self.total
            eta = self._calculate_eta()
        else:
            progress = 0.0  # Unknown total
            eta = None
        
        # Update widget
        current_step = f"{self.step}: {self.n}/{self.total or '?'}{self.unit}"
        
        pulse_state.update_progress(
            task_name=self.desc,
            current_step=current_step,
            progress=progress,
            eta_seconds=eta
        )
    
    def _calculate_eta(self) -> Optional[int]:
        """Calculate estimated time to completion in seconds"""
        if not self.total or self.n <= 0:
            return None
        
        elapsed = time.time() - self.start_t
        speed = self.n / elapsed if elapsed > 0 else 0
        
        if speed > 0:
            remaining = (self.total - self.n) / speed
            return int(remaining)
        return None
    
    def _format_time(self, seconds: int) -> str:
        """Format time in human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _print_final(self):
        """Print final progress to console"""
        if self.total:
            percentage = (self.n / self.total) * 100
            elapsed = time.time() - self.start_t
            speed = self.n / elapsed if elapsed > 0 else 0
            
            print(f"{self.desc}: {self.n}/{self.total} ({percentage:.1f}%) "
                  f"[{self._format_time(int(elapsed))}, {speed:.2f}{self.unit}/s]",
                  file=self.file)
        else:
            elapsed = time.time() - self.start_t
            print(f"{self.desc}: {self.n} items processed "
                  f"[{self._format_time(int(elapsed))}]",
                  file=self.file)

class PulseTask:
    """
    Context manager for multi-step tasks with progress reporting
    """
    
    def __init__(self, 
                 task_name: str,
                 total_steps: int = 1,
                 step_format: str = "Step {step}/{total}: {description}"):
        self.task_name = task_name
        self.total_steps = total_steps
        self.step_format = step_format
        self.current_step = 0
        self.start_time = None
        self.closed = False
        
        # Register cleanup
        atexit.register(self.close)
    
    def __enter__(self):
        self.start_time = time.time()
        pulse_state.update_progress(
            task_name=self.task_name,
            current_step="Starting...",
            progress=0.0
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            # Report error
            error_msg = f"{exc_type.__name__}: {exc_val}"
            pulse_state.update_progress(
                task_name=self.task_name,
                current_step="Error occurred",
                progress=self.current_step / self.total_steps if self.total_steps > 0 else 0.0,
                error=error_msg
            )
    
    def step(self, description: str, progress: Optional[float] = None):
        """Report completion of a step"""
        if self.closed:
            return
        
        self.current_step += 1
        
        if progress is None:
            progress = self.current_step / self.total_steps if self.total_steps > 0 else 0.0
        
        step_text = self.step_format.format(
            step=self.current_step,
            total=self.total_steps,
            description=description
        )
        
        pulse_state.update_progress(
            task_name=self.task_name,
            current_step=step_text,
            progress=progress
        )
    
    def update_progress(self, progress: float, description: Optional[str] = None):
        """Update current progress within step"""
        if self.closed:
            return
        
        step_text = description or f"Step {self.current_step}/{self.total_steps}"
        
        pulse_state.update_progress(
            task_name=self.task_name,
            current_step=step_text,
            progress=progress
        )
    
    def close(self):
        """Mark task as complete"""
        if not self.closed and self.start_time:
            self.closed = True
            pulse_state.complete_task(self.task_name)

# Convenience functions
def pulse_progress(iterable: Optional[Iterable] = None, 
                   desc: Optional[str] = None,
                   task: Optional[str] = None,
                   step: Optional[str] = None,
                   total: Optional[int] = None,
                   **kwargs) -> PulseProgress:
    """
    Create a PulseProgress instance (like tqdm)
    
    Args:
        iterable: Iterable to wrap
        desc: Description of the task
        task: Alternative to desc (task name)
        step: Step identifier
        total: Total number of items
        **kwargs: Additional arguments for PulseProgress
    
    Returns:
        PulseProgress instance
    """
    return PulseProgress(
        iterable=iterable,
        desc=desc,
        task=task,
        step=step,
        total=total,
        **kwargs
    )

def pulse_task(task_name: str, total_steps: int = 1, **kwargs) -> PulseTask:
    """
    Create a PulseTask instance for multi-step tasks
    
    Args:
        task_name: Name of the task
        total_steps: Total number of steps
        **kwargs: Additional arguments for PulseTask
    
    Returns:
        PulseTask instance
    """
    return PulseTask(task_name=task_name, total_steps=total_steps, **kwargs)

# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Example 1: Simple iterator
    print("Example 1: Simple progress")
    items = range(100)
    for item in pulse_progress(items, task="Processing items", step="1/1"):
        time.sleep(0.01)
    
    # Example 2: Multi-step task
    print("\nExample 2: Multi-step task")
    with pulse_task("Data Analysis", total_steps=4) as task:
        task.step("Loading data", progress=0.2)
        time.sleep(0.5)
        
        task.step("Cleaning data", progress=0.4)
        time.sleep(0.5)
        
        task.step("Analyzing", progress=0.6)
        time.sleep(0.5)
        
        task.step("Generating report", progress=0.8)
        time.sleep(0.5)
        
        task.update_progress(1.0, "Complete")
        time.sleep(0.2)
    
    print("\nExamples completed!")