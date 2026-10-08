import numpy as np

def clasificar_intermitencia(series_historica):
    """
    Calcula ADI, CV2 y tamaño de lote promedio z
    para la categorización de demanda (Syntetos-Boylan).
    """
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
    # Base de cálculo de demanda diaria (DDP)
    dias_bloque = float(dias_operativos_bloque) if dias_operativos_bloque > 0 else 30.0
    ddp = pronostico_m37 / dias_bloque
    demanda_anual = pronostico_m37 * 12.0
    
    te = float(tiempo_entrega_dias)
    z = float(nivel_servicio_z)
    demanda_lt = ddp * te
    
    # -----------------------------------------------------------------
    # 1. CÁLCULOS TRADICIONALES DE INVENTARIO
    # -----------------------------------------------------------------
    ss_exacto = z * std_diaria_historica * np.sqrt(te)
    pdr_exacto = demanda_lt + ss_exacto
    
    # Lote Económico de Compra (EOQ) si existen parámetros financieros
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
    
    # -----------------------------------------------------------------
    # 2. PROTECCIÓN POR LOTE Z (DEMANDA INTERMITENTE / ERRÁTICA)
    # -----------------------------------------------------------------
    adi, cv2, z_lote, categoria = 0.0, 0.0, 0.0, "Regular"
    if series_historica is not None and len(series_historica) > 0:
        adi, cv2, z_lote, categoria = clasificar_intermitencia(series_historica)
        
        if categoria in ["Intermitente", "Errática", "Irregular (Lumpy)"]:
            pdr_exacto = max(pdr_exacto, z_lote)
            lote_operativo = max(lote_operativo, z_lote)
            max_exacto = pdr_exacto + lote_operativo
            ss_exacto = max(ss_exacto, pdr_exacto - demanda_lt)

    # Registro del Piso Base de Protección (Lead Time + SS)
    pdr_piso_base = max(pdr_exacto, demanda_lt + ss_exacto)

    # -----------------------------------------------------------------
    # 3. REGLA DE PISO POR EVENTO MÁXIMO (SKUS PRIORITARIOS)
    # -----------------------------------------------------------------
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
                    pdr_piso_base = max(pdr_piso_base, val_evt)
        except (ValueError, TypeError):
            pass

    # -----------------------------------------------------------------
    # 4. TECHO SUPREMO POR DÍAS DE COBERTURA MÁXIMA (90D / 30D)
    # -----------------------------------------------------------------
    dias_max_cobertura = 30.0 if z_redondeado in [1.04, 1.28] else 90.0
    tope_maximo_unidades = ddp * dias_max_cobertura
    cap_cobertura_aplicado = False

    if max_exacto > tope_maximo_unidades and ddp > 0:
        cap_cobertura_aplicado = True
        max_exacto = tope_maximo_unidades
        
        paso_min = float(multiplo_empaque) if (multiplo_empaque and multiplo_empaque > 0) else 1.0
        pdr_exacto = min(max_exacto - paso_min, pdr_piso_base)
        
        if pdr_exacto < (demanda_lt + ss_exacto) and max_exacto > demanda_lt:
            pdr_exacto = min(max_exacto - paso_min, demanda_lt + ss_exacto)
            
        ss_exacto = max(0.0, pdr_exacto - demanda_lt)

    # -----------------------------------------------------------------
    # 5. REDONDEOS POR EMPAQUE O ENTEROS
    # -----------------------------------------------------------------
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

    # -----------------------------------------------------------------
    # 6. REGLAS DE PISO, SEPARACIÓN Y GUARDIÁN FINAL DEL PDR
    # -----------------------------------------------------------------
    paso_min = int(multiplo_empaque) if (multiplo_empaque and multiplo_empaque > 0) else 1

    # CASO A: Excepción de Pieza Única (Max = 1)
    if max_final == 1:
        pdr_final = 1

    # CASO B: Inventario de Stock Máximo > 1
    elif max_final > 1:
        # 1. Salvaguarda de Separación Obligatoria (PDR < Stock Máximo)
        if pdr_final >= max_final:
            pdr_final = max_final - paso_min
            
        # 2. Piso Operativo Anti-Stockout para Sucursales (Si Max >= 4)
        if max_final >= 4:
            pdr_piso_operativo = max(2, int(np.ceil(0.33 * max_final)))
            if pdr_final < pdr_piso_operativo:
                pdr_final = pdr_piso_operativo

    # GUARDIÁN FINAL (Regla de Oro Absoluta):
    # Si Stock_Maximo > 0, PDR jamás puede ser 0
    if max_final > 0 and pdr_final < 1:
        pdr_final = 1
        
    # Garantía final de coherencia de límites
    if max_final > 1 and pdr_final >= max_final:
        pdr_final = max(1, max_final - 1)

    # -----------------------------------------------------------------
    # 7. REABASTO SUGERIDO NETO
    # -----------------------------------------------------------------
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