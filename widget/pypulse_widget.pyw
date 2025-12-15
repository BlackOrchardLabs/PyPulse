#!/usr/bin/env python3
"""
PyPulse Widget - Retro Industrial Desktop Artifact
A beautiful, always-on-top progress monitoring widget for Python scripts.

Design Philosophy: "Beauty first, utility later."
This widget should feel like a physical artifact salvaged from an abandoned research bunker.

Author: Black Orchard Labs
Date: December 15, 2025
"""

import sys
import json
import os
import time
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

try:
    from PyQt6.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QMenu,
                                  QLabel, QVBoxLayout, QHBoxLayout)
    from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QPropertyAnimation, QRect, QRectF, pyqtProperty, QObject
    from PyQt6.QtGui import (QPainter, QBrush, QPen, QColor, QFont, QPixmap, QIcon,
                              QLinearGradient, QRadialGradient, QPainterPath, QRegion)
except ImportError:
    print("PyQt6 not found. Please install with: pip install PyQt6")
    sys.exit(1)

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("watchdog not found. Please install with: pip install watchdog")
    sys.exit(1)


class FileWatcher(FileSystemEventHandler):
    """Monitors progress.json for changes"""
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.src_path.endswith('progress.json'):
            # Debounce rapid file changes
            current_time = time.time()
            if current_time - self.last_modified > 0.1:
                self.last_modified = current_time
                self.callback()


def get_pulse_dir():
    """Get the PyPulse data directory (cross-platform)"""
    if os.name == 'nt':  # Windows
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:  # Linux/Mac
        base = os.path.expanduser('~')
    pulse_dir = Path(base) / 'pypulse'
    pulse_dir.mkdir(parents=True, exist_ok=True)
    return pulse_dir


class PulseWidget(QWidget):
    """Retro Industrial PyPulse Widget"""

    def __init__(self):
        super().__init__()
        self.pulse_dir = get_pulse_dir()
        self.progress_file = self.pulse_dir / "progress.json"
        self.position_file = self.pulse_dir / "widget_position.json"
        
        # Widget state
        self.current_state = "idle"
        self.progress_value = 0.0
        self.task_name = ""
        self.current_step = ""
        self.is_dragging = False
        self.drag_position = QPoint()
        self.blink_state = True
        self.animation_timer = None
        
        # Visual elements
        self.background_pixmap = None
        self.segment_on_pixmap = None
        self.segment_off_pixmap = None
        self.light_bezel_pixmap = None
        
        self.init_ui()
        self.load_assets()
        self.setup_file_watcher()
        self.load_position()
        self.update_from_file()
        
    def init_ui(self):
        """Initialize the widget UI with retro-industrial styling"""
        # Window properties
        self.setFixedSize(260, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set window title and icon
        self.setWindowTitle("PyPulse")

        # Start blink animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_blink)
        self.animation_timer.start(1000)  # 1 second interval
        
    def load_assets(self):
        """Load texture assets"""
        assets_dir = Path(__file__).parent / "assets"
        
        # Load background textures
        yellow_path = assets_dir / "body_yellow.png"
        if yellow_path.exists():
            self.background_pixmap = QPixmap(str(yellow_path))
        
        # Load segment images
        segment_on_path = assets_dir / "segment_on.png"
        if segment_on_path.exists():
            self.segment_on_pixmap = QPixmap(str(segment_on_path))
            
        segment_off_path = assets_dir / "segment_off.png"
        if segment_off_path.exists():
            self.segment_off_pixmap = QPixmap(str(segment_off_path))
            
        # Load light bezel
        light_bezel_path = assets_dir / "light_bezel.png"
        if light_bezel_path.exists():
            self.light_bezel_pixmap = QPixmap(str(light_bezel_path))
    
    def setup_file_watcher(self):
        """Set up file system monitoring"""
        if not self.pulse_dir.exists():
            self.pulse_dir.mkdir(parents=True, exist_ok=True)
            
        self.observer = Observer()
        self.file_watcher = FileWatcher(self.update_from_file)
        self.observer.schedule(self.file_watcher, str(self.pulse_dir), recursive=False)
        self.observer.start()
        
    def update_from_file(self):
        """Read progress data from JSON file"""
        try:
            if not self.progress_file.exists():
                # No file = idle state
                self.current_state = "idle"
                self.progress_value = 0.0
                self.task_name = ""
                self.current_step = ""
                self.update()
                return

            with open(self.progress_file, 'r') as f:
                data = json.load(f)

            # Update state
            self.progress_value = data.get('progress', 0.0)
            self.task_name = data.get('task_name', '')
            self.current_step = data.get('current_step', '')

            # Determine visual state - error must be a non-empty string
            error_value = data.get('error')
            if error_value and isinstance(error_value, str) and error_value.strip():
                self.current_state = "error"
            elif data.get('active', False):
                self.current_state = "active"
            elif self.progress_value >= 1.0:
                self.current_state = "complete"
            else:
                self.current_state = "idle"

            self.update()
        except Exception as e:
            # On error reading file, default to idle
            self.current_state = "idle"
            self.progress_value = 0.0
            self.update()
            print(f"Error reading progress file: {e}")
    
    def paintEvent(self, event):
        """Custom painting for retro-industrial look"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        self.draw_background(painter)
        
        # Draw embossed "PYPULSE" text
        self.draw_title(painter)
        
        # Draw manufacturer plate
        self.draw_manufacturer_plate(painter)
        
        # Draw progress bar
        self.draw_progress_bar(painter)
        
        # Draw activity indicator light
        self.draw_indicator_light(painter)
        
        # Draw rivets at corners
        self.draw_rivets(painter)
    
    def draw_background(self, painter):
        """Draw weathered metal background"""
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 8, 8)
        
        if self.background_pixmap and not self.background_pixmap.isNull():
            # Use texture pixmap
            painter.setClipPath(path)
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            # Fallback: draw gradient background
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(212, 160, 23))  # #D4A017
            gradient.setColorAt(0.5, QColor(180, 136, 20))
            gradient.setColorAt(1, QColor(150, 113, 16))
            
            painter.fillPath(path, QBrush(gradient))
            
            # Add some wear effects
            painter.setPen(QPen(QColor(100, 75, 10), 1))
            for i in range(5):
                x = 10 + i * 40
                painter.drawLine(x, 10, x + 20, 30)
    
    def draw_title(self, painter):
        """Draw embossed "PYPULSE" title"""
        font = QFont("Arial Black", 14, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        
        # Calculate position
        rect = QRect(10, 8, self.width() - 20, 25)
        
        # Draw shadow (embossed effect)
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
        painter.drawText(rect.translated(1, 1), Qt.AlignmentFlag.AlignCenter, "PYPULSE")
        
        # Draw highlight
        painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
        painter.drawText(rect.translated(-1, -1), Qt.AlignmentFlag.AlignCenter, "PYPULSE")
        
        # Draw main text
        gradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        gradient.setColorAt(0, QColor(50, 50, 50))
        gradient.setColorAt(1, QColor(100, 100, 100))
        painter.setPen(QPen(QBrush(gradient), 2))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "PYPULSE")
    
    def draw_manufacturer_plate(self, painter):
        """Draw small manufacturer plate"""
        # Main plate with company name
        font = QFont("Arial", 6)
        painter.setFont(font)

        plate_rect = QRect(self.width() - 100, self.height() - 15, 95, 12)

        # Draw plate background
        painter.fillRect(plate_rect, QBrush(QColor(40, 40, 40, 200)))

        # Draw border
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawRect(plate_rect)

        # Draw text
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawText(plate_rect, Qt.AlignmentFlag.AlignCenter, "BLACK ORCHARD LABS")

        # Draw model number above the plate
        model_font = QFont("Arial", 6)
        painter.setFont(model_font)
        model_rect = QRect(self.width() - 100, self.height() - 26, 40, 10)
        painter.drawText(model_rect, Qt.AlignmentFlag.AlignLeft, "MOD-001")
    
    def draw_progress_bar(self, painter):
        """Draw segmented LED progress bar"""
        # Progress bar area
        bar_x = 20
        bar_y = 45
        bar_width = 220
        bar_height = 20
        
        # Draw recessed bezel
        bezel_rect = QRect(bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8)
        painter.fillRect(bezel_rect, QBrush(QColor(20, 20, 20, 200)))
        
        # Draw bezel border
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRect(bezel_rect)
        
        # Draw segments
        num_segments = 16
        segment_width = bar_width // num_segments
        
        for i in range(num_segments):
            segment_x = bar_x + i * segment_width
            segment_progress = (i + 1) / num_segments
            
            # Determine if segment should be lit
            is_lit = segment_progress <= self.progress_value

            if is_lit:
                if self.current_state == "error":
                    # Lit segment in error state (red)
                    color = QColor(255, 50, 50)
                    glow_color = QColor(255, 50, 50, 100)
                else:
                    # Lit segment (amber)
                    color = QColor(255, 149, 0)  # #FF9500
                    glow_color = QColor(255, 149, 0, 100)
            else:
                # Unlit segment (dim)
                color = QColor(50, 40, 30)
                glow_color = QColor(0, 0, 0, 0)
            
            # Draw segment with glow effect
            segment_rect = QRect(segment_x + 1, bar_y + 1, segment_width - 2, bar_height - 2)
            
            # Draw glow
            if glow_color.alpha() > 0:
                glow_rect = segment_rect.adjusted(-2, -2, 2, 2)
                painter.fillRect(glow_rect, QBrush(glow_color))
            
            # Draw segment
            painter.fillRect(segment_rect, QBrush(color))
            
            # Add subtle border
            painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
            painter.drawRect(segment_rect)
    
    def draw_indicator_light(self, painter):
        """Draw activity indicator light"""
        light_x = self.width() - 30
        light_y = 15
        light_size = 12
        
        # Draw bezel
        if self.light_bezel_pixmap and not self.light_bezel_pixmap.isNull():
            bezel_pixmap = self.light_bezel_pixmap.scaled(
                light_size + 4, light_size + 4,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(light_x - 2, light_y - 2, bezel_pixmap)
        else:
            # Fallback bezel
            bezel_rect = QRect(light_x - 2, light_y - 2, light_size + 4, light_size + 4)
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawEllipse(bezel_rect)
        
        # Determine light color based on state
        if self.current_state == "idle":
            color = QColor(255, 200, 100, 50)  # Very dim amber
        elif self.current_state == "active":
            # Blinking amber (bright/dim cycle)
            if self.blink_state:
                color = QColor(255, 149, 0)  # Bright amber
            else:
                color = QColor(255, 149, 0, 100)  # Dim amber
        elif self.current_state == "complete":
            color = QColor(0, 255, 100)  # Solid green
        else:  # error
            # Pulsing red (bright/dim cycle)
            if self.blink_state:
                color = QColor(255, 50, 50)  # Bright red
            else:
                color = QColor(255, 50, 50, 150)  # Dim red
        
        # Draw light
        light_rect = QRect(light_x, light_y, light_size, light_size)
        
        # Add glow effect
        if color.alpha() == 255:  # Fully opaque means active
            glow_rect = light_rect.adjusted(-3, -3, 3, 3)
            glow_color = QColor(color.red(), color.green(), color.blue(), 100)
            painter.fillRect(glow_rect, QBrush(glow_color))
        
        painter.fillRect(light_rect, QBrush(color))
    
    def draw_rivets(self, painter):
        """Draw rivets at corners"""
        rivet_size = 4
        rivet_color = QColor(80, 80, 80)
        
        # Define corner positions
        corners = [
            (5, 5),  # Top-left
            (self.width() - 9, 5),  # Top-right
            (5, self.height() - 9),  # Bottom-left
            (self.width() - 9, self.height() - 9)  # Bottom-right
        ]
        
        for x, y in corners:
            # Draw rivet shadow
            painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
            painter.drawEllipse(x + 1, y + 1, rivet_size, rivet_size)
            
            # Draw rivet
            painter.setPen(QPen(rivet_color, 1))
            painter.setBrush(QBrush(rivet_color))
            painter.drawEllipse(x, y, rivet_size, rivet_size)
            
            # Add highlight
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
            painter.drawEllipse(x - 1, y - 1, rivet_size - 1, rivet_size - 1)
    
    def animate_blink(self):
        """Animate blinking for active state"""
        if self.current_state == "active":
            self.blink_state = not self.blink_state
            self.update()
        elif self.current_state == "error":
            # Rapid pulse for error state
            self.blink_state = not self.blink_state
            self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.save_position()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.is_dragging = False
    
    def contextMenuEvent(self, event):
        """Show context menu on right click"""
        menu = QMenu()

        # Add menu actions
        settings_action = menu.addAction("Settings")
        history_action = menu.addAction("History")
        menu.addSeparator()
        support_action = menu.addAction("Support PyPulse ☕")
        menu.addSeparator()
        exit_action = menu.addAction("Exit")

        # Handle menu actions
        action = menu.exec(event.globalPos())

        if action == exit_action:
            self.close()
        elif action == settings_action:
            # TODO: Implement settings dialog
            print("Settings not implemented yet")
        elif action == history_action:
            # TODO: Implement history viewer
            print("History not implemented yet")
        elif action == support_action:
            webbrowser.open("https://ko-fi.com/blackorchardlabs")
    
    def save_position(self):
        """Save widget position to file"""
        try:
            position_data = {
                'x': self.x(),
                'y': self.y(),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.position_file, 'w') as f:
                json.dump(position_data, f, indent=2)
        except Exception as e:
            print(f"Error saving position: {e}")
    
    def load_position(self):
        """Load and restore widget position"""
        try:
            if self.position_file.exists():
                with open(self.position_file, 'r') as f:
                    data = json.load(f)
                    
                x = data.get('x', 100)
                y = data.get('y', 100)
                self.move(x, y)
            else:
                # Default position: bottom-right corner
                screen = QApplication.primaryScreen()
                screen_rect = screen.availableGeometry()
                x = screen_rect.width() - self.width() - 20
                y = screen_rect.height() - self.height() - 20
                self.move(x, y)
        except Exception as e:
            print(f"Error loading position: {e}")
    
    def closeEvent(self, event):
        """Clean up when closing"""
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        event.accept()


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for PyPulse"""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

        # Create a simple programmatic icon (amber circle)
        icon_pixmap = QPixmap(32, 32)
        icon_pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        painter = QPainter(icon_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 149, 0)))  # Amber color
        painter.setPen(QPen(QColor(200, 100, 0), 2))
        painter.drawEllipse(2, 2, 28, 28)
        painter.end()
        self.setIcon(QIcon(icon_pixmap))
        
        # Create tray menu
        self.menu = QMenu()
        self.show_action = self.menu.addAction("Show PyPulse")
        self.hide_action = self.menu.addAction("Hide PyPulse")
        self.menu.addSeparator()
        self.support_action = self.menu.addAction("Support PyPulse ☕")
        self.menu.addSeparator()
        self.exit_action = self.menu.addAction("Exit")

        self.setContextMenu(self.menu)

        # Connect actions
        self.show_action.triggered.connect(self.widget.show)
        self.hide_action.triggered.connect(self.widget.hide)
        self.support_action.triggered.connect(lambda: webbrowser.open("https://ko-fi.com/blackorchardlabs"))
        self.exit_action.triggered.connect(QApplication.instance().quit)
        
        # Handle tray icon activation
        self.activated.connect(self.tray_activated)
        
    def tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.widget.isVisible():
                self.widget.hide()
            else:
                self.widget.show()


def ensure_single_instance():
    """Ensure only one instance of the widget is running"""
    # Simple file-based locking
    lock_file = get_pulse_dir() / "widget.lock"
    
    try:
        if lock_file.exists():
            # Check if process is still running
            with open(lock_file, 'r') as f:
                pid = f.read().strip()
                
            # Try to check if process exists (Windows-specific)
            import psutil
            if psutil.pid_exists(int(pid)):
                print("PyPulse widget is already running")
                sys.exit(0)
    except Exception:
        pass
    
    # Create lock file
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
    
    # Clean up lock file on exit
    import atexit
    atexit.register(lambda: lock_file.unlink(missing_ok=True))


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Ensure single instance
    ensure_single_instance()
    
    # Create and show widget
    widget = PulseWidget()
    widget.show()
    
    # Create system tray icon
    tray_icon = SystemTrayIcon(widget)
    tray_icon.show()
    
    # Set up application quit handling
    def quit_app():
        widget.close()
        app.quit()
    
    app.aboutToQuit.connect(quit_app)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()