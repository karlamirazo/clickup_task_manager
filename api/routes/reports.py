"""
Rutas para gestión de reportes
"""

from typing import List, Optional
import io
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import os

from core.database import get_db
from core.config import settings
from models.report import Report
from models.task import Task
from models.user import User
from api.schemas.report import (
    ReportCreate, 
    ReportResponse, 
    ReportList,
    ReportFilter
)

router = APIRouter()

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo reporte"""
    try:
        db_report = Report(
            name=report_data.name,
            description=report_data.description,
            report_type=report_data.report_type,
            parameters=report_data.parameters,
            filters=report_data.filters,
            date_range=report_data.date_range,
            workspace_id=report_data.workspace_id,
            created_by="system"  # En un sistema real, esto vendría del usuario autenticado
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return ReportResponse.from_orm(db_report)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el reporte: {str(e)}"
        )

@router.get("/", response_model=ReportList)
async def get_reports(
    workspace_id: Optional[str] = Query(None, description="ID del workspace"),
    report_type: Optional[str] = Query(None, description="Tipo de reporte"),
    status: Optional[str] = Query(None, description="Estado del reporte"),
    page: int = Query(0, ge=0, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    db: Session = Depends(get_db)
):
    """Obtener lista de reportes"""
    try:
        query = db.query(Report)
        
        # Aplicar filtros
        if workspace_id:
            query = query.filter(Report.workspace_id == workspace_id)
        if report_type:
            query = query.filter(Report.report_type == report_type)
        if status:
            query = query.filter(Report.status == status)
        
        # Contar total
        total = query.count()
        
        # Paginar
        reports = query.offset(page * limit).limit(limit).all()
        
        return ReportList(
            reports=[ReportResponse.from_orm(report) for report in reports],
            total=total,
            page=page,
            limit=limit,
            has_more=(page + 1) * limit < total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los reportes: {str(e)}"
        )

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un reporte específico"""
    try:
        db_report = db.query(Report).filter(Report.id == report_id).first()
        
        if not db_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        return ReportResponse.from_orm(db_report)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el reporte: {str(e)}"
        )

@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = Query("json", regex="^(json|csv|pdf)$", description="Formato de descarga: json, csv o pdf"),
    db: Session = Depends(get_db)
):
    """Descargar el reporte en JSON (archivo generado) o como CSV.

    - json: devuelve el archivo físico generado en `settings.REPORTS_STORAGE_PATH`.
    - csv: construye un CSV a partir de `db_report.data` para fácil lectura en Excel.
    """
    db_report = db.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")

    # Nombre base seguro
    base_name = db_report.name or "reporte"
    safe_name = "".join(c for c in base_name if c.isalnum() or c in (" ", "-", "_")) or "reporte"

    if format == "json":
        if not db_report.file_path or not os.path.exists(db_report.file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no disponible")
        filename = f"{safe_name}_{report_id}.json"
        return FileResponse(db_report.file_path, media_type="application/json", filename=filename)

    # CSV dinámico
    try:
        data = db_report.data or {}
        csv_lines: List[str] = []
        csv_lines.append("seccion,clave,valor")

        rt = (db_report.report_type or "").lower()
        if rt == "task_summary":
            csv_lines.append(f"resumen,total_tasks,{data.get('total_tasks', 0)}")
            csv_lines.append(f"resumen,completed_tasks,{data.get('completed_tasks', 0)}")
            csv_lines.append(f"resumen,pending_tasks,{data.get('pending_tasks', 0)}")
            for k, v in (data.get('status_distribution') or {}).items():
                csv_lines.append(f"status_distribution,{k},{v}")
            for k, v in (data.get('priority_distribution') or {}).items():
                csv_lines.append(f"priority_distribution,{k},{v}")
            for k, v in (data.get('assignee_distribution') or {}).items():
                csv_lines.append(f"assignee_distribution,{k},{v}")
        elif rt == "user_performance":
            csv_lines.append("usuario,total_tasks,completed_tasks,completion_rate,avg_priority")
            for perf in data.get('user_performance', []):
                csv_lines.append(
                    f"{perf.get('user_name','')},{perf.get('total_tasks',0)},{perf.get('completed_tasks',0)},{perf.get('completion_rate',0)},{perf.get('avg_priority',0)}"
                )
        elif rt == "task_timeline":
            csv_lines.append("task_id,task_name,created_at,due_date,status,priority")
            for item in data.get('timeline', []):
                csv_lines.append(
                    f"{item.get('task_id','')},{item.get('task_name','')},{item.get('created_at','')},{item.get('due_date','')},{item.get('status','')},{item.get('priority','')}"
                )
        elif rt == "workspace_overview":
            csv_lines.append(f"resumen,total_tasks,{data.get('total_tasks', 0)}")
            csv_lines.append(f"resumen,total_users,{data.get('total_users', 0)}")
            for k, v in (data.get('status_distribution') or {}).items():
                csv_lines.append(f"status_distribution,{k},{v}")
            for k, v in (data.get('priority_distribution') or {}).items():
                csv_lines.append(f"priority_distribution,{k},{v}")
        else:
            # Fallback genérico
            for k, v in (data or {}).items():
                csv_lines.append(f"general,{k},{v}")

        csv_content = "\n".join(csv_lines) + "\n"
        filename = f"{safe_name}_{report_id}.csv"
        headers = {
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Content-Type": "text/csv; charset=utf-8",
        }
        if format == "csv":
            return Response(content=csv_content, headers=headers, media_type="text/csv")

        # PDF dinámico con ReportLab
        if format == "pdf":
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
            except Exception as e:  # dependencia no disponible
                raise HTTPException(status_code=500, detail=f"Dependencia PDF no disponible: {e}")

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            title = Paragraph(f"{safe_name} (ID {report_id})", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            rt = (db_report.report_type or "").lower()
            table_data: List[List[str]] = []

            if rt == "task_summary":
                table_data = [["Métrica", "Valor"]]
                table_data.append(["Total tareas", str(data.get('total_tasks', 0))])
                table_data.append(["Completadas", str(data.get('completed_tasks', 0))])
                table_data.append(["Pendientes", str(data.get('pending_tasks', 0))])
                table_data.append(["", ""])  # separador visual
                table_data.append(["Distribución por estado", "Cantidad"])
                for k, v in (data.get('status_distribution') or {}).items():
                    table_data.append([str(k), str(v)])
                table_data.append(["", ""])  # separador
                table_data.append(["Distribución por prioridad", "Cantidad"])
                for k, v in (data.get('priority_distribution') or {}).items():
                    table_data.append([str(k), str(v)])
            elif rt == "user_performance":
                table_data = [["Usuario", "Total", "Completadas", "% Cumplimiento", "Prioridad Prom."]]
                for perf in data.get('user_performance', []):
                    table_data.append([
                        str(perf.get('user_name', '')),
                        str(perf.get('total_tasks', 0)),
                        str(perf.get('completed_tasks', 0)),
                        f"{perf.get('completion_rate', 0):.1f}",
                        f"{perf.get('avg_priority', 0):.2f}",
                    ])
            elif rt == "task_timeline":
                table_data = [["ID", "Nombre", "Creada", "Vence", "Estado", "Prioridad"]]
                for item in data.get('timeline', []):
                    table_data.append([
                        str(item.get('task_id', '')),
                        str(item.get('task_name', '')),
                        str(item.get('created_at', '')),
                        str(item.get('due_date', '')),
                        str(item.get('status', '')),
                        str(item.get('priority', '')),
                    ])
            elif rt == "workspace_overview":
                table_data = [["Métrica", "Valor"]]
                table_data.append(["Total tareas", str(data.get('total_tasks', 0))])
                table_data.append(["Total usuarios", str(data.get('total_users', 0))])
                table_data.append(["", ""])  # separador
                table_data.append(["Distribución por estado", "Cantidad"])
                for k, v in (data.get('status_distribution') or {}).items():
                    table_data.append([str(k), str(v)])
                table_data.append(["", ""])  # separador
                table_data.append(["Distribución por prioridad", "Cantidad"])
                for k, v in (data.get('priority_distribution') or {}).items():
                    table_data.append([str(k), str(v)])
            else:
                table_data = [["Clave", "Valor"]]
                for k, v in (data or {}).items():
                    table_data.append([str(k), str(v)])

            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]))
            elements.append(table)
            doc.build(elements)

            pdf_bytes = buffer.getvalue()
            buffer.close()
            headers = {
                "Content-Disposition": f"attachment; filename=\"{safe_name}_{report_id}.pdf\"",
                "Content-Type": "application/pdf",
            }
            return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")

        # Si el formato no coincide (por validación regex no debería pasar)
        raise HTTPException(status_code=400, detail="Formato no soportado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo generar CSV: {e}")

@router.post("/{report_id}/generate", response_model=ReportResponse)
async def generate_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Generar un reporte"""
    try:
        db_report = db.query(Report).filter(Report.id == report_id).first()
        
        if not db_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        # Actualizar estado
        db_report.status = "processing"
        db_report.updated_at = datetime.utcnow()
        db.commit()
        
        try:
            # Generar datos del reporte según el tipo
            report_data = await _generate_report_data(db_report, db)
            
            # Crear directorio si no existe
            os.makedirs(settings.REPORTS_STORAGE_PATH, exist_ok=True)
            
            # Guardar archivo
            file_path = os.path.join(settings.REPORTS_STORAGE_PATH, f"report_{report_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            
            # Actualizar reporte
            db_report.data = report_data
            db_report.summary = _generate_summary(report_data, db_report.report_type)
            db_report.status = "completed"
            db_report.generated = True
            db_report.generated_at = datetime.utcnow()
            db_report.file_path = file_path
            db_report.file_size = os.path.getsize(file_path)
            
            db.commit()
            db.refresh(db_report)
            
            return ReportResponse.from_orm(db_report)
            
        except Exception as e:
            # Marcar como fallido
            db_report.status = "failed"
            db_report.updated_at = datetime.utcnow()
            db.commit()
            raise e
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el reporte: {str(e)}"
        )

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un reporte"""
    try:
        db_report = db.query(Report).filter(Report.id == report_id).first()
        
        if not db_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        # Eliminar archivo si existe
        if db_report.file_path and os.path.exists(db_report.file_path):
            os.remove(db_report.file_path)
        
        db.delete(db_report)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el reporte: {str(e)}"
        )

@router.get("/types/available")
async def get_available_report_types():
    """Obtener tipos de reportes disponibles"""
    return {
        "report_types": [
            {
                "id": "task_summary",
                "name": "Resumen de Tareas",
                "description": "Resumen general de tareas por estado, prioridad y asignación"
            },
            {
                "id": "user_performance",
                "name": "Rendimiento de Usuarios",
                "description": "Análisis de productividad y carga de trabajo por usuario"
            },
            {
                "id": "task_timeline",
                "name": "Línea de Tiempo",
                "description": "Análisis temporal de creación y completado de tareas"
            },
            {
                "id": "workspace_overview",
                "name": "Vista General del Workspace",
                "description": "Resumen completo del workspace con métricas clave"
            },
            {
                "id": "custom_analysis",
                "name": "Análisis Personalizado",
                "description": "Reporte personalizable con filtros específicos"
            }
        ]
    }

async def _generate_report_data(report: Report, db: Session) -> dict:
    """Generar datos del reporte según el tipo"""
    if report.report_type == "task_summary":
        return await _generate_task_summary(report, db)
    elif report.report_type == "user_performance":
        return await _generate_user_performance(report, db)
    elif report.report_type == "task_timeline":
        return await _generate_task_timeline(report, db)
    elif report.report_type == "workspace_overview":
        return await _generate_workspace_overview(report, db)
    elif report.report_type == "custom_analysis":
        return await _generate_custom_analysis(report, db)
    else:
        raise ValueError(f"Tipo de reporte no soportado: {report.report_type}")

async def _generate_task_summary(report: Report, db: Session) -> dict:
    """Generar resumen de tareas"""
    # Obtener todas las tareas si no hay workspace_id específico
    if report.workspace_id:
        query = db.query(Task).filter(Task.workspace_id == report.workspace_id)
    else:
        query = db.query(Task)
    
    # Aplicar filtros de fecha si existen
    if report.date_range:
        start_date = report.date_range.get("start_date")
        end_date = report.date_range.get("end_date")
        if start_date:
            query = query.filter(Task.created_at >= start_date)
        if end_date:
            query = query.filter(Task.created_at <= end_date)
    
    tasks = query.all()
    
    print(f"Generando reporte para {len(tasks)} tareas")
    
    # Estadísticas por estado
    status_stats = {}
    priority_stats = {}
    assignee_stats = {}
    
    for task in tasks:
        # Por estado
        status = task.status or "pendiente"
        status_stats[status] = status_stats.get(status, 0) + 1
        
        # Por prioridad
        priority = task.priority or 3  # Prioridad normal por defecto
        priority_stats[priority] = priority_stats.get(priority, 0) + 1
        
        # Por asignado
        assignee = task.assignee_id or "Sin asignar"
        assignee_stats[assignee] = assignee_stats.get(assignee, 0) + 1
    
    return {
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks if t.status == "complete"]),
        "pending_tasks": len([t for t in tasks if t.status != "complete"]),
        "status_distribution": status_stats,
        "priority_distribution": priority_stats,
        "assignee_distribution": assignee_stats,
        "generated_at": datetime.utcnow().isoformat()
    }

async def _generate_user_performance(report: Report, db: Session) -> dict:
    """Generar reporte de rendimiento de usuarios"""
    # Obtener usuarios del workspace
    users = db.query(User).filter(User.workspace_id == report.workspace_id).all()
    
    user_performance = []
    for user in users:
        # Obtener tareas del usuario
        user_tasks = db.query(Task).filter(
            Task.workspace_id == report.workspace_id,
            Task.assignee_id == user.clickup_id
        ).all()
        
        completed_tasks = [t for t in user_tasks if t.status == "complete"]
        
        performance = {
            "user_id": user.clickup_id,
            "user_name": user.full_name,
            "total_tasks": len(user_tasks),
            "completed_tasks": len(completed_tasks),
            "completion_rate": len(completed_tasks) / len(user_tasks) * 100 if user_tasks else 0,
            "avg_priority": sum(t.priority for t in user_tasks) / len(user_tasks) if user_tasks else 0
        }
        user_performance.append(performance)
    
    return {
        "user_performance": user_performance,
        "generated_at": datetime.utcnow().isoformat()
    }

async def _generate_task_timeline(report: Report, db: Session) -> dict:
    """Generar línea de tiempo de tareas"""
    query = db.query(Task).filter(Task.workspace_id == report.workspace_id)
    
    # Aplicar filtros de fecha
    if report.date_range:
        start_date = report.date_range.get("start_date")
        end_date = report.date_range.get("end_date")
        if start_date:
            query = query.filter(Task.created_at >= start_date)
        if end_date:
            query = query.filter(Task.created_at <= end_date)
    
    tasks = query.order_by(Task.created_at).all()
    
    timeline = []
    for task in tasks:
        timeline.append({
            "task_id": task.clickup_id,
            "task_name": task.name,
            "created_at": task.created_at.isoformat(),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status,
            "priority": task.priority
        })
    
    return {
        "timeline": timeline,
        "total_tasks": len(timeline),
        "generated_at": datetime.utcnow().isoformat()
    }

async def _generate_workspace_overview(report: Report, db: Session) -> dict:
    """Generar vista general del workspace"""
    # Estadísticas generales
    total_tasks = db.query(Task).filter(Task.workspace_id == report.workspace_id).count()
    total_users = db.query(User).filter(User.workspace_id == report.workspace_id).count()
    
    # Tareas por estado
    status_counts = db.query(Task.status, db.func.count(Task.id)).filter(
        Task.workspace_id == report.workspace_id
    ).group_by(Task.status).all()
    
    # Tareas por prioridad
    priority_counts = db.query(Task.priority, db.func.count(Task.id)).filter(
        Task.workspace_id == report.workspace_id
    ).group_by(Task.priority).all()
    
    return {
        "workspace_id": report.workspace_id,
        "total_tasks": total_tasks,
        "total_users": total_users,
        "status_distribution": dict(status_counts),
        "priority_distribution": dict(priority_counts),
        "generated_at": datetime.utcnow().isoformat()
    }

async def _generate_custom_analysis(report: Report, db: Session) -> dict:
    """Generar análisis personalizado"""
    query = db.query(Task).filter(Task.workspace_id == report.workspace_id)
    
    # Aplicar filtros personalizados
    if report.filters:
        if report.filters.get("status"):
            query = query.filter(Task.status == report.filters["status"])
        if report.filters.get("priority"):
            query = query.filter(Task.priority == report.filters["priority"])
        if report.filters.get("assignee_id"):
            query = query.filter(Task.assignee_id == report.filters["assignee_id"])
    
    tasks = query.all()
    
    return {
        "filtered_tasks": len(tasks),
        "tasks": [task.to_dict() for task in tasks],
        "filters_applied": report.filters,
        "generated_at": datetime.utcnow().isoformat()
    }

def _generate_summary(data: dict, report_type: str) -> dict:
    """Generar resumen del reporte"""
    if report_type == "task_summary":
        return {
            "total_tasks": data.get("total_tasks", 0),
            "most_common_status": max(data.get("status_distribution", {}).items(), key=lambda x: x[1])[0] if data.get("status_distribution") else None,
            "most_common_priority": max(data.get("priority_distribution", {}).items(), key=lambda x: x[1])[0] if data.get("priority_distribution") else None
        }
    elif report_type == "user_performance":
        performances = data.get("user_performance", [])
        if performances:
            best_performer = max(performances, key=lambda x: x["completion_rate"])
            return {
                "total_users": len(performances),
                "best_performer": best_performer["user_name"],
                "avg_completion_rate": sum(p["completion_rate"] for p in performances) / len(performances)
            }
    elif report_type == "workspace_overview":
        return {
            "total_tasks": data.get("total_tasks", 0),
            "total_users": data.get("total_users", 0),
            "statuses_count": len(data.get("status_distribution", {}))
        }
    
    return {"summary": "Resumen generado automáticamente"}
