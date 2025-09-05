"""
Plantillas HTML para emails de notificaciones de ClickUp
"""

from typing import Optional

def get_email_template(
    action: str,
    task_name: str,
    task_id: str,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    assignee_name: Optional[str] = None,
    due_date: Optional[str] = None,
    description: Optional[str] = None,
    clickup_url: Optional[str] = None
) -> tuple[str, str]:
    """
    Generar plantilla HTML para email de notificacion
    
    Returns:
        tuple: (subject, html_body)
    """
    
    # Mapear acciones a emojis y colores
    action_config = {
        "created": {"emoji": "üÜï", "color": "#28a745", "text": "Nueva tarea creada"},
        "updated": {"emoji": "‚úèÔ∏è", "color": "#ffc107", "text": "Tarea actualizada"},
        "deleted": {"emoji": "üóëÔ∏è", "color": "#dc3545", "text": "Tarea eliminada"},
    }
    
    config = action_config.get(action, {"emoji": "üìã", "color": "#6c757d", "text": "Notificacion de tarea"})
    
    # Mapear prioridad a colores
    priority_config = {
        1: {"text": "Urgente", "color": "#dc3545", "emoji": "üî¥"},
        2: {"text": "Alta", "color": "#fd7e14", "emoji": "üü†"},
        3: {"text": "Normal", "color": "#ffc107", "emoji": "üü°"},
        4: {"text": "Baja", "color": "#28a745", "emoji": "üü¢"},
    }
    
    priority_info = priority_config.get(priority, {"text": "No especificada", "color": "#6c757d", "emoji": "‚ö™"})
    
    # Subject
    subject = f"{config['emoji']} {config['text']}: {task_name}"
    
    # URL de ClickUp
    if not clickup_url:
        clickup_url = f"https://app.clickup.com/t/{task_id}"
    
    # HTML Body
    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .email-container {{
                background-color: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid {config['color']};
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: {config['color']};
                margin: 0;
                font-size: 28px;
            }}
            .task-info {{
                background-color: #f8f9fa;
                border-left: 4px solid {config['color']};
                padding: 20px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }}
            .task-name {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .task-id {{
                font-family: 'Courier New', monospace;
                background-color: #e9ecef;
                padding: 5px 10px;
                border-radius: 4px;
                display: inline-block;
                margin: 10px 0;
            }}
            .metadata {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 20px 0;
            }}
            .metadata-item {{
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border-left: 3px solid {config['color']};
            }}
            .metadata-label {{
                font-weight: bold;
                color: #6c757d;
                font-size: 12px;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}
            .metadata-value {{
                color: #2c3e50;
                font-size: 14px;
            }}
            .description {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin: 20px 0;
                border-left: 3px solid #6c757d;
            }}
            .cta-button {{
                display: inline-block;
                background-color: {config['color']};
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
                margin: 20px 0;
                text-align: center;
                transition: background-color 0.3s;
            }}
            .cta-button:hover {{
                opacity: 0.9;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
                font-size: 14px;
            }}
            .priority-badge {{
                display: inline-block;
                background-color: {priority_info['color']};
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            @media (max-width: 600px) {{
                .metadata {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>{config['emoji']} {config['text']}</h1>
            </div>
            
            <div class="task-info">
                <div class="task-name">{task_name}</div>
                <div class="task-id">ID: {task_id}</div>
            </div>
    """
    
    # Metadata section
    html_body += '<div class="metadata">'
    
    if status:
        html_body += f'''
            <div class="metadata-item">
                <div class="metadata-label">üìä Estado</div>
                <div class="metadata-value">{status}</div>
            </div>
        '''
    
    if priority is not None:
        html_body += f'''
            <div class="metadata-item">
                <div class="metadata-label">{priority_info['emoji']} Prioridad</div>
                <div class="metadata-value">
                    <span class="priority-badge" style="background-color: {priority_info['color']}">{priority_info['text']}</span>
                </div>
            </div>
        '''
    
    if assignee_name:
        html_body += f'''
            <div class="metadata-item">
                <div class="metadata-label">üë§ Asignado a</div>
                <div class="metadata-value">{assignee_name}</div>
            </div>
        '''
    
    if due_date:
        html_body += f'''
            <div class="metadata-item">
                <div class="metadata-label">‚è∞ Fecha limite</div>
                <div class="metadata-value">{due_date}</div>
            </div>
        '''
    
    html_body += '</div>'
    
    # Description
    if description:
        html_body += f'''
            <div class="description">
                <div class="metadata-label">üìù Descripcion</div>
                <div style="margin-top: 10px;">{description}</div>
            </div>
        '''
    
    # CTA Button
    html_body += f'''
            <div style="text-align: center;">
                <a href="{clickup_url}" class="cta-button">
                    üîó Abrir en ClickUp
                </a>
            </div>
            
            <div class="footer">
                <p>üì± Notificacion automatica del Sistema de Gestion de Tareas ClickUp</p>
                <p>ü§ñ Este email fue generado automaticamente, no responder.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return subject, html_body


def get_summary_email_template(
    notifications_sent: int,
    successful_emails: int,
    successful_sms: int,
    successful_telegram: int,
    failed_notifications: int,
    time_period: str = "ultimas 24 horas"
) -> tuple[str, str]:
    """
    Plantilla para email de resumen de notificaciones
    """
    
    subject = f"üìä Resumen de notificaciones - {notifications_sent} enviadas"
    
    success_rate = (successful_emails + successful_sms + successful_telegram) / max(notifications_sent, 1) * 100
    
    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .email-container {{
                background-color: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #007bff;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-card {{
                text-align: center;
                padding: 20px;
                border-radius: 8px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .stat-number {{
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 12px;
                text-transform: uppercase;
                opacity: 0.9;
            }}
            .success-rate {{
                text-align: center;
                margin: 30px 0;
                padding: 20px;
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                border-radius: 10px;
                color: white;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>üìä Resumen de Notificaciones</h1>
                <p>Statistics for las {time_period}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                    <div class="stat-number">{successful_emails}</div>
                    <div class="stat-label">üìß Emails</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);">
                    <div class="stat-number">{successful_sms}</div>
                    <div class="stat-label">üì± SMS</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #007bff 0%, #6610f2 100%);">
                    <div class="stat-number">{successful_telegram}</div>
                    <div class="stat-label">üí¨ Telegram</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);">
                    <div class="stat-number">{failed_notifications}</div>
                    <div class="stat-label">‚ùå Fallos</div>
                </div>
            </div>
            
            <div class="success-rate">
                <h2 style="margin: 0;">‚úÖ Tasa de Exito</h2>
                <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">{success_rate:.1f}%</div>
                <p style="margin: 0;">De {notifications_sent} notificaciones enviadas</p>
            </div>
            
            <div class="footer">
                <p>ü§ñ Resumen automatico del Sistema de Gestion de Tareas ClickUp</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_body
