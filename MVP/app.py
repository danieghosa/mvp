import streamlit as st
import pandas as pd
import os

st.title("Recomendador interactivo de progresión de carga")

# 1) Lista inicial de ejercicios + opción “otro”
ejercicios = ['sentadilla', 'press banca', 'peso muerto', 'dominadas', 'remo con barra', 'otro ejercicio']

st.subheader("1) Introduce tus ejercicios")

n = st.number_input("¿Cuántos ejercicios quieres introducir?", min_value=1, max_value=20, value=5, step=1)

# Recopilamos las filas con inputs dinámicos
filas = []
for i in range(int(n)):
    st.markdown(f"**Ejercicio {i+1}**")
    ex_sel = st.selectbox(f"Elige ejercicio (fila {i+1})", ejercicios, key=f"ex_{i}")
    # Si elige “otro ejercicio”, mostramos un text_input para el nombre
    if ex_sel == "otro ejercicio":
        ex = st.text_input(f"Nombre de ejercicio personalizado (fila {i+1})", key=f"otro_{i}")
    else:
        ex = ex_sel

    s  = st.number_input(f"Set (fila {i+1})", min_value=1, max_value=10, value=1, key=f"set_{i}")
    p  = st.number_input(f"Peso (kg) (fila {i+1})", min_value=0.0, step=0.5, key=f"peso_{i}")
    r  = st.number_input(f"Reps realizadas (fila {i+1})", min_value=0, max_value=20, value=7, key=f"reps_{i}")
    t  = st.number_input(f"Objetivo de reps (fila {i+1})", min_value=1, max_value=20, value=7, key=f"target_{i}")
    filas.append({"ejercicio": ex, "set": s, "peso (kg)": p, "reps": r, "target": t})

# Cuando hayan introducido todo, calculamos
if st.button("Calcular recomendaciones"):
    df = pd.DataFrame(filas)
    # Función de recomendación
    def calcular_recomendado(row):
        if row['reps'] < row['target']:
            faltan = row['target'] - row['reps']
            factor = 1 - 0.05 * faltan
        else:
            factor = 1.02
        return round(row['peso (kg)'] * factor, 1)

    df['recomendado (kg)'] = df.apply(calcular_recomendado, axis=1)

    st.subheader("2) Recomendaciones por ejercicio")
    st.table(df[['ejercicio','set','peso (kg)','reps','target','recomendado (kg)']])

    # Feedback
    st.subheader("3) Tu feedback")
    with st.form("feedback_form"):
        utilidad = st.slider("¿Qué tan útil te parece esta funcionalidad?", 1, 5, 3)
        claridad = st.slider("¿La interfaz es clara?", 1, 5, 4)
        confianza = st.slider("¿Confiarías en usarla en tu entrenamiento?", 1, 5, 3)
        mejoras = st.text_area("¿Qué mejorarías o agregarías?")
        enviado = st.form_submit_button("Enviar feedback")
        if enviado:
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
                header=not os.path.exists("feedback.csv"),
                index=False
            )
            st.success("¡Gracias por tu feedback!")
