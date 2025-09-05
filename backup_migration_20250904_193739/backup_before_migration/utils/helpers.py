"""
Utilidades y helpers para ClickUp Project Manager
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """Configurar logging de la aplicacion"""
    # Create directorio de logs si no existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def ensure_directory(path: str) -> None:
    """Asegurar que un directorio existe"""
    Path(path).mkdir(parents=True, exist_ok=True)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Cargar archivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Guardar datos en archivo JSON"""
    ensure_directory(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formatear datetime a string"""
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parsear string a datetime"""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def get_date_range(days: int = 30, end_date: Optional[datetime] = None) -> Dict[str, datetime]:
    """Get rango de fechas"""
    if end_date is None:
        end_date = datetime.utcnow()
    
    start_date = end_date - timedelta(days=days)
    
    return {
        "start_date": start_date,
        "end_date": end_date
    }

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Dividir lista en chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Get valor de diccionario de forma segura"""
    return dictionary.get(key, default)

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Aplanar diccionario anidado"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo"""
    import re
    # Remover caracteres no permitidos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limitar longitud
    if len(filename) > 255:
        filename = filename[:255]
    return filename

def get_file_size_mb(file_path: str) -> float:
    """Get tamano de archivo en MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def format_file_size(size_bytes: int) -> str:
    """Formatear tamano de archivo"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def generate_unique_id() -> str:
    """Generar ID unico"""
    import uuid
    return str(uuid.uuid4())

def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0):
    """Decorador para reintentar funcion en caso de excepcion"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
        return None
    
    return wrapper

def calculate_percentage(part: int, total: int) -> float:
    """Calcular porcentaje"""
    if total == 0:
        return 0.0
    return (part / total) * 100

def format_duration(seconds: int) -> str:
    """Formatear duracion en segundos a string legible"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def is_weekend(date: datetime) -> bool:
    """Verificar si una fecha es fin de semana"""
    return date.weekday() >= 5

def get_working_days(start_date: datetime, end_date: datetime) -> int:
    """Get dias laborables entre dos fechas"""
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        if not is_weekend(current_date):
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Combinar dos diccionarios"""
    result = dict1.copy()
    result.update(dict2)
    return result

def filter_dict(dictionary: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filtrar diccionario por claves especificas"""
    return {k: v for k, v in dictionary.items() if k in keys}

def exclude_dict(dictionary: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Excluir claves especificas del diccionario"""
    return {k: v for k, v in dictionary.items() if k not in keys}
