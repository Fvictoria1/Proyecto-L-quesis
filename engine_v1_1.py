import numpy as np
import pandas as pd

# =====================================================================
# BLOQUE 1: MÉTODOS DE PRONÓSTICO (RETORNAN PRONÓSTICO PUNTUAL M37)
# =====================================================================

def promedio_simple(series):
    series = np.array(series, dtype=float)
    return float(np.mean(series))

def promedio_movil(series, window=4):
    series = np.array(series, dtype=float)
    if len(series) < window:
        return float(np.mean(series))
    return float(np.mean(series[-window:]))

def promedio_lineal(series, window=12):
    series = np.array(series, dtype=float)
    if len(series) < window:
        return float(np.mean(series))
    return float(np.mean(series[-window:]))

def suavizacion_exponencial_simple(series, alpha=0.2):
    series = np.array(series, dtype=float)
    forecast = series[0]
    for val in series[1:]:
        forecast = alpha * val + (1 - alpha) * forecast
    return float(forecast)

def suavizacion_exponencial_doble(series, alpha=0.2, beta=0.1):
    series = np.array(series, dtype=float)
    level = series[0]
    trend = series[1] - series[0] if len(series) > 1 else 0.0
    
    for val in series[1:]:
        last_level = level
        level = alpha * val + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        
    return float(max(0.0, level + trend))

def descomposicion_con_ciclo(series):
    series = np.array(series, dtype=float)
    n = len(series)
    if n < 24:
        return promedio_lineal(series, 12)
    
    avg_12 = np.mean(series[-12:])
    avg_prev_12 = np.mean(series[-24:-12])
    
    trend_factor = avg_12 / avg_prev_12 if avg_prev_12 > 0 else 1.0
    m_target_idx = -12
    seasonal_idx = series[m_target_idx] / avg_12 if avg_12 > 0 else 1.0
    
    forecast = avg_12 * trend_factor * seasonal_idx
    return float(max(0.0, forecast))

def descomposicion_sin_ciclo(series):
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
    croston_val = croston_tradicional(series, alpha)
    sba_val = (1.0 - (beta / 2.0)) * croston_val
    return float(sba_val)

def tsb_metodo(series, alpha=0.1, beta=0.1):
    """Método 10: Teunter-Syntetos-Babai (TSB) para demanda intermitente."""
    series = np.array(series, dtype=float)
    nz_indices = np.where(series > 0)[0]
    if len(nz_indices) == 0:
        return 0.0
    
    p = 1.0 / (np.mean(np.diff(nz_indices)) if len(nz_indices) > 1 else len(series))
    z = series[nz_indices[0]]
    
    for t in range(len(series)):
        if series[t] > 0:
            p = p + alpha * (1.0 - p)
            z = z + beta * (series[t] - z)
        else:
            p = p + alpha * (0.0 - p)
            
    return float(p * z)

# =====================================================================
# BLOQUE 2: EVALUACIÓN POR VENTANAS ACUMULADAS DE 3 MESES
# =====================================================================

def calcular_metricas_evaluacion(series, window=3):
    series = np.array(series, dtype=float)
    n = len(series)
    test_periods = 12
    
    metodos = {
        "Promedio Simple": promedio_simple,
        "Promedio Movil (4)": promedio_movil,
        "Promedio Lineal (12)": promedio_lineal,
        "Suavizacion Exp. Simple": suavizacion_exponencial_simple,
        "Suavizacion Exp. Doble": suavizacion_exponencial_doble,
        "Descomposicion Con Ciclo": descomposicion_con_ciclo,
        "Descomposicion Sin Ciclo": descomposicion_sin_ciclo,
        "Croston Tradicional": croston_tradicional,
        "Croston SBA": croston_sba,
        "TSB (Teunter-Syntetos-Babai)": tsb_metodo
    }
    
    resultados_eval = {}
    
    for nombre, func in metodos.items():
        cum_errors = []
        bias_list = []
        
        for i in range(n - test_periods, n - window + 1):
            sub = series[:i]
            act_cum = np.sum(series[i : i + window])
            pred_cum = func(sub) * window
            
            cum_errors.append(np.abs(pred_cum - act_cum))
            bias_list.append(pred_cum - act_cum)
            
        mae_cum = np.mean(cum_errors) if len(cum_errors) > 0 else 0.0
        bias_cum = np.abs(np.mean(bias_list)) if len(bias_list) > 0 else 0.0
        
        resultados_eval[nombre] = {
            "BIAS": float(bias_cum),
            "MAE": float(mae_cum)
        }
        
    return resultados_eval

# =====================================================================
# BLOQUE 3: SELECCIÓN DEL MÉTODO GANADOR (RELEASE 1.1)
# =====================================================================

def seleccionar_mejor_metodo(series):
    metricas = calcular_metricas_evaluacion(series, window=3)
    df_eval = pd.DataFrame(metricas).T
    
    n_methods = len(df_eval)
    
    df_eval["Rank_BIAS"] = df_eval["BIAS"].rank(ascending=True, method="min")
    df_eval["Rank_MAE"] = df_eval["MAE"].rank(ascending=True, method="min")
    
    df_eval["Puntos_BIAS"] = (n_methods - df_eval["Rank_BIAS"] + 1) * 0.40
    df_eval["Puntos_MAE"] = (n_methods - df_eval["Rank_MAE"] + 1) * 0.60
    
    df_eval["Puntaje_Total"] = df_eval["Puntos_BIAS"] + df_eval["Puntos_MAE"]
    
    ganador_nombre = df_eval["Puntaje_Total"].idxmax()
    
    metodos_map = {
        "Promedio Simple": promedio_simple,
        "Promedio Movil (4)": promedio_movil,
        "Promedio Lineal (12)": promedio_lineal,
        "Suavizacion Exp. Simple": suavizacion_exponencial_simple,
        "Suavizacion Exp. Doble": suavizacion_exponencial_doble,
        "Descomposicion Con Ciclo": descomposicion_con_ciclo,
        "Descomposicion Sin Ciclo": descomposicion_sin_ciclo,
        "Croston Tradicional": croston_tradicional,
        "Croston SBA": croston_sba,
        "TSB (Teunter-Syntetos-Babai)": tsb_metodo
    }
    
    pronostico_m37 = metodos_map[ganador_nombre](series)
    
    return {
        "Metodo_Ganador": ganador_nombre,
        "Pronostico_M37": float(pronostico_m37),
        "Puntaje_Total": float(df_eval.loc[ganador_nombre, "Puntaje_Total"]),
        "Detalle_Evaluacion": df_eval
    }