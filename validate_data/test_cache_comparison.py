# python .\validate_data\test_cache_comparison.py

import time
import requests_cache
from utils.functions import (
    start_server,
    stop_server,
    wait_for_server,
    print_server_log,
    render_table,
    cleanup_test_files,
    URL,
    PAYLOAD,
    BASE_DIR,
)

CACHE_DIR = BASE_DIR / "cache_test_files"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def print_cache_status(session):
    """
    [ES]
    Imprime el estado actual del caché.

    [EN]
    Prints the current cache status.
    """

    cache_entries = list(session.cache.responses.keys())

    print("\nEstado del caché")
    print("-" * 70)
    print(f"Entradas almacenadas : {len(cache_entries)}")

    if cache_entries:
        print("Claves almacenadas:")
        for index, key in enumerate(cache_entries, start=1):
            print(f"  {index}. {key}")
    else:
        print("No existen respuestas almacenadas.")


def test_cache_behavior(query_saving_cache: bool) -> bool:
    """
    [ES]
    Ejecuta tres peticiones QUERY y presenta una tabla resumen por cada
    solicitud. Si verbose=True, también imprime el log detallado completo.

    [EN]
    Executes three QUERY requests and presents a summary table for each
    request. If verbose=True, it also prints the full detailed log.
    """

    print("\n" + "=" * 80)
    print("CACHE BEHAVIOR TEST")
    print("=" * 80)
    print(f"QUERY_SAVING_CACHE = {query_saving_cache}")

    if not query_saving_cache:
        print("\nEXPECTED RESULT")
        print("-" * 80)
        print("• Cache-Control = no-store")
        print("• Every request must hit the SERVER.")
        print("• Nothing should ever be stored in the cache.")
    else:
        print("\nEXPECTED RESULT")
        print("-" * 80)
        print("• Cache-Control header should not be present.")
        print("• First request should come from the SERVER.")
        print("• First response should be stored.")
        print("• Remaining requests should come from CACHE.")

    session = requests_cache.CachedSession(
        cache_name=str(CACHE_DIR / "test_query_method_request_cache"),
        backend="sqlite",
        allowable_methods=("GET", "HEAD", "QUERY"),
        cache_control=True,
    )

    session.cache.clear()

    initial_entries = len(session.cache.responses)
    expected_cache_header = (
        "no-store, no-cache, must-revalidate, max-age=0"
        if not query_saving_cache
        else None
    )

    print("\n" + "=" * 80)
    print("INITIAL CACHE STATE")
    print("=" * 80)
    print(f"Cached responses : {initial_entries}")
    if initial_entries:
        print("Cache is not empty.")
    else:
        print("Cache is empty.")

    passed = True
    report_rows = []

    for request_number in range(1, 4):
        before_entries = len(session.cache.responses)

        response = session.request(
            method="QUERY",
            url=URL,
            json=PAYLOAD,
            timeout=10,
        )

        after_entries = len(session.cache.responses)

        from_cache = getattr(response, "from_cache", False)
        cache_control = response.headers.get("Cache-Control")

        expected_from_cache = (
            False if not query_saving_cache else request_number != 1
        )

        cache_ok = cache_control == expected_cache_header
        source_ok = from_cache == expected_from_cache
        status_ok = response.status_code == 200
        
        request_passed = cache_ok and source_ok and status_ok
        passed &= request_passed

        cache_keys = list(session.cache.responses.keys())
        cache_key = cache_keys[0] if cache_keys else "-"

        if after_entries > before_entries:
            result_text = "Stored"
        elif from_cache:
            result_text = "Reused"
        else:
            result_text = "No cache"

        report_rows.append([
            str(query_saving_cache),
            request_number,
            response.status_code,
            "CACHE" if from_cache else "SERVER",
            cache_control or "<not present>",
            "CACHE" if expected_from_cache else "SERVER",
            "PASS" if status_ok else "FAIL",
            "PASS" if source_ok else "FAIL",
            "PASS" if cache_ok else "FAIL",
            len(cache_keys),
            cache_key,
            result_text,
        ])

    print_report_summary(session, report_rows, query_saving_cache)
    
    return passed

def print_report_summary(session, report_rows, query_saving_cache):

    final_entries = len(session.cache.responses)

    print("\n" + "=" * 80)
    print("REQUEST REPORT")
    print("=" * 80)

    headers = [
        "query_saving_cache",
        "Req",
        "Status",
        "Source",
        "Cache-Control",
        "Expected",
        "Status ✓",
        "Source ✓",
        "Header ✓",
        "Entries",
        "Cache Key",
        "Result",
    ]

    render_table(report_rows, headers)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    server_hits = sum(1 for row in report_rows if row[3] == "SERVER")
    cache_hits = sum(1 for row in report_rows if row[3] == "CACHE")

    print(f"Requests executed : 3")
    print(f"Responses SERVER  : {server_hits}")
    print(f"Responses CACHE   : {cache_hits}")
    print(f"Cache entries     : {final_entries}")

    if not query_saving_cache:
        print("Conclusion        : No response was cached.")
        print("                    Cache saving is DISABLED.")
    else:
        print("Conclusion        : First response was cached and reused.")
        print("                    Cache saving is ENABLED.")

    print("\nFINAL CACHE STATE")
    print("-" * 80)
    print(f"Cached responses : {final_entries}")

    if final_entries:
        print("\nStored cache keys:")
        for index, key in enumerate(session.cache.responses.keys(), start=1):
            print(f"{index}. {key}")
    else:
        print("Cache is empty.")

    print()

def main():
    server_process = None

    try:
        configurations = [
            (False, "query_saving_cache=False (No CACHE - NO Save data, No Reuse in Future requests)"),
            (True, "query_saving_cache=True (Using CACHE - Save Data for Reuse in Future requests)"),
        ]

        for query_saving_cache, config_name in configurations:
            print(f"\n{'=' * 70}")
            print(f"Configuring: {config_name}")
            print(f"{'=' * 70}")

            stop_server(server_process)
            server_process = start_server(query_saving_cache)

            if wait_for_server():
                print("✅ Server Ready")
                test_cache_behavior(query_saving_cache)
            else:
                print("❌ El servidor no respondió a tiempo")
                print_server_log()

            time.sleep(1)

        print(f"\n{'=' * 70}")
        print("📋 RESULTS SUMMARY")
        print("=" * 70)
        print("query_saving_cache=False (SIN CACHE - NO GUARDA)")
        print(" - Todas las peticiones deberían venir con from_cache=False")
        print(" - Cache-Control debería bloquear caché del cliente")
        print(" - NO se almacenan respuestas en caché")
        print()
        print("query_saving_cache=True (USING CACHE - SAVE DATA)")
        print(" - La primera petición debería venir con from_cache=False")
        print(" - Las siguientes podrían venir con from_cache=True")
        print(" - SÍ se almacenan respuestas en caché")
        print(" - Solo si el cliente respeta la caché")

    except KeyboardInterrupt:
        print("\n⚠️ Prueba interrumpida por el usuario")

    finally:
        stop_server(server_process)
        print("\n🧹 Server Stopped")
        
        # Limpiar archivos temporales al finalizar
        cleanup_test_files(auto_cleanup=True)


if __name__ == "__main__":
    main()
