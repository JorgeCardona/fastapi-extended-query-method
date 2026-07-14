import os
import sys
import sqlite3
from pathlib import Path
from validate_data.utils.models import SearchFilters

# -----------------------------------------------------------------------------
# [ES] Fuerza UTF-8 en Windows para permitir imprimir emojis en consola.
# [EN] Forces UTF-8 on Windows so emojis can be printed to the console.
# -----------------------------------------------------------------------------
if os.name == "nt":
    os.system("chcp 65001 > nul")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "databases" / "products.db"

products = [
    # Computers
    ("Gamer Laptop", "computers", 1200.00, "Dell"), ("4K Monitor", "computers", 450.00, "Asus"), ("Mechanical Keyboard", "computers", 100.00, "Logitech"),

    # Furniture
    ("Executive Sofa", "furniture", 600.00, "MueblesSA"), ("Office Desk", "furniture", 350.00, "HomeCenter"), ("Ergonomic Chair", "furniture", 280.00, "ErgoPlus"),

    # Sports
    ("Soccer Ball", "sports", 35.00, "Nike"), ("Tennis Racket", "sports", 180.00, "Wilson"), ("Boxing Gloves", "sports", 75.00, "Everlast"),

    # Video Games
    ("PlayStation 5", "video games", 550.00, "Sony"), ("Xbox Series X", "video games", 530.00, "Microsoft"), ("Nintendo Switch OLED", "video games", 380.00, "Nintendo"),

    # Fruits
    ("Red Apple", "fruits", 1.20, "CampoFresco"), ("Banana", "fruits", 0.80, "CampoFresco"), ("Tommy Mango", "fruits", 2.50, "Frutas del Valle"),

    # Clothing
    ("Sports T-Shirt", "clothing", 28.00, "Adidas"), ("Slim Fit Jeans", "clothing", 55.00, "Levis"), ("Waterproof Jacket", "clothing", 95.00, "Columbia"),

    # Electronics
    ("Galaxy S25 Smartphone", "electronics", 999.00, "Samsung"), ("Wireless Headphones", "electronics", 149.00, "JBL"), ("Smartwatch", "electronics", 299.00, "Huawei"),

    # Books
    ("Cien Años de Soledad", "books", 24.00, "Penguin"), ("Clean Code", "books", 42.00, "Prentice Hall"), ("The Little Prince", "books", 18.00, "Salamandra"),

    # Toys
    ("LEGO Classic", "toys", 65.00, "LEGO"), ("Barbie Doll", "toys", 38.00, "Mattel"), ("Remote Control Car", "toys", 85.00, "Hot Wheels")
]


def insert_products(cursor, products):
    cursor.executemany(
        """
        INSERT INTO products (name, category, price, brand)
        VALUES (?, ?, ?, ?)
        """,
        products
    )


def insert_or_update_products(cursor, products):
    cursor.executemany(
        """
        INSERT INTO products (name, category, price, brand)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            category = excluded.category,
            price = excluded.price,
            brand = excluded.brand
        """,
        products,
    )


def initialize_database(products=None):
    try:
        with sqlite3.connect(DB_FILE) as connection:
            cursor = connection.cursor()

            cursor.execute("DROP TABLE IF EXISTS products")

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    brand TEXT NOT NULL
                )
                """
            )

            if products:
                insert_or_update_products(cursor, products)
                connection.commit()

                print(
                    f"✅ [ES] Base de datos sincronizada correctamente en "
                    f"'{os.path.abspath(DB_FILE)}'. "
                    f"{len(products)} productos procesados."
                )

                print(
                    f"✅ [EN] Database successfully synchronized at "
                    f"'{os.path.abspath(DB_FILE)}'. "
                    f"{len(products)} products processed."
                )

            else:
                print("⚠️ [ES] No se proporcionaron productos.")
                print("⚠️ [EN] No products were provided.")

    except sqlite3.Error as e:
        print(f"❌ [ES] Error en SQLite: {e}")
        print(f"❌ [EN] SQLite Error: {e}")


initialize_database(products)


def get_products_from_sqlite(
    filters: SearchFilters,
    limit: int,
    order_by: str,
) -> list[dict]:

    query_sql = """
        SELECT id, name, category, price, brand
        FROM products
        WHERE price <= ?
    """

    sql_params = [filters.max_price]

    if filters.categories:
        placeholders = ", ".join(["?"] * len(filters.categories))
        query_sql += f" AND category IN ({placeholders})"
        sql_params.extend(filters.categories)

    if filters.excluded_brands:
        placeholders = ", ".join(["?"] * len(filters.excluded_brands))
        query_sql += f" AND brand NOT IN ({placeholders})"
        sql_params.extend(filters.excluded_brands)

    allowed_columns = {"id", "price", "name"}
    order_column = order_by if order_by in allowed_columns else "id"

    query_sql += f" ORDER BY {order_column} ASC"
    query_sql += " LIMIT ?"

    sql_params.append(limit)

    with sqlite3.connect(DB_FILE) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()
        cursor.execute(query_sql, sql_params)

        rows = cursor.fetchall()

    return [dict(row) for row in rows]
