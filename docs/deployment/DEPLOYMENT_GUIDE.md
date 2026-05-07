# GUIDE de Despliegue

## Requisitos del Sistema

| Recurso | Requisito |
|--------|----------|
| Python | 3.8+ |
| OS | Windows / Linux / macOS |
| Memoria | 4GB RAM mínimo |
| Disco | 1GB libre |

## Instalación Local

```bash
# 1. Clonar o extraer
git clone https://github.com/usuario/analisis_curricular.git
cd analisis_curricular

# 2. Entorno virtual (recomendado)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar
python -c "import streamlit; print('OK')"
```

## Ejecución

### CLI (Consola)

```bash
# Procesar todos los archivos en data/raw/
python main.py
```

### Dashboard (Web)

```bash
# Iniciar dashboard Streamlit
streamlit run dashboard/app.py

# Puerto predeterminado: 8501
# Acceder: http://localhost:8501
```

## Producción (Básico)

```bash
# 1. Instalar en servidor
pip install -r requirements.txt

# 2. Configuration
export LOG_LEVEL=ERROR

# 3. Ejecutar como servicio
nohup python main.py > output.log 2>&1 &
```

## Docker (Futuro)

```dockerfile
# Dockerfile (no existe aún, ejemplo)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py"]
```

## Verificación

```bash
# Test de salud
python -c "from src import extractor, analyzer, validator; print('Modules OK')"

# Test de dependencias
pip list | grep -E "streamlit|pandas|plotly"
```

## Troubleshooting

| Error | Solución |
|-------|---------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `No such file: data/raw/` | Crear carpeta `data/raw/` |
| Puerto 8501 en uso | `streamlit run dashboard/app.py --server.port 8502` |