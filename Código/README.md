# UBA_MLOPs1

# Proyecto MLOps: Modelo predictivo de ventas - Evaluación de para tienda Minorista

Este proyecto forma parte de una pipeline de desarrollo y despliegue de modelos de machine learning en entornos productivos. El objetivo es construir un modelo robusto capaz de predecir el total de ventas mensuales de una tienda minorista, a partir de datos históricos diarios.

El sistema se integrará en una arquitectura MLOps donde los artefactos del modelo, la trazabilidad de experimentos, y las métricas estarán disponibles para auditoría y versionado.

-------------------------------------------------------------------------------
🔧 FASES DEL DESARROLLO DEL MODELO

## 1. Ingesta y Preparación de Datos
- Fuente: CSV / base de datos.
- Procesos:
    - Validación de esquema y tipos de datos.
    - Imputación de valores faltantes.
    - Codificación de variables categóricas si aplica.
    - División en conjuntos de entrenamiento, validación y test.

## 2. Análisis Exploratorio de Datos (EDA)
- Análisis visual y estadístico de distribución de ventas.
- Evaluación de correlaciones entre variables predictoras y objetivo.
- Agrupamientos temporales: comparativas entre días hábiles, festivos y fines de semana.
- Identificación de outliers o patrones estacionales.

## 3. Entrenamiento de Modelos Base
- Modelos evaluados:
    - `LinearRegression()`
    - `DecisionTreeRegressor()`
    - `RandomForestRegressor()`
    - *(opcional: agregar Lasso, XGBoost, etc.)*
- Métricas:
    - Coeficiente de determinación: R²
    - Error cuadrático medio (RMSE)
    - Error absoluto medio (MAE)
- Técnicas:
    - Búsqueda de hiperparámetros (`GridSearchCV` / `RandomizedSearchCV`)
    - Validación cruzada (`cross_val_score`)

## 4. Evaluación y Visualización
- Generación de reportes con métricas para cada modelo.
- Gráficos de comparación: ventas reales vs predichas.
- Análisis de errores por categoría y por horizonte temporal.

## 5. Empaquetado del Modelo
- Serialización del mejor modelo (`joblib` o `pickle`).
- Exportación de métricas y visualizaciones.
- Generación de archivo `requirements.txt` y documentación del entorno virtual.

## 6. Preparación para Producción (MLOps)
- Scripts de inferencia reutilizables (`predict.py`)
- Interfaz REST o CLI para consultas.
- Documentación técnica y funcional en README.md
- (Opcional) Integración con `MLflow` para seguimiento de experimentos.
- (Opcional) Despliegue en contenedor Docker / pipeline CI/CD.

-------------------------------------------------------------------------------
🎯 OBJETIVO DEL MODELO
Predecir el total de ventas para el mes siguiente en función de variables históricas,
lo que permitirá a la tienda:
- Optimizar su inventario.
- Definir estrategias promocionales.
- Asignar personal de forma eficiente.

-------------------------------------------------------------------------------
🧾 NOTAS ADICIONALES
- Enfocado en reproducibilidad, modularidad y trazabilidad.
- Compatible con flujos de trabajo de ciencia de datos y arquitectura MLOps.
- Código limpio, comentado y preparado para pruebas automatizadas.
