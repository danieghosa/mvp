import streamlit as st
import pandas as pd
import joblib

# 1) Configuración de página (si no la tienes ya al principio)
st.set_page_config(page_title="NextLift IA", layout="centered")

# 2) Carga del modelo
@st.cache_resource
def load_model():
    return joblib.load("nextlift_model.pkl")
model = load_model()

st.title("NextLift IA – Recomendaciones con IA")

# 3) Inputs de usuario
ejercicios = ["sentadilla", "press banca", "peso muerto", "otro ejercicio"]
ejercicio = st.selectbox("Ejercicio", ejercicios)
if ejercicio == "otro ejercicio":
    ejercicio = st.text_input("Nombre de ejercicio").strip()

peso_prev  = st.number_input("Peso anterior (kg)",   min_value=0.0, step=0.5, format="%.1f")
reps_prev  = st.number_input("Reps anteriores",       min_value=0,   max_value=20,  value=8, step=1)
rpe_prev   = st.number_input("RPE anterior (1–10)",   min_value=0.0, max_value=10.0, value=7.0, step=0.5, format="%.1f")
rir_prev   = st.number_input("RIR anterior (0–10)",   min_value=0.0, max_value=10.0, value=2.0, step=0.5, format="%.1f")
delta_peso = st.number_input("Δ Peso vs anterior (kg)",                  step=0.1, format="%.1f")
dias_entre = st.number_input("Días desde serie anterior", min_value=0, step=1)

# 4) Botón de predicción
if st.button("Calcular carga recomendada"):
    # Construir DataFrame con **exactamente** las 6 columnas que espera el modelo
    X_new = pd.DataFrame([{
        "peso_prev":  peso_prev,
        "reps_prev":  reps_prev,
        "rpe_prev":   rpe_prev,
        "rir_prev":   rir_prev,
        "delta_peso": delta_peso,
        "dias_entre": dias_entre
    }])

    # Predecir
    recomendado = model.predict(X_new)[0]
    st.success(f"🔮 Siguiente carga recomendada: **{recomendado:.1f} kg**")

    # Mostrar resumen
    resumen = X_new.copy()
    resumen["recomendado (kg)"] = round(recomendado, 1)
    st.subheader("Tus datos y la recomendación")
    st.table(resumen.T.rename(columns={0: "Valor"}))
