import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Recomendador interactivo de progresión de carga (2–3 semanas)")

# 1) Lista de ejercicios predefinidos + opción “otro”
ejercicios = [
    'sentadilla',
    'press banca',
    'peso muerto',
    'dominadas',
    'remo con barra',
    'otro ejercicio'
]

st.subheader("1) Introduce tus sesiones (hasta 20 filas)")

# Número de filas
n = st.number_input(
    "¿Cuántas sesiones (filas) quieres introducir?", 
    min_value=1, max_value=20, value=5, step=1
)

# Recopilamos las filas con inputs dinámicos, incluyendo fecha
filas = []
for i in range(int(n)):
    st.markdown(f"**Ejercicio {i+1}**")
    
    fecha = st.date_input(
        f"Fecha de la sesión (fila {i+1})",
        value=datetime.today().date(),
        key=f"fecha_{i}"
    )
    
    ex_sel = st.selectbox(
        f"Elige ejercicio (fila {i+1})", 
        ejercicios, key=f"ex_{i}"
    )
    if ex_sel == "otro ejercicio":
        ex = st.text_input(
            f"Nombre de ejercicio personalizado (fila {i+1})",
            key=f"otro_{i}"
        ).strip()
    else:
        ex = ex_sel

    s = st.number_input(
        f"Set (fila {i+1})",
        min_value=1, max_value=10, value=1, key=f"set_{i}"
    )
    p = st.number_input(
        f"Peso (kg) (fila {i+1})",
        min_value=0.0, step=0.5, key=f"peso_{i}"
    )
    r = st.number_input(
        f"Reps realizadas (fila {i+1})",
        min_value=0, max_value=20, value=7, key=f"reps_{i}"
    )
    t = st.number_input(
        f"Objetivo de reps (fila {i+1})",
        min_value=1, max_value=20, value=7, key=f"target_{i}"
    )

    # Convertir fecha a datetime para calcular intervalos a posteriori
    filas.append({
        "fecha": pd.to_datetime(fecha),
        "ejercicio": ex,
        "set": s,
        "peso (kg)": p,
        "reps": r,
        "target": t
    })

# 2) Cuando hayan introducido todo, calculamos
if st.button("Calcular recomendaciones y ver progresión"):
    df = pd.DataFrame(filas)
    # Si el usuario dejó algún nombre de ejercicio vacío al escoger "otro ejercicio", lo descartamos
    df = df[df["ejercicio"].str.strip() != ""].copy()
    
    # 2.a) Para cada ejercicio, ordenamos por fecha, calculamos recomendación y graficamos evolución
    resultados = []
    ejercicios_presentes = df["ejercicio"].unique()
    
    # Creamos dos columnas en el layout: tabla y gráfico
    tabla_col, grafs_col = st.columns((1, 1))
    
    with tabla_col:
        st.subheader("2) Recomendaciones por ejercicio y set")
        tabla_final = []
        for ex in ejercicios_presentes:
            df_ex = df[df["ejercicio"] == ex].sort_values("fecha")
            
            # Calcular promedio de las últimas 3 semanas (21 días) si hay suficientes datos
            ultima_fecha = df_ex["fecha"].max()
            inicio_3s = ultima_fecha - timedelta(days=21)
            df_ult_3s = df_ex[df_ex["fecha"] >= inicio_3s]
            
            # Para iterar serie a serie: baseamos la recomendación en dos casos:
            # - Si hay al menos 3 registros en esas 3 semanas, usamos el promedio de peso en ese periodo como base.
            # - Si no hay suficientes, usamos la última serie registrada.
            peso_base_3s = None
            if len(df_ult_3s) >= 3:
                peso_base_3s = df_ult_3s["peso (kg)"].mean()
            
            for idx, row in df_ex.iterrows():
                peso_actual = row["peso (kg)"]
                reps = row["reps"]
                target = row["target"]
                
                # Si no cumple el objetivo:
                if reps < target:
                    faltan = target - reps
                    factor = 1 - 0.05 * faltan
                    recomendado = round(peso_actual * factor, 1)
                else:
                    # Si cumple, usamos 2 % sobre el mejor de los dos: último peso o promedio 3s si existe
                    if peso_base_3s is not None:
                        referencia = max(peso_actual, peso_base_3s)
                    else:
                        referencia = peso_actual
                    recomendado = round(referencia * 1.02, 1)
                
                tabla_final.append({
                    "ejercicio": ex,
                    "fecha": row["fecha"].date(),
                    "set": row["set"],
                    "peso (kg)": peso_actual,
                    "reps": reps,
                    "target": target,
                    "recomendado (kg)": recomendado
                })
        
        df_res = pd.DataFrame(tabla_final)
        st.dataframe(df_res, use_container_width=True)
    
    with grafs_col:
        st.subheader("3) Gráfica de progresión por ejercicio")
        for ex in ejercicios_presentes:
            df_ex = df[df["ejercicio"] == ex].sort_values("fecha")
            if df_ex.shape[0] < 2:
                st.write(f"• {ex}: no hay suficientes datos para graficar.")
                continue
            
            # Dibujar con matplotlib
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot(df_ex["fecha"], df_ex["peso (kg)"], marker='o', linestyle='-')
            ax.set_title(f"Progresión: {ex}")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Peso (kg)")
            ax.grid(alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

    # 4) Guardar sesiones en CSV para posteriores análisis (opcional)
    if not df.empty:
        sesiones = df.copy()
        sesiones["timestamp_ingreso"] = pd.Timestamp.now()
        sesiones.to_csv(
            "sesiones_usuario.csv",
            mode="a",
            header=not os.path.exists("sesiones_usuario.csv"),
            index=False
        )

    # 5) Formulario de feedback
    st.subheader("4) Tu Feedback")
    with st.form("feedback_form"):
        utilidad = st.slider(
            "¿Qué tan útil te parece esta funcionalidad (2–3 semanas y gráficas)?",
            min_value=1, max_value=5, value=3, step=1
        )
        claridad = st.slider(
            "¿La interfaz es clara con estas nuevas opciones?",
            min_value=1, max_value=5, value=4, step=1
        )
        confianza = st.slider(
            "¿Confiarías en usar esta versión mejorada en tu entrenamiento?",
            min_value=1, max_value=5, value=3, step=1
        )
        mejoras = st.text_area("¿Qué mejorarías o agregarías ahora?")
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

