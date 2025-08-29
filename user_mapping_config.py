"""
Configuración de mapeo de usuarios de ClickUp
Este archivo mapea IDs de usuarios de ClickUp con nombres legibles
"""

# Mapeo de ID de ClickUp a nombres de usuario
CLICKUP_USER_MAPPING = {
    # Agrega aquí tus IDs de usuario de ClickUp y sus nombres correspondientes
    # Ejemplo: "12345678": "Juan Pérez"
}

# Mapeo inverso: ID a nombre
CLICKUP_USER_ID_TO_NAME = CLICKUP_USER_MAPPING

def get_clickup_user_id(username: str) -> str:
    """
    Obtiene el ID de ClickUp basado en el nombre de usuario
    
    Args:
        username: Nombre del usuario
        
    Returns:
        ID de usuario de ClickUp o None si no se encuentra
    """
    for user_id, name in CLICKUP_USER_MAPPING.items():
        if name.lower() == username.lower():
            return user_id
    return None

def get_clickup_user_name(user_id: str) -> str:
    """
    Obtiene el nombre del usuario basado en el ID de ClickUp
    
    Args:
        user_id: ID de usuario de ClickUp
        
    Returns:
        Nombre del usuario o el ID si no se encuentra el mapeo
    """
    return CLICKUP_USER_ID_TO_NAME.get(user_id, user_id)
