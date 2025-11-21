"""
Service wrapper para ejecutar DocuSeal como servicio de Windows sin terminal visible.
Este script está optimizado para ser compilado con PyInstaller.
"""

import sys
import os
import logging
import ctypes
from pathlib import Path

# Configurar logging a archivo
log_dir = Path.home() / "AppData" / "Local" / "DocuSeal" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "docuseal_service.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def hide_console():
    """Ocultar la ventana de consola en Windows."""
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleCP(65001)
        # Solo ocultar si no está en modo debug
        if not sys.flags.debug:
            import subprocess
            import sys
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
    except Exception as e:
        logger.warning(f"No se pudo ocultar la consola: {e}")


def main():
    """Función principal que inicia el servicio uvicorn."""
    logger.info("=" * 60)
    logger.info("Iniciando DocuSeal Service")
    logger.info("=" * 60)
    
    try:
        import uvicorn
        from backend.app.main import app
        
        logger.info("Configurando uvicorn...")
        logger.info("Host: 0.0.0.0, Puerto: 8000")
        
        # Ejecutar uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="error",
            access_log=False,
            use_colors=False
        )
        
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Arguments: {sys.argv}")
    
    main()
