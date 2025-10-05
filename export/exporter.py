"""
Game build exporter
"""

import shutil
import json
import logging
from pathlib import Path
from typing import List
import zipfile

from .build_config import BuildConfig, BuildPlatform, BuildMode

logger = logging.getLogger(__name__)


class GameExporter:
    """Export game builds for different platforms"""
    
    def __init__(self, config: BuildConfig):
        self.config = config
    
    def export(self) -> Path:
        """Export game build"""
        logger.info(f"Starting export for {self.config.platform.value}...")
        
        # Create output directory
        build_dir = self._create_build_directory()
        
        # Copy runtime files
        self._copy_runtime_files(build_dir)
        
        # Copy project assets
        self._copy_project_assets(build_dir)
        
        # Copy scenes
        self._copy_scenes(build_dir)
        
        # Generate build manifest
        self._generate_manifest(build_dir)
        
        # Platform-specific packaging
        if self.config.platform == BuildPlatform.WINDOWS:
            final_path = self._package_windows(build_dir)
        elif self.config.platform == BuildPlatform.LINUX:
            final_path = self._package_linux(build_dir)
        elif self.config.platform == BuildPlatform.MACOS:
            final_path = self._package_macos(build_dir)
        elif self.config.platform == BuildPlatform.WEB:
            final_path = self._package_web(build_dir)
        else:
            final_path = build_dir
        
        logger.info(f"Export complete: {final_path}")
        return final_path
    
    def _create_build_directory(self) -> Path:
        """Create build output directory"""
        build_name = f"{self.config.project_name}_{self.config.platform.value}_{self.config.version}"
        build_dir = self.config.output_path / build_name
        
        # Clean existing build
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        build_dir.mkdir(parents=True, exist_ok=True)
        
        return build_dir
    
    def _copy_runtime_files(self, build_dir: Path):
        """Copy runtime player files"""
        logger.info("Copying runtime files...")
        
        runtime_dir = Path(__file__).parent.parent / "runtime"
        dest_runtime = build_dir / "runtime"
        
        if runtime_dir.exists():
            shutil.copytree(runtime_dir, dest_runtime)
        
        # Copy core engine files
        core_dir = Path(__file__).parent.parent / "core"
        dest_core = build_dir / "core"
        
        if core_dir.exists():
            shutil.copytree(core_dir, dest_core)
    
    def _copy_project_assets(self, build_dir: Path):
        """Copy project assets"""
        logger.info("Copying project assets...")
        
        assets_dir = self.config.project_path / "assets"
        dest_assets = build_dir / "assets"
        
        if assets_dir.exists():
            shutil.copytree(assets_dir, dest_assets)
            
            # Optimize assets if enabled
            if self.config.compress_textures:
                self._compress_textures(dest_assets)
            
            if self.config.compress_audio:
                self._compress_audio(dest_assets)
            
            if self.config.optimize_meshes:
                self._optimize_meshes(dest_assets)
    
    def _copy_scenes(self, build_dir: Path):
        """Copy scene files"""
        logger.info("Copying scenes...")
        
        scenes_dir = build_dir / "scenes"
        scenes_dir.mkdir(exist_ok=True)
        
        # Copy main scene
        if self.config.main_scene and self.config.main_scene.exists():
            shutil.copy(self.config.main_scene, scenes_dir / "main.scene.json")
        
        # Copy included scenes
        for scene_path in self.config.included_scenes:
            if scene_path.exists():
                shutil.copy(scene_path, scenes_dir / scene_path.name)
    
    def _generate_manifest(self, build_dir: Path):
        """Generate build manifest"""
        logger.info("Generating manifest...")
        
        manifest = {
            "project_name": self.config.project_name,
            "version": self.config.version,
            "platform": self.config.platform.value,
            "mode": self.config.mode.value,
            "main_scene": "scenes/main.scene.json",
            "window": {
                "width": self.config.window_width,
                "height": self.config.window_height,
                "fullscreen": self.config.fullscreen,
                "resizable": self.config.resizable
            }
        }
        
        manifest_path = build_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def _package_windows(self, build_dir: Path) -> Path:
        """Package for Windows"""
        logger.info("Packaging for Windows...")
        
        # Create launcher script
        launcher_path = build_dir / f"{self.config.project_name}.bat"
        with open(launcher_path, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"python runtime/player.py\n")
            f.write(f"pause\n")
        
        # Create executable (requires PyInstaller)
        # TODO: Use PyInstaller to create .exe
        
        # Create ZIP archive
        zip_path = build_dir.parent / f"{build_dir.name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in build_dir.rglob('*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(build_dir.parent))
        
        return zip_path
    
    def _package_linux(self, build_dir: Path) -> Path:
        """Package for Linux"""
        logger.info("Packaging for Linux...")
        
        # Create launcher script
        launcher_path = build_dir / f"{self.config.project_name}.sh"
        with open(launcher_path, 'w') as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"python3 runtime/player.py\n")
        
        # Make executable
        launcher_path.chmod(0o755)
        
        # Create tar.gz archive
        import tarfile
        tar_path = build_dir.parent / f"{build_dir.name}.tar.gz"
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(build_dir, arcname=build_dir.name)
        
        return tar_path
    
    def _package_macos(self, build_dir: Path) -> Path:
        """Package for macOS"""
        logger.info("Packaging for macOS...")
        
        # Create .app bundle structure
        app_name = f"{self.config.project_name}.app"
        app_dir = build_dir.parent / app_name
        
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy build files to Resources
        shutil.copytree(build_dir, resources_dir / "game")
        
        # Create launcher script
        launcher_path = macos_dir / self.config.project_name
        with open(launcher_path, 'w') as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"cd \"$(dirname \"$0\")/../Resources/game\"\n")
            f.write(f"python3 runtime/player.py\n")
        
        launcher_path.chmod(0o755)
        
        # Create Info.plist
        plist_path = contents_dir / "Info.plist"
        with open(plist_path, 'w') as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{self.config.project_name}</string>
    <key>CFBundleVersion</key>
    <string>{self.config.version}</string>
    <key>CFBundleExecutable</key>
    <string>{self.config.project_name}</string>
</dict>
</plist>
""")
        
        return app_dir
    
    def _package_web(self, build_dir: Path) -> Path:
        """Package for web (HTML5)"""
        logger.info("Packaging for web...")
        
        # Create HTML launcher
        html_path = build_dir / "index.html"
        with open(html_path, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.config.project_name}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        canvas {{
            border: 1px solid #333;
        }}
    </style>
</head>
<body>
    <canvas id="game-canvas" width="{self.config.window_width}" height="{self.config.window_height}"></canvas>
    <script>
        // TODO: Implement WebGL/WebAssembly runtime
        console.log("PolyForge Web Runtime");
    </script>
</body>
</html>
""")
        
        return build_dir
    
    def _compress_textures(self, assets_dir: Path):
        """Compress texture assets"""
        logger.info("Compressing textures...")
        # TODO: Implement texture compression
    
    def _compress_audio(self, assets_dir: Path):
        """Compress audio assets"""
        logger.info("Compressing audio...")
        # TODO: Implement audio compression
    
    def _optimize_meshes(self, assets_dir: Path):
        """Optimize mesh assets"""
        logger.info("Optimizing meshes...")
        # TODO: Implement mesh optimization
