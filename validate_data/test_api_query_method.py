# python .\validate_data\test_api_query_method.py

import json
from pathlib import Path
import http.client

from utils.functions import (
    start_server,
    stop_server,
    wait_for_server,
    print_server_log,
    render_table,
    cleanup_test_files,
    PAYLOAD,
    BASE_DIR,
    QUERY_PATH,
    HOST,
    PORT, 
)


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[0]


def main():
    server_process = None

    try:
        print("\n" + "=" * 80)
        print("STARTING SERVER")
        print("=" * 80)

        server_process = start_server()

        if not wait_for_server():
            print("❌ El servidor no respondió a tiempo")
            print_server_log()
            return

        print("✅ Server Ready")

        print("\n" + "=" * 80)
        print("QUERY REQUEST")
        print("=" * 80)
        print(f"Method      : QUERY")
        print(f"URL         : http://{HOST}:{PORT}{QUERY_PATH}")
        print(f"Headers     : Content-Type: application/json")
        print(f"Body        : {json.dumps(PAYLOAD, ensure_ascii=False, indent=2)}")
        print("=" * 80)

        connection = http.client.HTTPConnection(HOST, PORT, timeout=10)

        headers = {
            "Content-Type": "application/json"
        }

        body = json.dumps(PAYLOAD, ensure_ascii=False)

        connection.request(
            "QUERY",
            QUERY_PATH,
            body=body,
            headers=headers
        )

        response = connection.getresponse()
        raw_data = response.read().decode("utf-8", errors="ignore")
        connection.close()

        try:
            response_json = json.loads(raw_data)
        except json.JSONDecodeError:
            print("❌ La respuesta no es un JSON válido")
            print(raw_data)
            return

        products = response_json.get("products", [])

        print("\n" + "=" * 80)
        print("QUERY RESPONSE")
        print("=" * 80)

        print(f"HTTP Status  : {response.status}")
        print(f"Reason       : {response.reason}")
        print(f"Status       : {response_json.get('status')}")
        print(f"Execution Id : {response_json.get('execution_id')}")
        print(f"Total Found  : {response_json.get('total_found')}")

        rows = []

        for product in products:
            rows.append([
                product.get("id", "-"),
                product.get("name", "-"),
                product.get("category", "-"),
                product.get("price", "-"),
                product.get("brand", "-"),
            ])

        print("\n" + "=" * 80)
        print("PRODUCTS")
        print("=" * 80)

        render_table(
            rows,
            [
                "Id",
                "Name",
                "Category",
                "Price",
                "Brand",
            ],
        )

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Products returned : {len(products)}")
        print("Result            : PASS" if response.status == 200 else "Result            : FAIL")

    except KeyboardInterrupt:
        print("\n⚠️ Prueba interrumpida por el usuario")

    except Exception as e:
        print(f"\n❌ Error ejecutando la prueba: {e}")
        print_server_log()

    finally:
        stop_server(server_process)
        print("\n🧹 Server Stopped")
        
        # Limpiar archivos temporales al finalizar
        cleanup_test_files(auto_cleanup=True)


if __name__ == "__main__":
    main()