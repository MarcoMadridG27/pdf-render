from fastapi import FastAPI, Response
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import json

app = FastAPI()

class LessonRequest(BaseModel):
    data: dict   # aquí viene tu JSON de sesión AI

@app.post("/generate-pdf")
def generate_pdf(req: LessonRequest):

    session = req.data

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Sesión de Aprendizaje</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        padding: 0;
        line-height: 1.7;
        color: #1a1a1a;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}

    .container {{
        max-width: 1100px;
        margin: 0 auto;
        background: white;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }}

    .header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 50px 60px;
        position: relative;
        overflow: hidden;
    }}

    .header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }}

    .header::after {{
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }}

    h1 {{
        font-family: 'Poppins', sans-serif;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 15px;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        letter-spacing: -0.5px;
    }}

    .subtitle {{
        font-size: 18px;
        font-weight: 300;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        font-style: italic;
    }}

    .content {{
        padding: 50px 60px;
    }}

    .info-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
        margin-bottom: 40px;
    }}

    .info-card {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}

    .info-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }}

    .info-label {{
        font-family: 'Poppins', sans-serif;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #667eea;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }}

    .info-label::before {{
        content: '';
        width: 4px;
        height: 16px;
        background: #667eea;
        margin-right: 10px;
        border-radius: 2px;
    }}

    .info-value {{
        font-size: 15px;
        color: #2d3748;
        font-weight: 400;
        line-height: 1.6;
    }}

    .section {{
        margin-bottom: 45px;
        page-break-inside: avoid;
    }}

    h2 {{
        font-family: 'Poppins', sans-serif;
        font-size: 28px;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #667eea, #764ba2) 1;
        display: flex;
        align-items: center;
    }}

    h2::before {{
        content: '';
        width: 8px;
        height: 35px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        margin-right: 15px;
        border-radius: 4px;
    }}

    h3 {{
        font-family: 'Poppins', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: #4a5568;
        margin-top: 30px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }}

    h3::before {{
        content: '◆';
        color: #667eea;
        margin-right: 12px;
        font-size: 16px;
    }}

    .box {{
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-left: 5px solid #667eea;
        padding: 22px 25px;
        margin-bottom: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: 15px;
        line-height: 1.8;
        transition: all 0.3s ease;
    }}

    .box:hover {{
        border-left-color: #764ba2;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}

    .tag-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }}

    .tag {{
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .tag:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
    }}

    .tag::before {{
        content: '✓';
        margin-right: 8px;
        font-weight: bold;
    }}

    ul {{
        margin-left: 25px;
        margin-top: 15px;
    }}

    ul li {{
        margin-bottom: 12px;
        padding-left: 15px;
        position: relative;
        font-size: 15px;
        line-height: 1.7;
        color: #2d3748;
    }}

    ul li::before {{
        content: '▸';
        position: absolute;
        left: -10px;
        color: #667eea;
        font-weight: bold;
        font-size: 18px;
    }}

    .highlight-box {{
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-left: 5px solid #fdcb6e;
        padding: 20px 25px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(253, 203, 110, 0.3);
    }}

    .duration-badge {{
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #00b894, #00cec9);
        color: white;
        padding: 12px 25px;
        border-radius: 30px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
    }}

    .duration-badge::before {{
        content: '⏱';
        margin-right: 10px;
        font-size: 20px;
    }}

    .footer {{
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: white;
        padding: 30px 60px;
        text-align: center;
        font-size: 14px;
        opacity: 0.9;
    }}

    .metodologia-container {{
        background: linear-gradient(135deg, #f8f9ff 0%, #e8eaff 100%);
        border-radius: 15px;
        padding: 30px;
        margin-top: 20px;
        border: 2px solid #667eea;
    }}

    .fase-box {{
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }}

    .fase-box:last-child {{
        margin-bottom: 0;
    }}

    @media print {{
        body {{
            background: white;
        }}
        .container {{
            box-shadow: none;
        }}
    }}
</style>

</head>
<body>

<div class="container">
    <div class="header">
        <h1>📚 Sesión de Aprendizaje</h1>
        <div class="subtitle">Planificación Pedagógica Detallada</div>
    </div>

    <div class="content">
        <!-- Sección: Información General -->
        <div class="section">
            <h2>📋 Información General</h2>
            
            <div class="info-grid">
                <div class="info-card">
                    <div class="info-label">Tema de la Sesión</div>
                    <div class="info-value">{session.get("tema", "")}</div>
                </div>
                
                <div class="info-card">
                    <div class="info-label">Ciclo Educativo</div>
                    <div class="info-value">{session.get("ciclo", "")}</div>
                </div>
            </div>

            <div class="info-card" style="margin-bottom: 25px;">
                <div class="info-label">Contexto del Aula</div>
                <div class="info-value">{session.get("contexto", "")}</div>
            </div>

            <div class="highlight-box">
                <div class="info-label" style="color: #d63031; margin-bottom: 10px;">⏱ Duración de la Sesión</div>
                <span class="duration-badge">{session.get("horasClase", 2)} horas pedagógicas</span>
            </div>
        </div>

        <!-- Sección: Competencias -->
        <div class="section">
            <h2>🎯 Competencias y Capacidades</h2>
            
            <div class="info-label" style="margin-bottom: 15px;">Competencias Seleccionadas</div>
            <div class="tag-container">
                {''.join(f'<span class="tag">{c}</span>' for c in session.get("competenciasSeleccionadas", []))}
            </div>

            <div style="margin-top: 25px;">
                <div class="info-label">Descripción de la Competencia</div>
                <div class="box">{session.get("competenciaDescripcion", "")}</div>
            </div>
        </div>

        <!-- Sección: Secuencia Metodológica -->
        <div class="section">
            <h2>📖 Secuencia Metodológica</h2>
            
            <div class="metodologia-container">
                <h3>🚀 Inicio</h3>
                <div class="fase-box">{session["secuenciaMetodologica"]["inicio"]}</div>

                <h3>⚙️ Desarrollo</h3>
                <div class="fase-box">{session["secuenciaMetodologica"]["desarrollo"]}</div>

                <h3>✅ Cierre</h3>
                <div class="fase-box">{session["secuenciaMetodologica"]["cierre"]}</div>
            </div>

            <div class="highlight-box" style="margin-top: 25px;">
                <div class="info-label" style="color: #d63031;">📊 Distribución Temporal</div>
                <div class="info-value" style="font-weight: 500; font-size: 16px; margin-top: 10px;">{session.get("distribucionHoras", "")}</div>
            </div>
        </div>

        <!-- Sección: Procesos Didácticos -->
        <div class="section">
            <h2>🔄 Procesos Didácticos</h2>
            <div class="box">
                <ul style="margin: 0;">
                    {''.join(f'<li>{p}</li>' for p in session.get("procesosDidacticos", []))}
                </ul>
            </div>
        </div>

        <!-- Sección: Materiales -->
        <div class="section">
            <h2>🎨 Recursos y Materiales</h2>
            
            <div class="info-label">Materiales Disponibles</div>
            <div class="box">{session.get("materialesDisponibles", "")}</div>

            <div class="info-label" style="margin-top: 25px;">Materiales Didácticos Sugeridos</div>
            <div class="box">
                <ul style="margin: 0;">
                    {''.join(f'<li>{m}</li>' for m in session.get("materialesDidacticosSugeridos", []))}
                </ul>
            </div>
        </div>

        <!-- Sección: Actividades -->
        <div class="section">
            <h2>✨ Actividades Contextualizadas</h2>
            <div class="box">
                <ul style="margin: 0;">
                    {''.join(f'<li>{a}</li>' for a in session.get("actividadesContextualizadas", []))}
                </ul>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>📄 Documento generado automáticamente | Sesión de Aprendizaje {session.get("ciclo", "")}</p>
    </div>
</div>

</body>
</html>
"""

    # ✅ Convertir a PDF con Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4")
        browser.close()

    return Response(content=pdf_bytes, media_type="application/pdf")
