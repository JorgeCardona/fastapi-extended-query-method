# FastAPI Extended Query Method - HTTP QUERY Method Support

[🇺🇸 English](#english) | [🇪🇸 Español](#español)

## English

### 📋 What is FastAPIWithQueryHttpMethod?

`FastAPIWithQueryHttpMethod` is a class that extends FastAPI to add native support for the HTTP QUERY method with automatic cache saving control and temporary file cleanup.

### 🎯 What is it for?

The class provides:
- **Native HTTP QUERY method support**: Allows creating endpoints that accept this semantically correct method
- **Intelligent cache control**: With `query_saving_cache=False` adds headers to prevent cache saving
- **Security middleware**: Automatically adds headers in QUERY responses when they contain sensitive data
- **Automatic cleanup**: Removes temporary files (.log, .sqlite, .db, __pycache__) after tests finish

### ⚙️ Configuration

- **`query_saving_cache=True` (DEFAULT)**: Allows QUERY responses to be cached by clients
- **`query_saving_cache=False`**: Prevents QUERY responses from being cached (adds no-store headers)

### 🧹 Automatic Cleanup

Test scripts include automatic cleanup that removes:
- Log files (*.log)
- SQLite databases (*.sqlite, *.db)
- Temporary SQLite files (*.sqlite-shm, *.sqlite-wal)
- Python cache directories (__pycache__)
- Temporary files (*.tmp)

### 🧪 How to run tests

Step 0: Run Automatic QUERY and API Cache Tests
```bash
python .\validate_data\test_api_query_method.py
python .\validate_data\test_cache_comparison.py
```
This script tests the basic QUERY method and displays the complete request. It also tests the Cache management of the QUERY method.

#### Step 1: Start the API
```bash
cd validate_data
python -m uvicorn main:app --reload
```

#### Step 2: Run QUERY tests
```bash
python test_api_query_method.py
```
This script tests the basic QUERY method and shows the complete request.

#### Step 3: Verify cache behavior
```bash
python test_cache_comparison.py
```
This script automatically tests both configurations:
- `query_saving_cache=False` (NO CACHE - DOESN'T SAVE)
- `query_saving_cache=True` (WITH CACHE - DOES SAVE)

---

## 🚀 Quick Testing

1. **Navigate**: `cd validate_data`
2. **Start API**: `python -m uvicorn main:app --reload`
3. **Test QUERY method**: `python test_api_query_method.py`
4. **Test cache behavior**: `python test_cache_comparison.py`

## 📊 Expected Results

### test_api_query_method.py
- ✅ Shows complete QUERY request details
- ✅ HTTP Status: 200
- ✅ Returns product data from database
- ✅ Displays execution ID and total found

### test_cache_comparison.py

#### query_saving_cache=False (NO CACHE)
- ✅ All requests: `from_cache=False`
- ✅ Cache-Control: `no-store, no-cache, must-revalidate, max-age=0`
- ✅ Cache entries: `0`

#### query_saving_cache=True (WITH CACHE)
- ✅ First request: `from_cache=False`
- ✅ Subsequent requests: `from_cache=True`
- ✅ Cache entries: `1+`

### Automatic Cleanup
- ✅ Removes temporary files after each test
- ✅ Cleans SQLite databases and logs
- ✅ Removes Python cache directories
- ✅ Shows list of cleaned files
---

## Español

### 📋 ¿Qué es FastAPIWithQueryHttpMethod?

`FastAPIWithQueryHttpMethod` es una clase que extiende FastAPI para añadir soporte nativo al método HTTP QUERY con control automático de guardado de caché y limpieza de archivos temporales.

### 🎯 ¿Para qué sirve?

La clase proporciona:
- **Soporte nativo para método HTTP QUERY**: Permite crear endpoints que acepten este método semánticamente correcto
- **Control inteligente de caché**: Con `query_saving_cache=False` añade headers para evitar que se guarde en caché
- **Middleware de seguridad**: Añade headers automáticamente en respuestas QUERY cuando contienen datos sensibles
- **Limpieza automática**: Elimina archivos temporales (.log, .sqlite, .db, __pycache__) al finalizar las pruebas

### ⚙️ Configuración

- **`query_saving_cache=True` (DEFAULT)**: Permite que las respuestas QUERY se guarden en caché del cliente
- **`query_saving_cache=False`**: Evita que las respuestas QUERY se guarden en caché (añade headers no-store)

### 🧹 Limpieza Automática

Los scripts de prueba incluyen limpieza automática que elimina:
- Archivos de log (*.log)
- Bases de datos SQLite (*.sqlite, *.db)
- Archivos temporales SQLite (*.sqlite-shm, *.sqlite-wal)
- Directorios de caché de Python (__pycache__)
- Archivos temporales (*.tmp)

### 🧪 Cómo hacer las pruebas

#### Paso 0: Ejecutar pruebas Automaticas de QUERY y Cache de API
```bash
python .\validate_data\test_api_query_method.py
python .\validate_data\test_cache_comparison.py
```
Este script prueba el método QUERY básico y muestra el request completo, También El manejo de Cache del metodo QUERY.

## USO MANUAL DE LA API
#### Paso 1: Iniciar la API
```bash
cd validate_data
python -m uvicorn main:app --reload
```

#### Paso 2: Ejecutar pruebas de QUERY
```bash
python test_api_query_method.py
```
Este script prueba el método QUERY básico y muestra el request completo.

#### Paso 3: Verificar comportamiento de caché
```bash
python test_cache_comparison.py
```
Este script prueba automáticamente ambas configuraciones:
- `query_saving_cache=False` (SIN CACHE - NO GUARDA)
- `query_saving_cache=True` (USING CACHE - SAVE DATA)

---