import numpy as np

def calcular_metricas_inventario(
    pronostico_m37,
    dias_operativos_bloque,
    tiempo_entrega_dias,
    nivel_servicio_z,
    std_diaria_historica,
    inventario_actual=None,
    costo_unitario=None,
    tasa_mantenimiento_anual=None,
    costo_ordenar=None,
    multiplo_empaque=None
):
    """
    Calcula las variables clave de control de inventario según las reglas
    de negocio flexibles (parámetros requeridos u opcionales).
    """
    # 1. Demanda Diaria Promedio (DDP) proyectada
    dias_bloque = float(dias_operativos_bloque) if dias_operativos_bloque > 0 else 30.0
    ddp = pronostico_m37 / dias_bloque
    
    # Proyección Anualizada (asumiendo 12 bloques al año o base anual proporcional)
    demanda_anual = pronostico_m37 * 12.0
    
    # 2. Stock de Seguridad (SS)
    te = float(tiempo_entrega_dias)
    z = float(nivel_servicio_z)
    ss_exacto = z * std_diaria_historica * np.sqrt(te)
    
    # 3. Punto de Reorden (PDR / ROP)
    pdr_exacto = (ddp * te) + ss_exacto
    
    # 4. Lote Económico de Compra (Q* / EOQ) - Opcional
    q_exacto = None
    if (
        costo_unitario is not None and costo_unitario > 0 and
        tasa_mantenimiento_anual is not None and tasa_mantenimiento_anual > 0 and
        costo_ordenar is not None and costo_ordenar > 0
    ):
        h = costo_unitario * tasa_mantenimiento_anual
        q_exacto = np.sqrt((2.0 * costo_ordenar * demanda_anual) / h)
        
    # 5. Stock Máximo
    lote_base = q_exacto if q_exacto is not None else pronostico_m37
    max_exacto = pdr_exacto + lote_base
    
    # 6. Ajuste por Múltiplo de Empaque (si aplica)
    if multiplo_empaque is not None and multiplo_empaque > 0:
        emp = float(multiplo_empaque)
        pdr_final = int(np.ceil(pdr_exacto / emp) * emp) if pdr_exacto > 0 else 0
        max_final = int(np.ceil(max_exacto / emp) * emp) if max_exacto > 0 else 0
        ss_final = int(np.ceil(ss_exacto))
        q_final = int(np.ceil(q_exacto / emp) * emp) if q_exacto is not None else None
    else:
        pdr_final = int(np.ceil(pdr_exacto))
        max_final = int(np.ceil(max_exacto))
        ss_final = int(np.ceil(ss_exacto))
        q_final = int(np.ceil(q_exacto)) if q_exacto is not None else None

    # 7. Sugerido de Reabasto Neto (si se ingresó Inventario Actual)
    reabasto_sugerido = None
    if inventario_actual is not None:
        inv_act = float(inventario_actual)
        if inv_act <= pdr_final:
            deficit = max_final - inv_act
            if multiplo_empaque is not None and multiplo_empaque > 0:
                reabasto_sugerido = int(np.ceil(deficit / float(multiplo_empaque)) * float(multiplo_empaque))
            else:
                reabasto_sugerido = int(np.ceil(deficit))
        else:
            reabasto_sugerido = 0

    return {
        "DDP": float(ddp),
        "Demanda_Anual": float(demanda_anual),
        "SS": ss_final,
        "PDR": pdr_final,
        "Stock_Maximo": max_final,
        "EOQ_Q": q_final,
        "Reabasto_Sugerido": reabasto_sugerido,
        "SS_Exacto": float(ss_exacto),
        "PDR_Exacto": float(pdr_exacto),
        "Max_Exacto": float(max_exacto)
    }