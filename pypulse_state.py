"""
PyPulse Shared State Management
Handles all communication between widget and progress wrapper
"""

import json
import os
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_pulse_dir():
    """Get the PyPulse data directory (cross-platform)"""
    if os.name == 'nt':  # Windows
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:  # Linux/Mac
        base = os.path.expanduser('~')
    pulse_dir = Path(base) / 'pypulse'
    pulse_dir.mkdir(parents=True, exist_ok=True)
    return pulse_dir


# Constants
PULSE_DIR = get_pulse_dir()
PROGRESS_FILE = PULSE_DIR / "progress.json"
HISTORY_FILE = PULSE_DIR / "history.json"
WIDGET_POSITION_FILE = PULSE_DIR / "widget_position.json"

class PulseState:
    """Manages shared state between widget and progress wrapper"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Initialize state files if they don't exist"""
        if not PROGRESS_FILE.exists():
            self._write_safe(PROGRESS_FILE, {
                "active": False,
                "task_name": None,
                "current_step": None,
                "progress": 0.0,
                "eta_seconds": None,
                "started_at": None,
                "last_update": None,
                "error": None,
                "pid": None
            })
        
        if not HISTORY_FILE.exists():
            self._write_safe(HISTORY_FILE, {"completed_tasks": []})
        
        if not WIDGET_POSITION_FILE.exists():
            self._write_safe(WIDGET_POSITION_FILE, {"x": 100, "y": 100})
    
    def _read_safe(self, filepath: Path) -> Dict[str, Any]:
        """Thread-safe file reading"""
        with self._lock:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading {filepath}: {e}")
                return {}
    
    def _write_safe(self, filepath: Path, data: Dict[str, Any]):
        """Thread-safe file writing"""
        with self._lock:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except IOError as e:
                logger.error(f"Error writing {filepath}: {e}")
    
    def update_progress(self, 
                       task_name: str,
                       current_step: str,
                       progress: float,
                       eta_seconds: Optional[int] = None,
                       error: Optional[str] = None,
                       pid: Optional[int] = None):
        """Update current progress state"""
        now = datetime.now(timezone.utc).isoformat()
        
        state = {
            "active": True,
            "task_name": task_name,
            "current_step": current_step,
            "progress": max(0.0, min(1.0, progress)),  # Clamp to 0-1
            "eta_seconds": eta_seconds,
            "started_at": self._get_started_at() or now,
            "last_update": now,
            "error": error,
            "pid": pid or os.getpid()
        }
        
        self._write_safe(PROGRESS_FILE, state)
    
    def complete_task(self, task_name: str):
        """Mark current task as complete and move to history"""
        with self._lock:
            # Get current state before clearing
            current_state = self._read_safe(PROGRESS_FILE)
            
            # Add to history
            history = self._read_safe(HISTORY_FILE)
            completed_task = {
                "task_name": task_name,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": self._calculate_duration()
            }
            
            history["completed_tasks"].insert(0, completed_task)
            history["completed_tasks"] = history["completed_tasks"][:10]  # Keep last 10
            
            self._write_safe(HISTORY_FILE, history)
            
            # Clear current progress
            self._write_safe(PROGRESS_FILE, {
                "active": False,
                "task_name": None,
                "current_step": None,
                "progress": 0.0,
                "eta_seconds": None,
                "started_at": None,
                "last_update": None,
                "error": None,
                "pid": None
            })
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress state"""
        return self._read_safe(PROGRESS_FILE)
    
    def get_history(self) -> Dict[str, Any]:
        """Get completed tasks history"""
        return self._read_safe(HISTORY_FILE)
    
    def save_widget_position(self, x: int, y: int):
        """Save widget window position"""
        self._write_safe(WIDGET_POSITION_FILE, {"x": x, "y": y})
    
    def get_widget_position(self) -> Dict[str, int]:
        """Get saved widget window position"""
        pos = self._read_safe(WIDGET_POSITION_FILE)
        return {"x": pos.get("x", 100), "y": pos.get("y", 100)}
    
    def _get_started_at(self) -> Optional[str]:
        """Get started_at from current state if exists"""
        current = self._read_safe(PROGRESS_FILE)
        return current.get("started_at")
    
    def _calculate_duration(self) -> Optional[int]:
        """Calculate duration in seconds for completed task"""
        current = self._read_safe(PROGRESS_FILE)
        started = current.get("started_at")
        if started:
            start_time = datetime.fromisoformat(started)
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            return int(duration)
        return None

# Global state instance
pulse_state = PulseState()

def clear_stale_progress(max_idle_seconds: int = 300):
    """Clear progress if no update for specified seconds"""
    try:
        state = pulse_state.get_progress()
        if state.get("active") and state.get("last_update"):
            last_update = datetime.fromisoformat(state["last_update"])
            idle_time = (datetime.now(timezone.utc) - last_update).total_seconds()
            
            if idle_time > max_idle_seconds:
                # Mark as inactive but preserve error state
                pulse_state._write_safe(PROGRESS_FILE, {
                    "active": False,
                    "task_name": state.get("task_name"),
                    "current_step": state.get("current_step"),
                    "progress": state.get("progress", 0.0),
                    "eta_seconds": None,
                    "started_at": None,
                    "last_update": None,
                    "error": state.get("error"),
                    "pid": None
                })
    except Exception as e:
        logger.error(f"Error clearing stale progress: {e}")

# Auto-clear stale progress every 60 seconds
def _cleanup_worker():
    while True:
        time.sleep(60)
        clear_stale_progress()

# Start cleanup thread
cleanup_thread = threading.Thread(target=_cleanup_worker, daemon=True)
cleanup_thread.start()