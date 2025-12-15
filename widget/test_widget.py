#!/usr/bin/env python3
"""
Simple test script for PyPulse widget
Tests the visual appearance and basic functionality
"""

import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime


def get_pulse_dir():
    """Get the PyPulse data directory (cross-platform)"""
    if os.name == 'nt':  # Windows
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:  # Linux/Mac
        base = os.path.expanduser('~')
    pulse_dir = Path(base) / 'pypulse'
    pulse_dir.mkdir(parents=True, exist_ok=True)
    return pulse_dir


def write_progress(progress_file, active, progress, step, error=None):
    """Write a progress state to the file"""
    data = {
        "active": active,
        "task_name": "Data Processing Pipeline",
        "current_step": step,
        "progress": progress,
        "eta_seconds": int((1.0 - progress) * 100) if active else 0,
        "started_at": datetime.now().isoformat(),
        "last_update": datetime.now().isoformat(),
        "error": error,
        "pid": 12345
    }
    with open(progress_file, 'w') as f:
        json.dump(data, f, indent=2)


def reset_to_idle(progress_file):
    """Reset progress file to idle state"""
    data = {
        "active": False,
        "task_name": "",
        "current_step": "",
        "progress": 0.0,
        "eta_seconds": 0,
        "started_at": None,
        "last_update": None,
        "error": None,
        "pid": None
    }
    with open(progress_file, 'w') as f:
        json.dump(data, f, indent=2)


def run_test():
    """Run the widget test"""
    pulse_dir = get_pulse_dir()
    progress_file = pulse_dir / "progress.json"

    print("Phase 1: Smooth progress fill (0% to 100%)")
    print("-" * 40)

    # Smooth progress from 0 to 100% in 16 steps (one per segment)
    for i in range(17):
        progress = i / 16.0
        step = f"Processing... {int(progress * 100)}%"
        write_progress(progress_file, True, progress, step)
        print(f"  Progress: {int(progress * 100):3d}% - Segments: {i}/16")
        time.sleep(0.5)

    print("\nPhase 2: Complete state (green light)")
    print("-" * 40)
    write_progress(progress_file, False, 1.0, "Complete!")
    print("  Showing complete state for 3 seconds...")
    time.sleep(3)

    print("\nPhase 3: Error state (red segments)")
    print("-" * 40)
    write_progress(progress_file, False, 0.5, "Error occurred", "RuntimeError: Something went wrong")
    print("  Showing error state for 3 seconds...")
    time.sleep(3)

    print("\nPhase 4: Reset to idle")
    print("-" * 40)
    reset_to_idle(progress_file)
    print("  Widget reset to idle state")

    print("\n" + "=" * 40)
    print("Test complete! Widget should be back to idle.")


def main():
    print("PyPulse Widget Test")
    print("=" * 40)
    print()
    print("This test will:")
    print("  1. Fill progress bar segment by segment (0-100%)")
    print("  2. Show complete state (green)")
    print("  3. Show error state (red)")
    print("  4. Reset to idle state")
    print()
    print("Make sure the widget is running before starting!")
    print()

    input("Press Enter to start test...")
    print()

    try:
        run_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted - resetting to idle...")
        pulse_dir = get_pulse_dir()
        reset_to_idle(pulse_dir / "progress.json")
        print("Done.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during test: {e}")
        print("Resetting to idle...")
        pulse_dir = get_pulse_dir()
        reset_to_idle(pulse_dir / "progress.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
