"""
Modelo de datos para reportes
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from core.database import Base

class Report(Base):
    """Modelo de reporte"""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuración del reporte
    report_type = Column(String(100), nullable=False)  # task_summary, user_performance, etc.
    parameters = Column(JSON, nullable=True)  # Parámetros del reporte
    
    # Filtros y configuración
    filters = Column(JSON, nullable=True)  # Filtros aplicados
    date_range = Column(JSON, nullable=True)  # Rango de fechas
    
    # Resultados
    data = Column(JSON, nullable=True)  # Datos del reporte
    summary = Column(JSON, nullable=True)  # Resumen del reporte
    
    # Estado
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    generated = Column(Boolean, default=False)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generated_at = Column(DateTime, nullable=True)
    
    # Metadatos
    workspace_id = Column(String(255), nullable=True)
    created_by = Column(String(255), nullable=False)
    
    # Archivos
    file_path = Column(String(500), nullable=True)  # Ruta al archivo generado
    file_size = Column(Integer, nullable=True)  # Tamaño del archivo en bytes
    
    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', type='{self.report_type}')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "report_type": self.report_type,
            "parameters": self.parameters,
            "filters": self.filters,
            "date_range": self.date_range,
            "data": self.data,
            "summary": self.summary,
            "status": self.status,
            "generated": self.generated,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "workspace_id": self.workspace_id,
            "created_by": self.created_by,
            "file_path": self.file_path,
            "file_size": self.file_size
        }
