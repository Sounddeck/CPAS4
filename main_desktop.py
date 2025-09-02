#!/usr/bin/env python3

"""
CPAS4 Main Desktop Application
This is the main entry point for the CPAS4 desktop application.
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PyQt6.QtCore import Qt
except ImportError:
    print("Error: PyQt6 is not installed. Please run: pip install PyQt6")
    sys.exit(1)

def setup_logging():
    """Set up logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "cpas4.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file"""
    try:
        import yaml
        config_path = Path("config.yaml")
        if not config_path.exists():
            config_path = Path("config.example.yaml")
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("Error: PyYAML is not installed. Please run: pip install pyyaml")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

class CPAS4MainWindow(QMainWindow):
    """Main window for CPAS4 application"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CPAS4 - Cognitive Personal Assistant System")
        self.setGeometry(100, 100, 
                        self.config.get('ui', {}).get('window_width', 1200),
                        self.config.get('ui', {}).get('window_height', 800))
        
        # Create a central widget with a welcome message
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        welcome_label = QLabel("Welcome to CPAS4!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        
        status_label = QLabel("System is initializing...")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(welcome_label)
        layout.addWidget(status_label)
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)
        
    def show_error(self, message):
        """Show an error message to the user"""
        QMessageBox.critical(self, "Error", message)

def main():
    """Main entry point for the application"""
    logger = setup_logging()
    logger.info("Starting CPAS4 application")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = CPAS4MainWindow(config)
        window.show()
        
        logger.info("Application started successfully")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
