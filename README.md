# PyPulse

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20PyPulse-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/blackorchardlabs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Beautiful retro-industrial progress monitoring widget for Python scripts.**

> *"Beauty first, utility later."* — Black Orchard Labs

![PyPulse Widget](https://img.shields.io/badge/PyPulse-Retro%20Industrial-D4A017?style=for-the-badge)

## Features

- **Desktop Widget** - Always-on-top progress display with retro-industrial aesthetic
- **Drop-in Replacement** - tqdm-compatible API for easy migration
- **Real-time Updates** - File-based communication for live progress tracking
- **Visual States** - Idle, Active, Complete, and Error states with distinct indicators
- **System Tray** - Minimize to tray, right-click menu, drag to reposition
- **Cross-Platform** - Works on Windows (Linux/Mac support planned)

## Installation

### Requirements

```bash
pip install PyQt6 watchdog psutil
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/BlackOrchardLabs/pypulse.git
cd pypulse
```

2. Launch the widget:
```bash
cd widget
pythonw pypulse_widget.pyw
```

3. Use the library in your scripts:
```python
from pypulse import pulse_progress, pulse_task
```

## Usage

### Simple Progress (tqdm-style)

```python
from pypulse import pulse_progress

# Wrap any iterable
for item in pulse_progress(range(100), desc="Processing"):
    process(item)
```

### Multi-Step Tasks

```python
from pypulse import pulse_task

with pulse_task("Data Pipeline", total_steps=4) as task:
    task.step("Loading data")
    load_data()

    task.step("Cleaning")
    clean_data()

    task.step("Analyzing")
    analyze()

    task.step("Saving results")
    save()
```

### Manual Progress Updates

```python
from pypulse_state import pulse_state

# Direct state updates
pulse_state.update_progress(
    task_name="My Task",
    current_step="Step 1/3: Processing",
    progress=0.33
)

# Mark complete
pulse_state.complete_task("My Task")
```

## Widget Controls

- **Drag** - Click and drag to reposition
- **Right-click** - Context menu (Settings, History, Support, Exit)
- **System Tray** - Double-click to show/hide

## Visual States

| State | Progress Bar | Indicator Light |
|-------|--------------|-----------------|
| Idle | Dim segments | Faint amber |
| Active | Amber segments (animated) | Blinking amber |
| Complete | Full amber | Solid green |
| Error | Red segments | Pulsing red |

## Project Structure

```
pypulse/
├── pypulse.py           # Main library (tqdm-style API)
├── pypulse_state.py     # Shared state management
├── test_pypulse.py      # Library tests
├── widget/
│   ├── pypulse_widget.pyw   # Desktop widget
│   ├── test_widget.py       # Widget test script
│   └── assets/              # Visual assets (PNGs)
└── examples/
    ├── data_processing.py
    ├── machine_learning.py
    └── web_scraping.py
```

## Data Location

PyPulse stores progress data in:
- **Windows**: `%APPDATA%\pypulse\`
- **Linux/Mac**: `~/.pypulse/`

## Support

If you find PyPulse useful, consider supporting development:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/blackorchardlabs)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Black Orchard Labs** - *Building beautiful tools for developers*
