# 🔧 Fases del Desarrollo del Modelo

Este directorio contiene el código fuente asociado al desarrollo del modelo predictivo de ventas diarias para una tienda minorista. El flujo de trabajo ha sido diseñado siguiendo principios de MLOps, priorizando la reproducibilidad, modularidad y trazabilidad.

---

## 1. Ingesta y Preparación de Datos

- **Fuente de datos:** archivo `.csv` o conexión a base de datos (extensible a MinIO).
- **Procesamiento inicial:**
  - Validación de tipos y estructura de las columnas.
  - Imputación de valores faltantes.
  - Codificación de variables categóricas si aplica.
  - Conversión y tratamiento de fechas.
  - División de los datos en entrenamiento, validación y test.

---

## 2. Análisis Exploratorio de Datos (EDA)

- Análisis visual y estadístico de la variable objetivo.
- Cálculo de correlaciones entre variables predictoras y ventas.
- Análisis temporal según tipo de día (laboral, fin de semana, feriado).
- Identificación de outliers, estacionalidades y tendencias.

---

## 3. Entrenamiento de Modelos Base

- **Modelos explorados:**
  - `LinearRegression()`
  - `DecisionTreeRegressor()`
  - `RandomForestRegressor()`
  - *(Opcionales: `Lasso`, `XGBoost`, etc.)*

- **Métricas de evaluación:**
  - R² (coeficiente de determinación)
  - RMSE (error cuadrático medio)
  - MAE (error absoluto medio)

- **Técnicas empleadas:**
  - Validación cruzada (`cross_val_score`)
  - Optimización de hiperparámetros (`GridSearchCV`, `RandomizedSearchCV`)

---

## 4. Evaluación y Visualización

- Reportes de rendimiento para cada modelo.
- Visualizaciones comparativas: ventas reales vs predichas.
- Análisis de errores por categoría y por horizonte temporal.
- Detección de sobreajuste y subajuste.

---

## 5. Empaquetado del Modelo

- Serialización del modelo final utilizando `joblib` o `pickle`.
- Exportación de métricas y visualizaciones en formato portable.
- Generación del archivo `requirements.txt` para replicar el entorno.

---

## 6. Preparación para Producción (MLOps)

- Desarrollo de scripts de inferencia (`predict.py`)
- Documentación técnica (README) y funcional.
- Posible implementación de API REST o CLI.
- Integración opcional con:
  - MLflow (para seguimiento de experimentos)
  - MinIO (para almacenamiento de datasets y artefactos)
  - Docker y GitHub Actions (para CI/CD)

---

# 🎯 Objetivo del Modelo

Predecir el volumen total de ventas diarias para el mes siguiente utilizando datos históricos. Esto permitirá a la tienda:

- Optimizar el stock de productos.
- Planificar campañas promocionales.
- Asignar personal de forma eficiente.

---

# 🧾 Notas Adicionales

- El código está diseñado para ser reutilizable y fácilmente integrable en pipelines productivos.
- Compatible con buenas prácticas de ciencia de datos y despliegue automatizado.
- Ideal como base para implementación de flujos de MLOps en entorno controlado.

---
