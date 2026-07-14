import os
import subprocess
import sys
import shutil
from pathlib import Path
import requests
import time

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[1]

HOST = "127.0.0.1"
PORT = 8000
QUERY_PATH = "/products/filter?limit=100&order_by=id"

URL = f"http://{HOST}:{PORT}{QUERY_PATH}"
LOG_FILE = BASE_DIR / "_uvicorn_test.log"
TABLE_FORMAT = "rounded_grid"

PAYLOAD = {
    "categories": [],
    "max_price": 90.0,
    "excluded_brands": [],
}

try:
    from tabulate import tabulate
except Exception:
    tabulate = None


def start_server(query_saving_cache: bool = True):
    """
    [ES]
    Inicia una instancia del servidor FastAPI Configuring el valor de la
    variable de entorno QUERY_SAVING_CACHE.

    [EN]
    Starts a FastAPI server instance configuring the QUERY_SAVING_CACHE
    environment variable.
    """

    env = os.environ.copy()
    env["QUERY_SAVING_CACHE"] = str(query_saving_cache).lower()

    log_file = open(LOG_FILE, "w", encoding="utf-8")

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "validate_data.main:app",
            "--app-dir",
            str(PROJECT_ROOT),
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--log-level",
            "info",
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=log_file,
        stderr=log_file,
    )

    return process


def stop_server(process):
    """
    [ES]
    Detiene el servidor si continúa en ejecución.

    [EN]
    Stops the server if it is still running.
    """

    if process is None:
        return

    if process.poll() is not None:
        return

    try:
        process.terminate()
        process.wait(timeout=5)
    except Exception:
        try:
            process.kill()
            process.wait(timeout=5)
        except Exception:
            pass


def wait_for_server(timeout_seconds: int = 30):
    """
    [ES]
    Espera hasta que el endpoint de health responda correctamente.

    [EN]
    Waits until the health endpoint becomes available.
    """

    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        try:
            response = requests.get(
                "http://127.0.0.1:8000/health",
                timeout=1,
            )

            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass

        time.sleep(1)

    return False


def print_server_log():
    """
    [ES]
    Imprime el contenido del log del servidor.

    [EN]
    Prints the server log content.
    """

    if not LOG_FILE.exists():
        return

    print("\n--- LOG DEL SERVIDOR ---")
    print(LOG_FILE.read_text(encoding="utf-8", errors="ignore"))
    print("--- FIN LOG ---\n")

def render_table(rows, headers):
    """
    Prints a readable table using tabulate if available.
    """
    if tabulate is not None:
        print(
            tabulate(
                rows,
                headers=headers,
                tablefmt=TABLE_FORMAT,
                stralign="center",
                numalign="center",
            )
        )
        return

    widths = [len(str(h)) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]

    for row in str_rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def fmt_row(row):
        return " | ".join(cell.center(widths[idx]) for idx, cell in enumerate(row))

    separator = "-+-".join("-" * w for w in widths)
    print(fmt_row(headers))
    print(separator)
    for row in str_rows:
        print(fmt_row(row))


def cleanup_test_files(auto_cleanup: bool = True):
    """
    [ES] Elimina archivos temporales usando patrones dinámicos.
    [EN] Removes temporary files using dynamic patterns.
    """
    if not auto_cleanup:
        print("\n🚫 [ES] Limpieza automática deshabilitada")
        print("🚫 [EN] Automatic cleanup disabled")
        return
    
        # Directorio desde donde se ejecuta (validate_data)
    current_dir = BASE_DIR.parent  # validate_data
    
    # Patrones de archivos a eliminar
    file_patterns = [
        "**/*.log",           # Todos los logs
        "**/*.sqlite",        # Todos los SQLite
        "**/*.db",            # Todos los DB
        "**/*.sqlite-shm",    # Archivos SQLite temporales
        "**/*.sqlite-wal",    # Archivos SQLite temporales
        "**/*.tmp",           # Archivos temporales
    ]
    
    cleaned_files = []
    
    # Eliminar archivos
    for pattern in file_patterns:
        for file_path in current_dir.glob(pattern):
            try:
                file_path.unlink()
                cleaned_files.append(str(file_path.relative_to(current_dir)))
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {file_path.name}: {e}")
    
    # Eliminar directorios __pycache__
    for pycache_dir in current_dir.glob("**/__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            cleaned_files.append(str(pycache_dir.relative_to(current_dir)) + "/")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar directorio {pycache_dir.name}: {e}")
    
    if cleaned_files:
        print(f"\n🧹 [ES] Archivos y directorios eliminados: {len(cleaned_files)}")
        print(f"🧹 [EN] Files and directories cleaned: {len(cleaned_files)}")
        for file_path in cleaned_files:
            print(f"   - {file_path}")
    else:
        print("\n🧹 [ES] No se encontraron archivos temporales")
        print("🧹 [EN] No temporary files found")


def cleanup_existing_files():
    """
    [ES] Alias para cleanup_test_files() - mantiene compatibilidad
    [EN] Alias for cleanup_test_files() - maintains compatibility
    """
    cleanup_test_files(auto_cleanup=True)


def cleanup_with_confirmation():
    """
    [ES]
    Versión interactiva de cleanup que pide confirmación al usuario.
    
    [EN]
    Interactive version of cleanup that asks for user confirmation.
    """
    
    print("\n❓ [ES] ¿Deseas eliminar los archivos temporales de prueba? (y/N): ", end="")
    print("\n❓ [EN] Do you want to delete temporary test files? (y/N): ", end="")
    
    try:
        response = input().strip().lower()
        if response in ['y', 'yes', 's', 'si', 'sí']:
            cleanup_test_files(auto_cleanup=True)
        else:
            print("\n✋ [ES] Limpieza cancelada por el usuario")
            print("✋ [EN] Cleanup cancelled by user")
    except (KeyboardInterrupt, EOFError):
        print("\n\n✋ [ES] Limpieza cancelada")
        print("✋ [EN] Cleanup cancelled")