import pandas as pd
import numpy as np
import engine_v1_1
import inventory_v1_1

# Cargar la plantilla de prueba
df_carga = pd.read_excel('Plantilla_Carga_Forecasting.xlsx', sheet_name='Carga_Datos')
cols_m = [f"M{i:02d}" for i in range(1, 37)]

print("="*75)
print("🚀 PRUEBA DE EJECUCIÓN - RELEASE 1.1")
print("="*75)

for idx, row in df_carga.iterrows():
    sku = row['SKU']
    desc = row['Descripcion']
    series = row[cols_m].values.astype(float)
    
    # Engine 1.1
    res_forecast = engine_v1_1.seleccionar_mejor_metodo(series)
    p_m37 = res_forecast["Pronostico_M37"]
    
    # Inventory 1.1
    std_diaria = float(np.std(series) / float(row.get("Dias_Operativos_Bloque", 25.5)))
    res_inv = inventory_v1_1.calcular_metricas_inventario(
        pronostico_m37=p_m37,
        dias_operativos_bloque=row.get("Dias_Operativos_Bloque", 25.5),
        tiempo_entrega_dias=row.get("Tiempo_Entrega_Dias", 5),
        nivel_servicio_z=row.get("Nivel_Servicio_Deseado", 1.65),
        std_diaria_historica=std_diaria,
        series_historica=series
    )
    
    print(f"\n📦 SKU {sku} | {desc[:35]}")
    print(f"  • Categoría Demanda: {res_inv['Categoria_Demanda']} (ADI: {res_inv['ADI']}, CV2: {res_inv['CV2']})")
    print(f"  • Método Ganador:    {res_forecast['Metodo_Ganador']}")
    print(f"  • Pronóstico M37:    {p_m37:.2f} unidades")
    print(f"  • Lote Venta (Z):    {res_inv['Lote_Promedio_Z']} unidades")
    print(f"  • PDR Protegido:     {res_inv['PDR']} unidades | Max Protegido: {res_inv['Stock_Maximo']} unidades")

print("\n" + "="*75)