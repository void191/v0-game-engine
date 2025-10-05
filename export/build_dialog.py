"""
Build export dialog UI
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QSpinBox, QFileDialog,
    QGroupBox, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path
import logging

from .build_config import BuildConfig, BuildPlatform, BuildMode
from .exporter import GameExporter

logger = logging.getLogger(__name__)


class ExportThread(QThread):
    """Background thread for export process"""
    
    progress = Signal(str)
    finished = Signal(Path)
    error = Signal(str)
    
    def __init__(self, config: BuildConfig):
        super().__init__()
        self.config = config
    
    def run(self):
        """Run export"""
        try:
            self.progress.emit("Starting export...")
            exporter = GameExporter(self.config)
            output_path = exporter.export()
            self.finished.emit(output_path)
        except Exception as e:
            logger.error(f"Export failed: {e}")
            self.error.emit(str(e))


class BuildDialog(QDialog):
    """Build export configuration dialog"""
    
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.export_thread = None
        
        self.setWindowTitle("Export Build")
        self.setModal(True)
        self.resize(600, 700)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Project settings
        project_group = QGroupBox("Project Settings")
        project_layout = QVBoxLayout()
        project_group.setLayout(project_layout)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit("MyGame")
        name_layout.addWidget(self.name_edit)
        project_layout.addLayout(name_layout)
        
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        self.version_edit = QLineEdit("1.0.0")
        version_layout.addWidget(self.version_edit)
        project_layout.addLayout(version_layout)
        
        layout.addWidget(project_group)
        
        # Build settings
        build_group = QGroupBox("Build Settings")
        build_layout = QVBoxLayout()
        build_group.setLayout(build_layout)
        
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel("Platform:"))
        self.platform_combo = QComboBox()
        for platform in BuildPlatform:
            self.platform_combo.addItem(platform.value.capitalize(), platform)
        platform_layout.addWidget(self.platform_combo)
        build_layout.addLayout(platform_layout)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        for mode in BuildMode:
            self.mode_combo.addItem(mode.value.capitalize(), mode)
        mode_layout.addWidget(self.mode_combo)
        build_layout.addLayout(mode_layout)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Path:"))
        self.output_edit = QLineEdit("./builds")
        output_layout.addWidget(self.output_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(browse_btn)
        build_layout.addLayout(output_layout)
        
        layout.addWidget(build_group)
        
        # Window settings
        window_group = QGroupBox("Window Settings")
        window_layout = QVBoxLayout()
        window_group.setLayout(window_layout)
        
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(640, 3840)
        self.width_spin.setValue(1280)
        resolution_layout.addWidget(self.width_spin)
        resolution_layout.addWidget(QLabel("x"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(480, 2160)
        self.height_spin.setValue(720)
        resolution_layout.addWidget(self.height_spin)
        window_layout.addLayout(resolution_layout)
        
        self.fullscreen_check = QCheckBox("Fullscreen")
        window_layout.addWidget(self.fullscreen_check)
        
        self.resizable_check = QCheckBox("Resizable")
        self.resizable_check.setChecked(True)
        window_layout.addWidget(self.resizable_check)
        
        layout.addWidget(window_group)
        
        # Optimization settings
        opt_group = QGroupBox("Optimization")
        opt_layout = QVBoxLayout()
        opt_group.setLayout(opt_layout)
        
        self.compress_textures_check = QCheckBox("Compress Textures")
        self.compress_textures_check.setChecked(True)
        opt_layout.addWidget(self.compress_textures_check)
        
        self.compress_audio_check = QCheckBox("Compress Audio")
        self.compress_audio_check.setChecked(True)
        opt_layout.addWidget(self.compress_audio_check)
        
        self.optimize_meshes_check = QCheckBox("Optimize Meshes")
        self.optimize_meshes_check.setChecked(True)
        opt_layout.addWidget(self.optimize_meshes_check)
        
        self.strip_debug_check = QCheckBox("Strip Debug Symbols")
        self.strip_debug_check.setChecked(True)
        opt_layout.addWidget(self.strip_debug_check)
        
        layout.addWidget(opt_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._on_export)
        button_layout.addWidget(export_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _browse_output(self):
        """Browse for output directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_edit.setText(path)
    
    def _on_export(self):
        """Start export process"""
        # Create config
        config = BuildConfig(
            project_name=self.name_edit.text(),
            project_path=self.engine.config.project_path,
            version=self.version_edit.text(),
            platform=self.platform_combo.currentData(),
            mode=self.mode_combo.currentData(),
            output_path=Path(self.output_edit.text()),
            window_width=self.width_spin.value(),
            window_height=self.height_spin.value(),
            fullscreen=self.fullscreen_check.isChecked(),
            resizable=self.resizable_check.isChecked(),
            compress_textures=self.compress_textures_check.isChecked(),
            compress_audio=self.compress_audio_check.isChecked(),
            optimize_meshes=self.optimize_meshes_check.isChecked(),
            strip_debug_symbols=self.strip_debug_check.isChecked()
        )
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.log_text.setVisible(True)
        
        # Start export thread
        self.export_thread = ExportThread(config)
        self.export_thread.progress.connect(self._on_progress)
        self.export_thread.finished.connect(self._on_finished)
        self.export_thread.error.connect(self._on_error)
        self.export_thread.start()
    
    def _on_progress(self, message: str):
        """Handle progress update"""
        self.log_text.append(message)
    
    def _on_finished(self, output_path: Path):
        """Handle export completion"""
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.log_text.append(f"\nExport complete: {output_path}")
        logger.info(f"Export complete: {output_path}")
    
    def _on_error(self, error: str):
        """Handle export error"""
        self.progress_bar.setVisible(False)
        self.log_text.append(f"\nError: {error}")
        logger.error(f"Export error: {error}")
