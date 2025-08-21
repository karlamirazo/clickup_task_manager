# Configuración de mapeo de usuarios para ClickUp
# Mapeo de nombres de usuario a IDs de ClickUp

CLICKUP_USER_MAPPING = {
    "156221125": "Karla Ve",
    "88425546": "Veronica Mirazo", 
    "88425547": "Karla Rosas"
}

CLICKUP_USER_ID_TO_NAME = {
    "156221125": "Karla Ve",
    "88425546": "Veronica Mirazo",
    "88425547": "Karla Rosas"
}

def get_clickup_user_id(username: str) -> str:
    """Obtener ID de ClickUp por nombre de usuario"""
    for user_id, name in CLICKUP_USER_MAPPING.items():
        if name.lower() == username.lower():
            return user_id
    return None
