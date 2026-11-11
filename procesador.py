import io

import pandas as pd
import streamlit as st

from picado.procesador import procesar_pdf

st.set_page_config(page_title="PICADO", layout="wide")
st.title("PICADO · Extractor de albaranes")

archivos = st.file_uploader(
    "Sube uno o varios PDFs escaneados", type="pdf", accept_multiple_files=True
)

if archivos and st.button("Procesar", type="primary"):
    resumen, detalle = [], []
    barra = st.progress(0.0, text="Preparando...")
    for archivo in archivos:
        filas, hojas = procesar_pdf(
            archivo.getvalue(),
            lambda n, total, nombre=archivo.name: barra.progress(
                n / total, text=f"{nombre}: hoja {n} de {total}"
            ),
        )
        for fila in filas:
            fila["Archivo"] = archivo.name
        for hoja in hojas:
            hoja["archivo"] = archivo.name
        resumen += filas
        detalle += hojas
    barra.empty()
    st.session_state["resumen"] = resumen
    st.session_state["detalle"] = detalle

if "resumen" in st.session_state:
    df = pd.DataFrame(st.session_state["resumen"])
    columnas = ["Archivo", "Cliente", "Destinatario", "Pedidos",
                "Palets", "Bultos", "Unidades", "Peso", "Hojas", "Avisos"]
    df = df[columnas]

    avisos = df[df["Avisos"] != ""]
    if len(avisos):
        st.warning("Revisa estas filas antes de exportar:")
        st.dataframe(avisos[["Archivo", "Destinatario", "Avisos"]], hide_index=True)

    st.subheader("Resultado (puedes corregir cualquier celda)")
    editado = st.data_editor(df, num_rows="dynamic")

    buffer = io.BytesIO()
    editado.to_excel(buffer, index=False)
    st.download_button(
        "Descargar Excel",
        data=buffer.getvalue(),
        file_name="picado_resultado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    with st.expander("Revisar hoja por hoja"):
        detalle = st.session_state["detalle"]
        i = st.selectbox(
            "Hoja", range(len(detalle)),
            format_func=lambda k: f"{detalle[k]['archivo']} · hoja {detalle[k]['pagina']}",
        )
        hoja = detalle[i]
        izquierda, derecha = st.columns(2)
        izquierda.image(hoja["miniatura"])
        derecha.write({k: hoja.get(k) for k in
                       ["cliente", "destinatario", "pedido", "palets",
                        "bultos", "unidades", "peso"]})
        derecha.text_area("Texto leído por el OCR", hoja["texto"], height=300)
