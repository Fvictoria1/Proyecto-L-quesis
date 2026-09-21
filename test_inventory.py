import engine
import inventory
import numpy as np

# Datos del SKU 1394000
demo_series = [
    0, 0, 0, 0, 0, 241, 322, 296, 246, 339, 390, 225, 
    794, 297, 282, 422, 212, 274, 120, 249, 271, 513, 
    338, 343, 154, 708, 235, 310, 154, 199, 205, 225, 
    211, 333, 342, 298
]

# 1. Obtener Pronóstico con Engine
res_forecast = engine.seleccionar_mejor_metodo(demo_series)
p_m37 = res_forecast["Pronostico_M37"]

# Desviación estándar diaria aproximada (sobre periodos no cero)
std_diaria = float(np.std(demo_series) / 30.0)

# 2. Calcular Inventarios
res_inv = inventory.calcular_metricas_inventario(
    pronostico_m37=p_m37,
    dias_operativos_bloque=30,
    tiempo_entrega_dias=5,
    nivel_servicio_z=1.65,
    std_diaria_historica=std_diaria,
    inventario_actual=12,
    costo_unitario=6.10,
    tasa_mantenimiento_anual=0.10,
    costo_ordenar=1.00,
    multiplo_empaque=50
)

print("\n" + "="*50)
print("📊 RESULTADOS INTEGRADOS FORECASTING + INVENTARIOS")
print("="*50)
print(f"📦 Método Ganador:      {res_forecast['Metodo_Ganador']}")
print(f"📈 Pronóstico M37:      {p_m37:.2f} unidades")
print(f"🛒 Lote Económico (Q*): {res_inv['EOQ_Q']} unidades (Ajustado empaque)")
print(f"🛡️ Stock Seguridad (SS):{res_inv['SS']} unidades")
print(f"📍 Punto Reorden (PDR): {res_inv['PDR']} unidades")
print(f"🔝 Stock Máximo (Max):  {res_inv['Stock_Maximo']} unidades")
print(f"🔔 Reabasto Sugerido:  {res_inv['Reabasto_Sugerido']} unidades")
print("="*50)