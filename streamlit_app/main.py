import requests

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# Configuración de la página y API
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")
API_URL = "http://api:8000"


def predictions_page():
    st.header("📈 Predicciones de ventas")
    col1, col2, col3 = st.columns(3)
    dia = col1.slider(
        "Día de la semana", min_value=1, max_value=7, value=1,
        format="%d", help="1=Lun, 7=Dom"
    )
    promo = col2.checkbox("Hubo promoción")
    festivo = col3.checkbox("Festivo")
    st.write("---")
    if st.button("Obtener predicción"):
        payload = {
            "DíaDeLaSemana": int(dia),
            "Promociones": int(promo),
            "Festivo": int(festivo)
        }
        try:
            resp = requests.post(f"{API_URL}/predict/", json=payload)
            resp.raise_for_status()
            ventas = resp.json().get("prediction")
            st.success(f"🛒 Ventas predichas: ${ventas:.2f}")
        except Exception as e:
            st.error(f"⚠️ Error al predecir: {e}")

def history_page():
    st.header("📜 Historial de predicciones")
    try:
        resp = requests.get(f"{API_URL}/history/")
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.dataframe(df)
    except Exception as e:
        st.error(f"⚠️ No se pudo cargar el historial: {e}")

def docs_page():
    st.header("📚 Documentación de la API")
    # st.markdown(f"[🔗 Ver documentación completa]({API_URL}/docs)")
    components.iframe(f"http://localhost:8000/docs", height=800, scrolling=True)

# Definición de páginas usando st.navigation (Streamlit 1.45)
pages = [
    st.Page(predictions_page, title="📈 Predictions"),
    st.Page(history_page,    title="📜 History"),
    st.Page(docs_page,       title="📚 Docs")
]

def main():
    selected_page = st.navigation(pages, position="sidebar", expanded=True)
    selected_page.run()

if __name__ == "__main__":
    main()
