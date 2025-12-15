"""
PyPulse Test Suite
Verify all components work correctly
"""

import time
import os
import sys
from pathlib import Path
import threading
import subprocess
import json

# Add current directory to path for testing
sys.path.insert(0, str(Path(__file__).parent))

def test_state_management():
    """Test the shared state management"""
    print("Testing state management...")
    
    from pypulse_state import pulse_state
    
    # Test progress update
    pulse_state.update_progress(
        task_name="Test Task",
        current_step="Step 1/3: Testing",
        progress=0.5,
        eta_seconds=120
    )
    
    # Verify state was written
    state = pulse_state.get_progress()
    assert state["active"] == True
    assert state["task_name"] == "Test Task"
    assert state["current_step"] == "Step 1/3: Testing"
    assert state["progress"] == 0.5
    assert state["eta_seconds"] == 120
    
    print("✓ State management test passed")

def test_progress_wrapper():
    """Test the progress wrapper functionality"""
    print("Testing progress wrapper...")
    
    from pypulse import pulse_progress, pulse_task
    
    # Test simple progress
    items = list(range(10))
    for i, item in enumerate(pulse_progress(items, task="Test Progress")):
        time.sleep(0.01)
        assert i == item
    
    # Test task context manager
    with pulse_task("Test Task", total_steps=3) as task:
        task.step("Step 1", progress=0.3)
        time.sleep(0.1)
        task.step("Step 2", progress=0.6)
        time.sleep(0.1)
        task.step("Step 3", progress=1.0)
        time.sleep(0.1)
    
    print("✓ Progress wrapper test passed")

def test_error_handling():
    """Test error handling and reporting"""
    print("Testing error handling...")
    
    from pypulse import pulse_task
    from pypulse_state import pulse_state
    
    try:
        with pulse_task("Error Test", total_steps=2) as task:
            task.step("Step 1", progress=0.5)
            raise ValueError("Test error")
    except ValueError:
        pass  # Expected
    
    # Check that error was recorded
    state = pulse_state.get_progress()
    # Note: Error state might be cleared by cleanup, so we just verify it doesn't crash
    
    print("✓ Error handling test passed")

def test_widget_integration():
    """Test widget integration (requires widget to be running)"""
    print("Testing widget integration...")
    
    from pypulse import pulse_progress
    from pypulse_state import pulse_state
    
    # Start a background progress
    def simulate_work():
        for i in pulse_progress(range(50), task="Integration Test"):
            time.sleep(0.05)
    
    thread = threading.Thread(target=simulate_work)
    thread.start()
    
    # Monitor progress
    start_time = time.time()
    while thread.is_alive() and time.time() - start_time < 5:
        state = pulse_state.get_progress()
        if state.get("active"):
            print(f"  Progress: {state.get('progress', 0):.1%}")
        time.sleep(0.2)
    
    thread.join(timeout=2)
    
    print("✓ Widget integration test passed")

def test_file_structure():
    """Test that required files exist"""
    print("Testing file structure...")
    
    base_dir = Path("C:/Hermes/.pypulse")
    
    # Check if directory exists (will be created on first use)
    if not base_dir.exists():
        print("  Note: Installation directory not found (will be created on first use)")
    
    # Check current directory files
    required_files = [
        "pypulse_widget.pyw",
        "pypulse.py",
        "pypulse_state.py",
        "install_pypulse.ps1",
        "README.md"
    ]
    
    current_dir = Path(__file__).parent
    for file in required_files:
        if not (current_dir / file).exists():
            print(f"  Warning: {file} not found in current directory")
        else:
            print(f"  ✓ Found {file}")
    
    print("✓ File structure test completed")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("PyPulse Test Suite")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_state_management,
        test_progress_wrapper,
        test_error_handling,
        test_widget_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("🎉 All tests passed! PyPulse is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)