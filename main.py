from fastapi import FastAPI, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import markdown

app = FastAPI()

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LessonRequest(BaseModel):
    data: dict


# =========================================================
# GENERAR PDF PRINCIPAL
# =========================================================
@app.post("/generate-pdf")
def generate_pdf(req: LessonRequest):

    session = req.data

    # ------------------------------------------------------
    # Fichas de Trabajo
    # ------------------------------------------------------
    fichas_html = "".join(
        (
            "<div class='label'>" + f["titulo"] + "</div>"
            "<div class='box'>" + f["instrucciones"] + "</div>"
            "<ul>"
            + "".join("<li>" + e + "</li>" for e in f["ejercicios"])
            + "</ul>"
        )
        for f in session["recursosAdicionales"]["fichasDeTrabajo"]
    )

    # ------------------------------------------------------
    # Problemas y ejercicios
    # ------------------------------------------------------
    problemas_html = "".join(
        (
            "<div class='box'>"
            "<b>Problema:</b> " + p.get("enunciado", "---") + "<br>"
            "<b>Respuesta:</b> " + p.get("respuesta", "---") + "<br>"
            "<b>Criterios:</b> " + p.get("criterios", "---") +
            "</div>"
        )
        for p in session.get("recursosAdicionales", {}).get("problemasYEjercicios", [])
    )


    # ------------------------------------------------------
    # Actividad de activación
    # ------------------------------------------------------
    activacion_html = "".join(
        (
            "<div class='box'>"
            "<b>" + a.get("nombre", "---") + "</b><br>"
            + a.get("descripcion", "---") + "<br>"
            "<i>Duración: " + a.get("duracion", "---") + "</i>"
            "</div>"
        )
        for a in session.get("recursosAdicionales", {}).get("actividadDeActivacion", [])
    )


    # ------------------------------------------------------
    # Evaluación formativa
    # ------------------------------------------------------
    evaluacion_html = "".join(
        (
            "<div class='box'>"
            "<b>" + q["enunciado"] + "</b><br>"
            "Respuesta: " + q["respuesta"] + "<br>"
            "Criterios: " + q["criterios"] +
            "</div>"
        )
        for q in session["recursosAdicionales"]["evaluacionFormativa"]["preguntas"]
    )

    # ------------------------------------------------------
    # Actividades diferenciadas
    # ------------------------------------------------------
    refuerzo_html = "".join("<li>" + r + "</li>" for r in session["recursosAdicionales"]["actividadesDiferenciadas"]["refuerzo"])
    consolidacion_html = "".join("<li>" + c + "</li>" for c in session["recursosAdicionales"]["actividadesDiferenciadas"]["consolidacion"])
    profundizacion_html = "".join("<li>" + p + "</li>" for p in session["recursosAdicionales"]["actividadesDiferenciadas"]["profundizacion"])

    # ------------------------------------------------------
    # Juego Didáctico
    # ------------------------------------------------------
    juego = session["recursosAdicionales"]["juegoDidactico"]
    juego_html = (
        "<div class='box'>"
        "<b>" + juego["nombre"] + "</b><br><br>"
        + juego["descripcion"] + "<br><br>"
        "<b>Materiales:</b> " + juego["materiales"] + "<br>"
        "<b>Instrucciones:</b> " + juego["instrucciones"] + "<br><br>"
        "<b>Niveles de dificultad:</b>"
        "<ul>" + "".join("<li>" + n + "</li>" for n in juego["nivelesDificultad"]) + "</ul>"
        "<b>Reflexión:</b> " + juego["reflexion"] +
        "</div>"
    )

    # ------------------------------------------------------
    # HTML PRINCIPAL
    # ------------------------------------------------------
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
    .footer {{ text-align: center; color: #888; font-size: 0.95em; margin-top: 2.5em; }}
</style>
</head>
<body>

<div class='container'>
    <h1>📝 SESIÓN DE APRENDIZAJE</h1>

    <div class='section'>
        <h2>📌 Datos Generales</h2>
        <div class='label'>Título</div>
        <div class='box'>{session['datosGenerales']['titulo']}</div>
        <div class='label'>Docente</div>
        <div class='box'>{session['datosGenerales']['docente']}</div>
        <div class='label'>Grado y sección</div>
        <div class='box'>{session['datosGenerales']['grado']} {session['datosGenerales']['seccion']}</div>
        <div class='label'>Fecha</div>
        <div class='box'>{session['datosGenerales']['fecha']}</div>

        <div class='label'>Tema</div>
        <div class='box'>{session['tema']}</div>

        <div class='label'>Ciclo</div>
        <div class='box'>{session['ciclo']}</div>

        <div class='label'>Contexto</div>
        <div class='box'>{session['contexto']}</div>

        <div class='label'>Horas de clase</div>
        <div class='box'>{session['horasClase']}</div>
    </div>

    <div class='section'>
        <h2>🎯 Competencias</h2>
        <div class='label'>Competencias seleccionadas</div>
        <ul>
            {''.join('<li>' + c + '</li>' for c in session['competenciasSeleccionadas'])}
        </ul>
        <div class='label'>Capacidades</div>
        <ul>
            {''.join('<li>' + c + '</li>' for c in session['capacidades'])}
        </ul>
        <div class='label'>Enfoque transversal</div>
        <div class='box'>{session['enfoqueTransversal']}</div>
        <div class='label'>Competencia transversal</div>
        <div class='box'>{session['competenciaTransversal']}</div>
        <div class='label'>Descripción</div>
        <div class='box'>{session['competenciaDescripcion']}</div>
    </div>

    <div class='section'>
        <h2>🧩 Criterios de evaluación</h2>
        <ul>
            {''.join('<li>' + x.strip() + '</li>' for x in session['criteriosEvaluacion'].split(' 2. '))}
        </ul>
    </div>

    <div class='section'>
        <h2>📄 Evidencias de aprendizaje</h2>
        <ul>
            {''.join('<li>' + x.strip() + '</li>' for x in session['evidenciasAprendizaje'].split(' 2. '))}
        </ul>
    </div>

    <div class='section'>
        <h2>🎯 Propósito de la sesión</h2>
        <div class='box'>{session['propositoSesion']}</div>
    </div>

    <div class='section'>
        <h2>✏️ Materiales</h2>
        <div class='label'>Materiales disponibles</div>
        <div class='box'>{session['materialesDisponibles']}</div>
        <div class='label'>Materiales didácticos sugeridos</div>
        <ul>
            {''.join('<li>' + m + '</li>' for m in session['materialesDidacticosSugeridos'])}
        </ul>
    </div>

    <div class='section'>
        <h2>⏱️ Momentos de la sesión</h2>
        <div class='box'>{session['distribucionHoras']}</div>
        <h3>Inicio</h3>
        <div class='box'>{session['secuenciaMetodologica']['inicio']}</div>
        <h3>Desarrollo</h3>
        <div class='box'>{session['secuenciaMetodologica']['desarrollo']}</div>
        <h3>Cierre</h3>
        <div class='box'>{session['secuenciaMetodologica']['cierre']}</div>
    </div>

    <div class='section'>
        <h2>🔄 Procesos Didácticos</h2>
        <ul>{''.join('<li>' + p + '</li>' for p in session['procesosDidacticos'])}</ul>
    </div>

    <div class='section'>
        <h2>✨ Actividades Contextualizadas</h2>
        <ul>{''.join('<li>' + a + '</li>' for a in session['actividadesContextualizadas'])}</ul>
    </div>

    <div class='section'>
        <h2>📚 Recursos Adicionales</h2>
        <h3>Fichas de Trabajo</h3>
        {fichas_html}

        <h3>Problemas y Ejercicios</h3>
        {problemas_html}

        <h3>Juego Didáctico</h3>
        {juego_html}
    </div>

    <div class='section'>
        <h2>⚡ Actividades de Activación</h2>
        {activacion_html}
    </div>

    <div class='section'>
        <h2>📝 Evaluación Formativa</h2>
        {evaluacion_html}
        <div class='label'>Criterios Generales</div>
        <div class='box'>{session['recursosAdicionales']['evaluacionFormativa']['criteriosGenerales']}</div>
    </div>

    <div class='section'>
        <h2>🎓 Actividades Diferenciadas</h2>
        <h3>Refuerzo</h3>
        <ul>{refuerzo_html}</ul>

        <h3>Consolidación</h3>
        <ul>{consolidacion_html}</ul>

        <h3>Profundización</h3>
        <ul>{profundizacion_html}</ul>
    </div>

    <div class='section'>
        <h2>📢 Comunicado para Padres</h2>
        <div class='box'>{session['recursosAdicionales']['comunicadoParaPadres']}</div>
    </div>

    <div class='footer'>Documento generado automáticamente | Sesión de Aprendizaje</div>

</div>
</body>
</html>
"""

    # ------------------------------------------------------
    # GENERAR PDF
    # ------------------------------------------------------
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4")
        browser.close()

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
