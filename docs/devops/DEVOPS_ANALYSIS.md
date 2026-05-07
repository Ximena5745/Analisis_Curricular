# Análisis DevOps

## Estado Actual

**Sin pipelines CI/CD formales.**Sistema en modo desarrollo local.

## Estructura de Archivos

| Archivo | Descripción |
|---------|-----------|
| `.devcontainer/devcontainer.json` | Configuración Dev Containers |
| `pyvenv.cfg` | Configuración virtualenv |
| `requirements.txt` | Dependencias (si existe) |

## Entornos

| Entorno | Descripción |
|---------|-----------|
| Desarrollo | Máquina local (`python main.py`) |
| Dashboard | `streamlit run dashboard/app.py` |
| Producción | No configurado |

## Contenedores (Opcional)

```dockerfile
# No existe Dockerfile formal
# можно crear si se necesita
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## CI/CD

**No hay pipelines configurados.**

## Monitoreo

| Componente | Estado |
|-----------|--------|
| Logs | Archivo local (`logs/analytics_microcurricular.log`) |
| Métricas | Dashboard Streamlit |
| Alertas | No configurado |

## Recomendaciones Futuras

- [ ] GitHub Actions para tests
- [ ] Dockerización
- [ ] Helm chart si se despliega en Kubernetes
- [ ] Prometheus + Grafana para métricas
- [ ] Logs centralizados (ELK/stack)

## Despliegue Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/usuario/analisis_curricular.git
cd analisis_curricular

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python main.py

# 5. Dashboard (opcional)
streamlit run dashboard/app.py
```

## Observabilidad

- Logging: `logs/analisis_microcurricular.log`
- Configurable: nivel en `config.py`
- Errores: mensajes en consola

## Pendientes

- [ ] Dockerizar aplicación
- [ ] Configurar GitHub Actions
- [ ] Pipeline de despliegue
- [ ] Tests automatizados
- [ ] Helm chart