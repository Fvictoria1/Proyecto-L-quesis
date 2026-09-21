import numpy as np
import pandas as pd

# =====================================================================
# BLOQUE 1: MÉTODOS DE PRONÓSTICO (RETORNAN PRONÓSTICO PUNTUAL M37)
# =====================================================================

def promedio_simple(series):
    """Método 1: Promedio de todos los periodos históricos disponibles."""
    series = np.array(series, dtype=float)
    return float(np.mean(series))

def promedio_movil(series, window=4):
    """Método 2: Promedio Móvil de los últimos 'window' periodos (por defecto 4)."""
    series = np.array(series, dtype=float)
    if len(series) < window:
        return float(np.mean(series))
    return float(np.mean(series[-window:]))

def promedio_lineal(series, window=12):
    """Método 3: Promedio Móvil de los últimos 'window' periodos (12)."""
    series = np.array(series, dtype=float)
    if len(series) < window:
        return float(np.mean(series))
    return float(np.mean(series[-window:]))

def suavizacion_exponencial_simple(series, alpha=0.2):
    """Método 4: Suavización Exponencial Simple (SES)."""
    series = np.array(series, dtype=float)
    forecast = series[0]
    for val in series[1:]:
        forecast = alpha * val + (1 - alpha) * forecast
    return float(forecast)

def suavizacion_exponencial_doble(series, alpha=0.2, beta=0.1):
    """Método 5: Suavización Exponencial Doble (Holt)."""
    series = np.array(series, dtype=float)
    level = series[0]
    trend = series[1] - series[0] if len(series) > 1 else 0.0
    
    for val in series[1:]:
        last_level = level
        level = alpha * val + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        
    return float(max(0.0, level + trend))

def descomposicion_con_ciclo(series):
    """Método 6: Descomposición de series de tiempo considerando estacionalidad/ciclo."""
    series = np.array(series, dtype=float)
    n = len(series)
    if n < 24:
        return promedio_lineal(series, 12)
    
    # Promedio móvil de 12 meses como nivel base
    avg_12 = np.mean(series[-12:])
    avg_prev_12 = np.mean(series[-24:-12])
    
    # Factor de tendencia
    trend_factor = avg_12 / avg_prev_12 if avg_prev_12 > 0 else 1.0
    
    # Índice estacional del mes equivalente (hace 12 meses)
    m_target_idx = -12
    seasonal_idx = series[m_target_idx] / avg_12 if avg_12 > 0 else 1.0
    
    forecast = avg_12 * trend_factor * seasonal_idx
    return float(max(0.0, forecast))

def descomposicion_sin_ciclo(series):
    """Método 7: Descomposición ajustada omitiendo la componente cíclica."""
    series = np.array(series, dtype=float)
    n = len(series)
    if n < 24:
        return promedio_lineal(series, 12)
    
    avg_12 = np.mean(series[-12:])
    avg_prev_12 = np.mean(series[-24:-12])
    trend_factor = avg_12 / avg_prev_12 if avg_prev_12 > 0 else 1.0
    
    forecast = avg_12 * trend_factor
    return float(max(0.0, forecast))

def croston_tradicional(series, alpha=0.1):
    """Método 8: Método de Croston para demanda intermitente."""
    series = np.array(series, dtype=float)
    nz_indices = np.where(series > 0)[0]
    
    if len(nz_indices) == 0:
        return 0.0
    
    z = series[nz_indices[0]]
    p = float(nz_indices[0] + 1) if nz_indices[0] > 0 else 1.0
    q = 1
    
    for t in range(len(series)):
        if series[t] > 0:
            z = z + alpha * (series[t] - z)
            p = p + alpha * (q - p)
            q = 1
        else:
            q += 1
            
    return float(z / p) if p > 0 else 0.0

def croston_sba(series, alpha=0.1, beta=0.1):
    """Método 9: Syntetos-Boylan Approximation (SBA) para demanda intermitente/errática."""
    croston_val = croston_tradicional(series, alpha)
    sba_val = (1.0 - (beta / 2.0)) * croston_val
    return float(sba_val)


# =====================================================================
# BLOQUE 2: EVALUACIÓN HISTÓRICA (BIAS & MAE EN VENTANAS)
# =====================================================================

def calcular_metricas_evaluacion(series):
    """
    Simula el ajuste histórico (backtesting) para los 9 métodos
    y retorna BIAS (Sesgo) y MAE (Error Absoluto Medio) por algoritmo.
    """
    series = np.array(series, dtype=float)
    n = len(series)
    test_periods = 12  # Evaluamos los últimos 12 meses
    
    metodos = {
        "Promedio Simple": promedio_simple,
        "Promedio Movil (4)": promedio_movil,
        "Promedio Lineal (12)": promedio_lineal,
        "Suavizacion Exp. Simple": suavizacion_exponencial_simple,
        "Suavizacion Exp. Doble": suavizacion_exponencial_doble,
        "Descomposicion Con Ciclo": descomposicion_con_ciclo,
        "Descomposicion Sin Ciclo": descomposicion_sin_ciclo,
        "Croston Tradicional": croston_tradicional,
        "Croston SBA": croston_sba
    }
    
    resultados_eval = {}
    
    for nombre, func in metodos.items():
        errores = []
        for i in range(n - test_periods, n):
            sub_series = series[:i]
            val_real = series[i]
            pred = func(sub_series)
            errores.append(pred - val_real)
            
        errores = np.array(errores)
        bias = np.abs(np.mean(errores))  # Magnitud del sesgo medio
        mae = np.mean(np.abs(errores))   # Error absoluto medio
        
        resultados_eval[nombre] = {
            "BIAS": float(bias),
            "MAE": float(mae)
        }
        
    return resultados_eval


# =====================================================================
# BLOQUE 3: SELECCIÓN DEL MÉTODO GANADOR (RANKING 40% BIAS / 60% MAE)
# =====================================================================

def seleccionar_mejor_metodo(series):
    """
    Ejecuta el ranking ponderado sobre los 9 métodos
    y retorna el método ganador junto con el pronóstico puntual M37.
    """
    metricas = calcular_metricas_evaluacion(series)
    df_eval = pd.DataFrame(metricas).T
    
    # Asignación de puntos por Ranking (1° recibe más puntos)
    # BIAS peso 40%, MAE peso 60%
    n_methods = len(df_eval)
    
    df_eval["Rank_BIAS"] = df_eval["BIAS"].rank(ascending=True, method="min")
    df_eval["Rank_MAE"] = df_eval["MAE"].rank(ascending=True, method="min")
    
    df_eval["Puntos_BIAS"] = (n_methods - df_eval["Rank_BIAS"] + 1) * 0.40
    df_eval["Puntos_MAE"] = (n_methods - df_eval["Rank_MAE"] + 1) * 0.60
    
    df_eval["Puntaje_Total"] = df_eval["Puntos_BIAS"] + df_eval["Puntos_MAE"]
    
    # Método con mayor puntaje
    ganador_nombre = df_eval["Puntaje_Total"].idxmax()
    
    # Mapeo de funciones
    metodos_map = {
        "Promedio Simple": promedio_simple,
        "Promedio Movil (4)": promedio_movil,
        "Promedio Lineal (12)": promedio_lineal,
        "Suavizacion Exp. Simple": suavizacion_exponencial_simple,
        "Suavizacion Exp. Doble": suavizacion_exponencial_doble,
        "Descomposicion Con Ciclo": descomposicion_con_ciclo,
        "Descomposicion Sin Ciclo": descomposicion_sin_ciclo,
        "Croston Tradicional": croston_tradicional,
        "Croston SBA": croston_sba
    }
    
    pronostico_m37 = metodos_map[ganador_nombre](series)
    
    return {
        "Metodo_Ganador": ganador_nombre,
        "Pronostico_M37": float(pronostico_m37),
        "Puntaje_Total": float(df_eval.loc[ganador_nombre, "Puntaje_Total"]),
        "Detalle_Evaluacion": df_eval
    }