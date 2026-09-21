import streamlit as st
import pandas as pd
import numpy as np
import engine_v1_1 as engine
import inventory_v1_1 as inventory
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Sistema Forecasting & Inventarios v1.1",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Sistema de Planeación de la Demanda e Inventarios (Release 1.1)")
st.markdown("Versión 1.1: Evaluación por Ventanas de 3M, Algoritmo TSB e Inventarios con Protección por Lote $Z$.")

st.sidebar.header("⚙️ Configuración y Carga v1.1")

archivo_subido = st.sidebar.file_uploader("Sube tu archivo de Excel (.xlsx)", type=["xlsx"])

try:
    with open("Plantilla_Carga_Forecasting.xlsx", "rb") as f:
        bytes_plantilla = f.read()
    st.sidebar.download_button(
        label="📥 Descargar Plantilla Demo",
        data=bytes_plantilla,
        file_name="Plantilla_Carga_Forecasting.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
except FileNotFoundError:
    pass

if archivo_subido is not None:
    try:
        df_input = pd.read_excel(archivo_subido, sheet_name="Carga_Datos")
    except Exception:
        df_input = pd.read_excel(archivo_subido)
        
    st.success(f"✅ Archivo cargado correctamente: {len(df_input)} SKUs detectados.")
    
    if st.button("🚀 Procesar Pronósticos e Inventarios (v1.1)"):
        resultados_totales = []
        progress_bar = st.progress(0)
        total_skus = len(df_input)
        
        cols_historico = [col for col in df_input.columns if col.startswith("M") and col[1:].isdigit()]
        
        for idx, row in df_input.iterrows():
            sku = row["SKU"]
            desc = row.get("Descripcion", "")
            series_val = row[cols_historico].values.astype(float)
            
            dias_bloque = float(row.get("Dias_Operativos_Bloque", 30))
            te_dias = float(row.get("Tiempo_Entrega_Dias", 5))
            z_val = float(row.get("Nivel_Servicio_Deseado", 1.65))
            
            inv_act = row.get("Inventario_Actual", None)
            inv_act = float(inv_act) if pd.notna(inv_act) else None
            
            costo_u = row.get("Costo_Unitario", None)
            costo_u = float(costo_u) if pd.notna(costo_u) else None
            
            tasa_m = row.get("Tasa_Mantenimiento_Anual", None)
            tasa_m = float(tasa_m) if pd.notna(tasa_m) else None
            
            costo_o = row.get("Costo_Ordenar", None)
            costo_o = float(costo_o) if pd.notna(costo_o) else None
            
            mult_e = row.get("Multiplo_Empaque", None)
            mult_e = float(mult_e) if pd.notna(mult_e) else None
            
            # Engine 1.1
            res_forecast = engine.seleccionar_mejor_metodo(series_val)
            p_m37 = res_forecast["Pronostico_M37"]
            metodo = res_forecast["Metodo_Ganador"]
            puntaje = res_forecast["Puntaje_Total"]
            
            std_diaria = float(np.std(series_val) / dias_bloque)
            
            # Inventory 1.1
            res_inv = inventory.calcular_metricas_inventario(
                pronostico_m37=p_m37,
                dias_operativos_bloque=dias_bloque,
                tiempo_entrega_dias=te_dias,
                nivel_servicio_z=z_val,
                std_diaria_historica=std_diaria,
                series_historica=series_val,
                inventario_actual=inv_act,
                costo_unitario=costo_u,
                tasa_mantenimiento_anual=tasa_m,
                costo_ordenar=costo_o,
                multiplo_empaque=mult_e
            )
            
            fila_res = {
                "SKU": sku,
                "Descripcion": desc,
                "Categoria": res_inv["Categoria_Demanda"],
                "Lote_Venta_Z": res_inv["Lote_Promedio_Z"],
                "Metodo_Ganador": metodo,
                "Puntaje_Modelo": round(puntaje, 2),
                "Pronostico_M37": round(p_m37, 2),
                "Demanda_Diaria_DDP": round(res_inv["DDP"], 2),
                "Stock_Seguridad_SS": res_inv["SS"],
                "Punto_Reorden_PDR": res_inv["PDR"],
                "Stock_Maximo": res_inv["Stock_Maximo"],
                "Lote_Economico_Q": res_inv["EOQ_Q"],
                "Reabasto_Sugerido": res_inv["Reabasto_Sugerido"]
            }
            resultados_totales.append(fila_res)
            progress_bar.progress((idx + 1) / total_skus)
            
        df_resultados = pd.DataFrame(resultados_totales)
        st.session_state["df_resultados_v1_1"] = df_resultados
        st.session_state["df_input_v1_1"] = df_input
        st.success("🎉 ¡Procesamiento v1.1 completado!")

    if "df_resultados_v1_1" in st.session_state:
        df_res = st.session_state["df_resultados_v1_1"]
        
        st.subheader("📋 Resumen General de Resultados (v1.1)")
        st.dataframe(df_res, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📈 Inspección Individual por SKU")
        
        sku_seleccionado = st.selectbox("Selecciona un SKU:", df_res["SKU"].unique())
        
        row_res = df_res[df_res["SKU"] == sku_seleccionado].iloc[0]
        row_inp = st.session_state["df_input_v1_1"][st.session_state["df_input_v1_1"]["SKU"] == sku_seleccionado].iloc[0]
        
        cols_m = [c for c in st.session_state["df_input_v1_1"].columns if c.startswith("M") and c[1:].isdigit()]
        serie_hist = row_inp[cols_m].values.astype(float)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Categoría", row_res["Categoria"])
        col2.metric("Método Ganador", row_res["Metodo_Ganador"])
        col3.metric("Pronóstico M37", f"{row_res['Pronostico_M37']} uds")
        col4.metric("Punto Reorden (PDR)", f"{row_res['Punto_Reorden_PDR']} uds")
        col5.metric("Stock Máximo", f"{row_res['Stock_Maximo']} uds")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(range(1, 37), serie_hist, label="Ventas Históricas", marker="o", color="#1F4E78")
        ax.axhline(row_res["Pronostico_M37"], color="red", linestyle="--", label=f"Pronóstico M37 ({row_res['Pronostico_M37']})")
        ax.set_title(f"Historial y Proyección v1.1 - SKU {sku_seleccionado} ({row_res['Categoria']})")
        ax.set_xlabel("Periodos (M01 - M36)")
        ax.set_ylabel("Unidades")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.6)
        
        st.pyplot(fig)

else:
    st.info("👈 Sube la plantilla oficial para procesar la versión 1.1.")