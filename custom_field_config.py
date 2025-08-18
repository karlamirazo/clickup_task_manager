"""
Configuración de campos personalizados de ClickUp
IDs obtenidos automáticamente de la API de ClickUp
"""

# Configuración de campos personalizados por lista
CUSTOM_FIELD_IDS = {
    "901411770471": {  # PROYECTO 1
        "Email": "6464a671-73dd-4be5-b720-b5f0fe5adb04",
        "Celular": "51fa0661-0995-4c37-ba8d-3307aef300ca"
    },
    "901411770470": {  # PROYECTO 2
        # Sin campos personalizados
    },
    "901412119767": {  # Tareas del Proyecto
        "email": "621ed627-a960-4d3a-8ac7-7d0946fe17c2",  # Nota: minúscula
        "Celular": "51fa0661-0995-4c37-ba8d-3307aef300ca"
    }
}

def get_custom_field_id(list_id: str, field_name: str) -> str:
    """
    Obtener el ID de un campo personalizado específico
    
    Args:
        list_id: ID de la lista
        field_name: Nombre del campo (Email, Celular, etc.)
    
    Returns:
        ID del campo personalizado o None si no existe
    """
    list_fields = CUSTOM_FIELD_IDS.get(list_id, {})
    
    # Buscar coincidencia exacta primero
    if field_name in list_fields:
        return list_fields[field_name]
    
    # Buscar coincidencia case-insensitive
    for key, value in list_fields.items():
        if key.lower() == field_name.lower():
            return value
    
    return None

def get_all_custom_field_ids(list_id: str) -> dict:
    """
    Obtener todos los IDs de campos personalizados de una lista
    
    Args:
        list_id: ID de la lista
    
    Returns:
        Diccionario con {nombre_campo: id_campo}
    """
    return CUSTOM_FIELD_IDS.get(list_id, {})

def has_custom_fields(list_id: str) -> bool:
    """
    Verificar si una lista tiene campos personalizados
    
    Args:
        list_id: ID de la lista
    
    Returns:
        True si tiene campos personalizados
    """
    return bool(CUSTOM_FIELD_IDS.get(list_id, {}))
