import streamlit as st
import pandas as pd

st.title("Recomendador de progresión de carga (+2%) con Feedback")

# 1) Subida del CSV
uploaded_file = st.file_uploader("1) Sube tu CSV de historial de entrenamiento", type=["csv"])
if not uploaded_file:
    st.info("Carga un archivo CSV para obtener recomendaciones.")
    st.stop()

# 2) Lectura y normalización
df = pd.read_csv(uploaded_file)
# Normalizar columnas de fecha y ejercicio
if "Date" in df.columns:
    df["fecha"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
if "Exercise Name" in df.columns:
    df["ejercicio"] = df["Exercise Name"]
else:
    df["ejercicio"] = df["ejercicio"]
if "Weight" in df.columns:
    df["peso (kg)"] = df["Weight"]
elif "peso (kg)" not in df.columns:
    st.error("Tu CSV debe tener columna 'Weight' o 'peso (kg)'")
    st.stop()

# 3) Cálculo de la recomendación (+2%)
df = df.sort_values(["ejercicio", "fecha", "set"])
last = df.groupby("ejercicio").last().reset_index()
last["recomendado (kg)"] = (last["peso (kg)"] * 1.02).round(1)

# 4) Mostrar tabla de recomendaciones
st.subheader("2) Recomendaciones de carga")
st.table(last[["ejercicio", "peso (kg)", "recomendado (kg)"]])

# 5) Formulario de feedback
st.subheader("3) Tu Feedback")
with st.form("feedback_form"):
    utilidad = st.slider(
        "¿Qué tan útil te parece la recomendación?",
        min_value=1, max_value=5, value=3, step=1
    )
    claridad = st.slider(
        "¿La recomendación es clara?",
        min_value=1, max_value=5, value=4, step=1
    )
    confianza = st.slider(
        "¿Confiarías en usar esto en tu entrenamiento?",
        min_value=1, max_value=5, value=3, step=1
    )
    mejoras = st.text_area(
        "¿Qué mejorarías o agregarías?"
    )
    enviado = st.form_submit_button("Enviar Feedback")
    if enviado:
        # Guardar feedback
        fb = {
            "timestamp": pd.Timestamp.now(),
            "utilidad": utilidad,
            "claridad": claridad,
            "confianza": confianza,
            "mejoras": mejoras
        }
        fb_df = pd.DataFrame([fb])
        fb_df.to_csv(
            "feedback.csv",
            mode="a",
            header=not pd.io.common.file_exists("feedback.csv"),
            index=False
        )
        st.success("¡Gracias por tu feedback!")
