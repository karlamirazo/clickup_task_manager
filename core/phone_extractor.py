"""
Extractor de números de teléfono desde descripciones de tareas de ClickUp
Permite extraer números en formato internacional sin necesidad de campos personalizados
"""

import re
import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExtractedPhone:
    """Número de teléfono extraído con información adicional"""
    number: str
    original_text: str
    start_pos: int
    end_pos: int
    confidence: float
    format_type: str

class PhoneNumberExtractor:
    """Extractor inteligente de números de teléfono"""
    
    def __init__(self):
        # Patrones para diferentes formatos de números internacionales
        self.patterns = {
            # Formato internacional estándar: +[código país][número]
            "international_plus": r'\+(\d{1,4})\s*(\d{6,15})',
            
            # Formato internacional sin +: [código país][número]
            "international_no_plus": r'\b(\d{1,4})\s*(\d{6,15})\b',
            
            # Formato mexicano específico: +52 [número] o 52 [número]
            "mexican": r'(?:\+52|52)\s*(\d{10})',
            
            # Formato con paréntesis: +[código país] ([número])
            "parentheses": r'\+(\d{1,4})\s*\((\d{6,15})\)',
            
            # Formato con guiones: +[código país]-[número]
            "hyphenated": r'\+(\d{1,4})\s*-\s*(\d{6,15})',
            
            # Formato con espacios: +[código país] [número] [número]
            "spaced": r'\+(\d{1,4})\s+(\d{3,5})\s+(\d{3,5})\s+(\d{3,5})',
            
            # Formato WhatsApp específico: wa.me/[número]
            "whatsapp_link": r'wa\.me/(\d{10,15})',
            
            # Formato con texto descriptivo: WhatsApp: [número]
            "whatsapp_labeled": r'(?:WhatsApp|WA|Teléfono|Phone|Cel|Móvil|Tel):\s*(\+?[\d\s\-\(\)]{7,20})',
        }
        
        # Códigos de país comunes para validación
        self.common_country_codes = {
            '52': 'México',
            '1': 'Estados Unidos/Canadá',
            '33': 'Francia',
            '34': 'España',
            '39': 'Italia',
            '44': 'Reino Unido',
            '49': 'Alemania',
            '55': 'Brasil',
            '57': 'Colombia',
            '58': 'Venezuela',
            '593': 'Ecuador',
            '595': 'Paraguay',
            '598': 'Uruguay',
            '54': 'Argentina',
            '56': 'Chile',
            '51': 'Perú',
            '591': 'Bolivia',
            '503': 'El Salvador',
            '504': 'Honduras',
            '502': 'Guatemala',
            '505': 'Nicaragua',
            '506': 'Costa Rica',
            '507': 'Panamá'
        }
    
    def extract_phones_from_text(self, text: str) -> List[ExtractedPhone]:
        """
        Extrae todos los números de teléfono de un texto
        
        Args:
            text: Texto a analizar (descripción de tarea)
            
        Returns:
            Lista de números de teléfono extraídos
        """
        if not text:
            return []
        
        extracted_phones = []
        
        # Probar cada patrón
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                try:
                    phone_info = self._process_match(match, pattern_name, text)
                    if phone_info:
                        extracted_phones.append(phone_info)
                except Exception as e:
                    logger.warning(f"Error procesando match de {pattern_name}: {e}")
                    continue
        
        # Eliminar duplicados y ordenar por confianza
        unique_phones = self._remove_duplicates(extracted_phones)
        unique_phones.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_phones
    
    def _process_match(self, match, pattern_name: str, original_text: str) -> Optional[ExtractedPhone]:
        """Procesa un match encontrado y crea un objeto ExtractedPhone"""
        try:
            groups = match.groups()
            start_pos = match.start()
            end_pos = match.end()
            matched_text = match.group(0)
            
            # Construir el número completo según el patrón
            if pattern_name == "international_plus":
                country_code = groups[0]
                number = groups[1]
                full_number = f"+{country_code}{number}"
                confidence = 0.95
                
            elif pattern_name == "international_no_plus":
                country_code = groups[0]
                number = groups[1]
                full_number = f"+{country_code}{number}"
                confidence = 0.90
                
            elif pattern_name == "mexican":
                number = groups[0]
                full_number = f"+52{number}"
                confidence = 0.98
                
            elif pattern_name == "parentheses":
                country_code = groups[0]
                number = groups[1]
                full_number = f"+{country_code}{number}"
                confidence = 0.92
                
            elif pattern_name == "hyphenated":
                country_code = groups[0]
                number = groups[1]
                full_number = f"+{country_code}{number}"
                confidence = 0.88
                
            elif pattern_name == "spaced":
                country_code = groups[0]
                number_parts = groups[1:]
                full_number = f"+{country_code}{''.join(number_parts)}"
                confidence = 0.85
                
            elif pattern_name == "whatsapp_link":
                number = groups[0]
                full_number = f"+{number}" if not number.startswith('+') else number
                confidence = 0.96
                
            elif pattern_name == "whatsapp_labeled":
                number = groups[0]
                full_number = self._normalize_number(number)
                confidence = 0.94
                
            else:
                return None
            
            # Validar el número
            if not self._is_valid_phone(full_number):
                return None
            
            return ExtractedPhone(
                number=full_number,
                original_text=matched_text,
                start_pos=start_pos,
                end_pos=end_pos,
                confidence=confidence,
                format_type=pattern_name
            )
            
        except Exception as e:
            logger.error(f"Error procesando match: {e}")
            return None
    
    def _normalize_number(self, number: str) -> str:
        """Normaliza un número de teléfono"""
        # Remover espacios, guiones, paréntesis y otros caracteres
        normalized = re.sub(r'[\s\-\(\)\.]', '', number)
        
        # Asegurar que tenga el formato internacional
        if normalized.startswith('+'):
            return normalized
        elif normalized.startswith('52') and len(normalized) >= 12:
            return f"+{normalized}"
        elif normalized.startswith('1') and len(normalized) == 11:
            return f"+{normalized}"
        elif len(normalized) == 10 and not normalized.startswith('0'):
            # Números de 10 dígitos sin código de país - asumir México
            return f"+52{normalized}"
        elif len(normalized) >= 10:
            return f"+{normalized}"
        else:
            return normalized
    
    def _is_valid_phone(self, number: str) -> bool:
        """Valida si un número de teléfono es válido"""
        if not number:
            return False
        
        # Remover el + para el análisis
        clean_number = number.replace('+', '')
        
        # Verificar longitud mínima y máxima
        if len(clean_number) < 10 or len(clean_number) > 15:
            return False
        
        # Verificar que solo contenga dígitos
        if not clean_number.isdigit():
            return False
        
        # Verificar código de país
        if len(clean_number) >= 2:
            country_code = clean_number[:2]
            if country_code in self.common_country_codes:
                return True
        
        return True
    
    def _remove_duplicates(self, phones: List[ExtractedPhone]) -> List[ExtractedPhone]:
        """Elimina números duplicados manteniendo el de mayor confianza"""
        seen = {}
        
        for phone in phones:
            normalized = self._normalize_number(phone.number)
            
            if normalized not in seen or seen[normalized].confidence < phone.confidence:
                seen[normalized] = phone
        
        return list(seen.values())
    
    def extract_primary_phone(self, text: str) -> Optional[str]:
        """
        Extrae el número de teléfono principal (más confiable) de un texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Número de teléfono principal o None si no se encuentra
        """
        phones = self.extract_phones_from_text(text)
        return phones[0].number if phones else None
    
    def extract_all_phones(self, text: str) -> List[str]:
        """
        Extrae todos los números de teléfono únicos de un texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de números de teléfono únicos
        """
        phones = self.extract_phones_from_text(text)
        return [phone.number for phone in phones]
    
    def get_phone_info(self, number: str) -> dict:
        """
        Obtiene información detallada sobre un número de teléfono
        
        Args:
            number: Número de teléfono en formato internacional
            
        Returns:
            Diccionario con información del número
        """
        clean_number = number.replace('+', '')
        
        info = {
            'number': number,
            'country_code': None,
            'country_name': None,
            'is_valid': self._is_valid_phone(number),
            'length': len(clean_number)
        }
        
        if len(clean_number) >= 2:
            country_code = clean_number[:2]
            info['country_code'] = country_code
            info['country_name'] = self.common_country_codes.get(country_code, 'Desconocido')
        
        return info

# Instancia global del extractor
phone_extractor = PhoneNumberExtractor()

def extract_whatsapp_numbers_from_task(task_description: str, task_title: str = "") -> List[str]:
    """
    Función de conveniencia para extraer números de WhatsApp de una tarea de ClickUp
    
    Args:
        task_description: Descripción de la tarea
        task_title: Título de la tarea (opcional, para búsqueda adicional)
        
    Returns:
        Lista de números de teléfono únicos encontrados
    """
    # Combinar título y descripción para búsqueda
    search_text = f"{task_title}\n{task_description}" if task_title else task_description
    
    return phone_extractor.extract_all_phones(search_text)

def get_primary_whatsapp_number(task_description: str, task_title: str = "") -> Optional[str]:
    """
    Obtiene el número de WhatsApp principal de una tarea
    
    Args:
        task_description: Descripción de la tarea
        task_title: Título de la tarea (opcional)
        
    Returns:
        Número de teléfono principal o None si no se encuentra
    """
    # Combinar título y descripción para búsqueda
    search_text = f"{task_title}\n{task_description}" if task_title else task_description
    
    return phone_extractor.extract_primary_phone(search_text)
