import numpy as np

def clasificar_intermitencia(series_historica):
    """Calcula ADI, CV2 y tamaño de lote promedio z."""
    s = np.array(series_historica, dtype=float)
    nz_indices = np.where(s > 0)[0]
    nz_vals = s[s > 0]
    
    if len(nz_indices) == 0:
        return 0.0, 0.0, 0.0, "Sin Demanda"
        
    intervals = np.diff(nz_indices) if len(nz_indices) > 1 else np.array([len(s)])
    adi = float(np.mean(intervals)) if len(intervals) > 0 else float(len(s))
    cv2 = float((np.std(nz_vals, ddof=1) / np.mean(nz_vals))**2) if len(nz_vals) > 1 else 0.0
    z_lote_promedio = float(np.mean(nz_vals))
    
    if adi < 1.32 and cv2 < 0.49:
        cat = "Regular"
    elif adi >= 1.32 and cv2 < 0.49:
        cat = "Intermitente"
    elif adi < 1.32 and cv2 >= 0.49:
        cat = "Errática"
    else:
        cat = "Irregular (Lumpy)"
        
    return adi, cv2, z_lote_promedio, cat


def calcular_metricas_inventario(
    pronostico_m37,
    dias_operativos_bloque,
    tiempo_entrega_dias,
    nivel_servicio_z,
    std_diaria_historica,
    series_historica=None,
    inventario_actual=None,
    costo_unitario=None,
    tasa_mantenimiento_anual=None,
    costo_ordenar=None,
    multiplo_empaque=None,
    evento_maximo=None
):
    dias_bloque = float(dias_operativos_bloque) if dias_operativos_bloque > 0 else 30.0
    ddp = pronostico_m37 / dias_bloque
    demanda_anual = pronostico_m37 * 12.0
    
    te = float(tiempo_entrega_dias)
    z = float(nivel_servicio_z)
    demanda_lt = ddp * te
    
    # 1. Cálculos Tradicionales
    ss_exacto = z * std_diaria_historica * np.sqrt(te)
    pdr_exacto = demanda_lt + ss_exacto
    
    # Lote Económico (EOQ)
    q_exacto = None
    if (
        costo_unitario is not None and costo_unitario > 0 and
        tasa_mantenimiento_anual is not None and tasa_mantenimiento_anual > 0 and
        costo_ordenar is not None and costo_ordenar > 0
    ):
        h = costo_unitario * tasa_mantenimiento_anual
        q_exacto = np.sqrt((2.0 * costo_ordenar * demanda_anual) / h)
        
    lote_base = q_exacto if q_exacto is not None else pronostico_m37
    lote_operativo = max(lote_base, 1.0)
    max_exacto = pdr_exacto + lote_operativo
    
    # 2. Protección de Lote Z para Demanda Intermitente / Errática
    adi, cv2, z_lote, categoria = 0.0, 0.0, 0.0, "Regular"
    if series_historica is not None and len(series_historica) > 0:
        adi, cv2, z_lote, categoria = clasificar_intermitencia(series_historica)
        
        if categoria in ["Intermitente", "Errática", "Irregular (Lumpy)"]:
            pdr_exacto = max(pdr_exacto, z_lote)
            lote_operativo = max(lote_operativo, z_lote)
            max_exacto = pdr_exacto + lote_operativo
            ss_exacto = max(ss_exacto, pdr_exacto - demanda_lt)

    # 3. Regla de Piso por Evento Máximo
    z_redondeado = round(z, 2)
    es_sku_prioritario = z_redondeado in [1.65, 2.05]
    piso_evento_aplicado = False
    
    if evento_maximo is not None:
        try:
            val_evt = float(evento_maximo)
            if not np.isnan(val_evt) and val_evt > 0 and es_sku_prioritario:
                if pdr_exacto < val_evt:
                    pdr_exacto = val_evt
                    ss_exacto = pdr_exacto - demanda_lt
                    max_exacto = pdr_exacto + lote_operativo
                    piso_evento_aplicado = True
        except (ValueError, TypeError):
            pass

    # 4. Regla de Techo por Cobertura Máxima de Días (Con Garantía de Separación)
    if z_redondeado in [1.04, 1.28]:
        dias_max_cobertura = 30.0
    else:
        dias_max_cobertura = 90.0

    tope_maximo_unidades = ddp * dias_max_cobertura
    cap_cobertura_aplicado = False

    if max_exacto > tope_maximo_unidades and ddp > 0:
        cap_cobertura_aplicado = True
        max_exacto = tope_maximo_unidades
        
        paso_min = float(multiplo_empaque) if (multiplo_empaque and multiplo_empaque > 0) else 1.0
        lote_disponible = max_exacto - demanda_lt
        
        if lote_disponible >= paso_min:
            lote_efectivo = min(lote_operativo, lote_disponible)
            pdr_exacto = max_exacto - lote_efectivo
        else:
            pdr_exacto = max(demanda_lt, max_exacto - paso_min) if max_exacto > paso_min else max_exacto
            
        ss_exacto = max(0.0, pdr_exacto - demanda_lt)

    # 5. Ajuste por Múltiplo de Empaque / Redondeos
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

    # 6. Salvaguarda Absoluta de Separación Obligatoria
    if max_final > 1 and pdr_final >= max_final:
        paso_separacion = int(multiplo_empaque) if (multiplo_empaque and multiplo_empaque > 0) else 1
        pdr_final = max(1, max_final - paso_separacion)

    # 7. Reabasto Sugerido Neto
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
        "Categoria_Demanda": categoria,
        "ADI": round(adi, 2),
        "CV2": round(cv2, 2),
        "Lote_Promedio_Z": round(z_lote, 1),
        "SS": ss_final,
        "PDR": pdr_final,
        "Stock_Maximo": max_final,
        "EOQ_Q": q_final,
        "Reabasto_Sugerido": reabasto_sugerido,
        "Piso_Evento_Aplicado": piso_evento_aplicado,
        "Cap_Cobertura_Aplicado": cap_cobertura_aplicado,
        "Dias_Max_Cobertura": int(dias_max_cobertura)
    }