import engine

# Serie de ventas de prueba (36 meses del SKU 1394000)
demo_series = [
    0, 0, 0, 0, 0, 241, 322, 296, 246, 339, 390, 225, 
    794, 297, 282, 422, 212, 274, 120, 249, 271, 513, 
    338, 343, 154, 708, 235, 310, 154, 199, 205, 225, 
    211, 333, 342, 298
]

print("⏳ Ejecutando evaluación histórica de los 9 métodos...")
resultado = engine.seleccionar_mejor_metodo(demo_series)

print("\n" + "="*50)
print(f"🏆 MÉTODO GANADOR: {resultado['Metodo_Ganador']}")
print(f"📈 PRONÓSTICO M37: {resultado['Pronostico_M37']:.2f} unidades")
print(f"⭐ PUNTAJE TOTAL:  {resultado['Puntaje_Total']:.2f} / 9.00")
print("="*50)

print("\n📊 DETALLE DEL RANKING Y ERRORES HISTÓRICOS:")
df_detalle = resultado['Detalle_Evaluacion'][['BIAS', 'MAE', 'Puntaje_Total']].sort_values(by='Puntaje_Total', ascending=False)
print(df_detalle)