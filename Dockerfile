FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download es_core_news_sm \
    && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
# El modelo queda en la caché de la imagen: la asociación del perfil (src/asociacion_perfil.py) corre sin conexión

COPY . .

RUN mkdir -p data/raw data/processed data/output data/cache logs

EXPOSE 8501

CMD ["streamlit", "run", "dashboard_tematico.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
