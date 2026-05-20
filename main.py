from fastapi import FastAPI, Response, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import markdown
import os
import tempfile
import traceback
from sesion_template import generate_sesion

app = FastAPI()

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Handler global: garantiza CORS headers incluso en errores 500
# ---------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"[ERROR 500]\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb},
        headers={"Access-Control-Allow-Origin": "*"},
    )

class LessonRequest(BaseModel):
    data: dict

def map_data(data: dict) -> dict:
    """Mapea los datos del JSON antiguo al nuevo formato si es necesario."""
    new_data = dict(data)
    
    if "datosGenerales" in data:
        dg = data["datosGenerales"]
        new_data["ie"] = dg.get("ie", new_data.get("ie", ""))
        new_data["docente"] = dg.get("docente", new_data.get("docente", ""))
        new_data["grado"] = dg.get("grado", new_data.get("grado", ""))
        new_data["seccion"] = dg.get("seccion", new_data.get("seccion", ""))
        new_data["fecha"] = dg.get("fecha", new_data.get("fecha", ""))
        new_data["titulo"] = dg.get("titulo", new_data.get("titulo", ""))

    if "tema" in data and not new_data.get("titulo"):
        new_data["titulo"] = data["tema"]
        
    if "ciclo" in data and not new_data.get("ciclo"):
        new_data["ciclo"] = data["ciclo"]
        
    if "horasClase" in data and not new_data.get("duracion"):
        new_data["duracion"] = data["horasClase"]
        
    if "propositoSesion" in data and not new_data.get("proposito_aprendizaje"):
        new_data["proposito_aprendizaje"] = data["propositoSesion"]
        
    if "enfoqueTransversal" in data and not new_data.get("enfoque_transversal"):
        new_data["enfoque_transversal"] = data["enfoqueTransversal"]
        
    if "competenciasSeleccionadas" in data and not new_data.get("competencias"):
        new_data["competencias"] = [{"competencia": c, "capacidades": data.get("capacidades", [])} for c in data["competenciasSeleccionadas"]]
        
    if "criteriosEvaluacion" in data and isinstance(data["criteriosEvaluacion"], str) and not new_data.get("criterios_evaluacion"):
        import re
        criterios = re.split(r'\s*\d+\.\s*', data["criteriosEvaluacion"])
        new_data["criterios_evaluacion"] = [c.strip() for c in criterios if c.strip()]
        
    if "evidenciasAprendizaje" in data and isinstance(data["evidenciasAprendizaje"], str) and not new_data.get("evidencia"):
        new_data["evidencia"] = data["evidenciasAprendizaje"]
        
    if "materialesDidacticosSugeridos" in data and not new_data.get("recursos_materiales"):
        new_data["recursos_materiales"] = data["materialesDidacticosSugeridos"]
        
    if "secuenciaMetodologica" in data:
        sm = data["secuenciaMetodologica"]
        if "inicio" in sm and isinstance(sm["inicio"], str) and not new_data.get("inicio"):
            new_data["inicio"] = [{"tipo": "texto", "texto": sm["inicio"]}]
        if "desarrollo" in sm and isinstance(sm["desarrollo"], str) and not new_data.get("desarrollo"):
            new_data["desarrollo"] = [{"tipo": "texto", "texto": sm["desarrollo"]}]
        if "cierre" in sm and isinstance(sm["cierre"], str) and not new_data.get("cierre"):
            new_data["cierre"] = [{"tipo": "texto", "texto": sm["cierre"]}]

    if "recursosAdicionales" in data:
        ra = data["recursosAdicionales"]
        if "instrumentoEvaluacionGenerado" in ra and not new_data.get("instrumento_evaluacion_generado"):
            new_data["instrumento_evaluacion_generado"] = ra["instrumentoEvaluacionGenerado"]

    return new_data

# =========================================================
# GENERAR PDF PRINCIPAL
# =========================================================
@app.post("/generate-pdf")
def generate_pdf(req: LessonRequest):
    # Map the incoming data in case it's using the old format
    mapped_data = map_data(req.data)
    
    # Generate random temp file
    fd, output_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    try:
        # Usar la nueva plantilla de sesión
        generate_sesion(mapped_data, output_path)
        
        with open(output_path, "rb") as f:
            pdf_bytes = f.read()
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[generate_pdf ERROR]\n{tb}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "traceback": tb},
            headers={"Access-Control-Allow-Origin": "*"},
        )
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)
            
    return Response(content=pdf_bytes, media_type="application/pdf")

# =========================================================
# PDF desde Markdown
# =========================================================
def _wrap_with_template(content_html: str, title: str = "Sesión de Aprendizaje") -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body>
{content_html}
</body>
</html>
"""

@app.post("/generate-pdf-from-md")
async def generate_pdf_from_md(file: UploadFile = File(None), markdown_text: str = Form(None)):

    if file:
        raw = await file.read()
        try:
            md = raw.decode("utf-8")
        except:
            md = raw.decode("latin-1")
    else:
        md = markdown_text or ""

    html = _wrap_with_template(
        markdown.markdown(md, extensions=["fenced_code", "tables", "toc"])
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4")
        browser.close()

    return Response(content=pdf_bytes, media_type="application/pdf")
