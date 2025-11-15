from fastapi import FastAPI, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import json
import markdown

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

class LessonRequest(BaseModel):
    data: dict   # aquí viene tu JSON de sesión AI

@app.post("/generate-pdf")
def generate_pdf(req: LessonRequest):

    session = req.data

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>Sesión de Aprendizaje</title>
<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap' rel='stylesheet'>
<style>
    body {{ font-family: 'Inter', 'Segoe UI', sans-serif; background: #f6f8fa; color: #222; }}
    .container {{ max-width: 900px; margin: 30px auto; background: #fff; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); padding: 40px 50px; }}
    h1, h2, h3 {{ font-family: 'Poppins', sans-serif; }}
    h1 {{ font-size: 2.2em; margin-bottom: 0.2em; }}
    h2 {{ font-size: 1.4em; margin-top: 2em; margin-bottom: 0.7em; border-bottom: 2px solid #667eea; padding-bottom: 0.2em; }}
    h3 {{ font-size: 1.1em; margin-top: 1.2em; margin-bottom: 0.5em; color: #764ba2; }}
    .section {{ margin-bottom: 2.2em; }}
    .label {{ font-weight: 600; color: #667eea; font-size: 0.98em; margin-top: 0.7em; }}
    ul, ol {{ margin-left: 1.5em; }}
    .box {{ background: #f5f7fa; border-left: 4px solid #667eea; border-radius: 7px; padding: 15px 18px; margin-bottom: 1em; }}
    .tag {{ display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border-radius: 16px; padding: 5px 15px; margin: 2px 6px 2px 0; font-size: 0.95em; }}
    .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 1.5em; }}
    .info-table td, .info-table th {{ border: 1px solid #e2e8f0; padding: 7px 12px; }}
    .info-table th {{ background: #f0f4ff; color: #667eea; font-weight: 600; }}
    .footer {{ text-align: center; color: #888; font-size: 0.95em; margin-top: 2.5em; }}
</style>
</head>
<body>
<div class='container'>
    <h1>📝 SESIÓN DE APRENDIZAJE</h1>
    <div class='section'>
        <h2>📌 Título de la sesión</h2>
        <div class='box'>{session.get('datosGenerales',{}).get('titulo','')}</div>
        <div class='label'>Docente</div>
        <div class='box'>{session.get('datosGenerales',{}).get('docente','')}</div>
        <div class='label'>Grado y sección</div>
        <div class='box'>{session.get('datosGenerales',{}).get('grado','')} {session.get('datosGenerales',{}).get('seccion','')}</div>
        <div class='label'>Fecha</div>
        <div class='box'>{session.get('datosGenerales',{}).get('fecha','')}</div>
    </div>
    <div class='section'>
        <h2>🎯 Competencias y capacidades</h2>
        <div class='label'>Competencia</div>
        <div class='box'>{session.get('competenciasSeleccionadas',[''])[0]}</div>
        <div class='label'>Capacidades</div>
        <ul>
            {''.join(f'<li>{c}</li>' for c in session.get('capacidades',[]))}
        </ul>
    </div>
    <div class='section'>
        <h2>🧩 Criterios de evaluación</h2>
        <ul>
            {''.join(f'<li>{crit.strip()}</li>' for crit in str(session.get('criteriosEvaluacion','')).split(' 1. ')[-1].split(' 2. ') if crit)}
        </ul>
    </div>
    <div class='section'>
        <h2>📄 Evidencias de aprendizaje</h2>
        <ul>
            {''.join(f'<li>{ev.strip()}</li>' for ev in str(session.get('evidenciasAprendizaje','')).split(' 1. ')[-1].split(' 2. ') if ev)}
        </ul>
    </div>
    <div class='section'>
        <h2>🎯 Propósito de la sesión</h2>
        <div class='box'>{session.get('propositoSesion','')}</div>
    </div>
    <div class='section'>
        <h2>✏️ Materiales para el desarrollo de la sesión</h2>
        <div class='label'>Materiales para la sesión</div>
        <div class='box'>{session.get('materialesDisponibles','')}</div>
        <div class='label'>Materiales didácticos sugeridos</div>
        <ul>
            {''.join(f'<li>{m}</li>' for m in session.get('materialesDidacticosSugeridos',[]))}
        </ul>
    </div>
    <div class='section'>
        <h2>⏱️ MOMENTOS DE LA SESIÓN</h2>
        <div class='label'>Distribución temporal</div>
        <div class='box'>{session.get('distribucionHoras','')}</div>
        <h3>🔹 Inicio</h3>
        <div class='box'>{session.get('secuenciaMetodologica',{}).get('inicio','')}</div>
        <h3>🔹 Desarrollo</h3>
        <div class='box'>{session.get('secuenciaMetodologica',{}).get('desarrollo','')}</div>
        <h3>🔹 Cierre</h3>
        <div class='box'>{session.get('secuenciaMetodologica',{}).get('cierre','')}</div>
    </div>
    <div class='section'>
        <h2>🔄 Procesos Didácticos</h2>
        <ul>
            {''.join(f'<li>{p}</li>' for p in session.get('procesosDidacticos',[]))}
        </ul>
    </div>
    <div class='section'>
        <h2>✨ Actividades Contextualizadas</h2>
        <ul>
            {''.join(f'<li>{a}</li>' for a in session.get('actividadesContextualizadas',[]))}
        </ul>
    </div>
    <div class='footer'>Documento generado automáticamente | Sesión de Aprendizaje</div>
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


def _wrap_with_template(content_html: str, title: str = "Sesión de Aprendizaje") -> str:
    # Reutiliza los estilos definidos en la plantilla principal y coloca el HTML convertido
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
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
        margin: 40px auto;
        background: white;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        border-radius: 12px;
        overflow: hidden;
    }}

    .header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px 40px;
    }}

    h1 {{
        font-family: 'Poppins', sans-serif;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 6px;
    }}

    .content {{
        padding: 30px 40px;
        color: #2d3748;
    }}

    .footer {{
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: white;
        padding: 20px 40px;
        text-align: center;
        font-size: 13px;
        opacity: 0.9;
    }}

    img {{ max-width: 100%; }}
    pre {{ background: #f4f4f4; padding: 12px; border-radius: 6px; overflow: auto; }}
    table {{ border-collapse: collapse; width: 100%; }}
    table, th, td {{ border: 1px solid #ddd; padding: 8px; }}

    @media print {{
        body {{ background: white; }}
        .container {{ box-shadow: none; }}
    }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📚 {title}</h1>
    </div>
    <div class="content">
        {content_html}
    </div>
    <div class="footer">
        <p>📄 Documento generado automáticamente</p>
    </div>
</div>
</body>
</html>
"""


@app.post("/generate-pdf-from-md")
async def generate_pdf_from_md(file: UploadFile = File(None), markdown_text: str = Form(None)):
    """Genera un PDF a partir de un archivo .md subido o de texto Markdown en el formulario.

    - Envíe `file` como multipart/form-data con el archivo .md, o
    - Envíe `markdown_text` como campo de formulario con el contenido Markdown.
    """

    if file is not None:
        raw = await file.read()
        try:
            md = raw.decode('utf-8')
        except Exception:
            md = raw.decode('latin-1')
    elif markdown_text:
        md = markdown_text
    else:
        return {"error": "No se proporcionó ningún Markdown (archivo o campo 'markdown_text')."}

    # Convertir Markdown a HTML (extensiones útiles)
    content_html = markdown.markdown(md, extensions=["fenced_code", "tables", "toc"])

    html = _wrap_with_template(content_html)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4")
        browser.close()

    return Response(content=pdf_bytes, media_type="application/pdf")
