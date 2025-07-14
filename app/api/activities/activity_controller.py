#   LOGICA NO APLICADA AUN DE CONSEJOS DEL DIA 
#
# def obtener_consejo_del_dia():
#     hoy = date.today()
    
#     # Verificar si ya hay un consejo para hoy
#     consejo_hoy = buscar_consejo_mostrado_hoy(hoy)
    
#     if consejo_hoy:
#         return consejo_hoy
    
#     # Obtener todos los consejos no mostrados recientemente
#     ultimos_meses = hoy - timedelta(days=90) # Por ejemplo, no repetir en 3 meses
#     consejos_no_mostrados = obtener_consejos_no_mostrados(ultimos_meses)
    
#     if not consejos_no_mostrados:
#         # Si todos han sido mostrados, reiniciar el historial
#         reiniciar_historial_consejos()
#         consejos_no_mostrados = obtener_todos_consejos()
    
#     # Seleccionar aleatoriamente uno de los consejos no mostrados
#     consejo_seleccionado = choice(consejos_no_mostrados)
    
#     registrar_consejo_mostrado(consejo_seleccionado.id, hoy)
    
#     return consejo_seleccionado