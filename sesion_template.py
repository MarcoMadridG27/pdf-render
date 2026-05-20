"""
MICROSERVICIO: Generador de Sesión de Aprendizaje - MINEDU Perú
Uso: python sesion_template.py  →  genera sesion_aprendizaje.pdf
Para microservicio: llamar a generate_sesion(data, output_path)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

# ─── PALETA ───────────────────────────────────────────────────────────────────
AZUL_HEADER  = colors.HexColor("#1565C0")   # azul oscuro títulos
AZUL_MED     = colors.HexColor("#1976D2")   # azul medio
AZUL_CLARO   = colors.HexColor("#BBDEFB")   # azul claro fondo cabecera
AZUL_PALIDO  = colors.HexColor("#E3F2FD")   # azul muy claro fondo alterno
GRIS_LINEA   = colors.HexColor("#90A4AE")   # gris para bordes
GRIS_FONDO   = colors.HexColor("#F5F5F5")   # gris claro fondo
NEGRO        = colors.HexColor("#212121")
GRIS_TEXTO   = colors.HexColor("#424242")
BLANCO       = colors.white

W_PAGE = A4[0] - 3.6*cm   # ancho útil

# ─── ESTILOS ──────────────────────────────────────────────────────────────────
def estilos():
    E = {}
    E['doc_title'] = ParagraphStyle('doc_title',
        fontName='Helvetica-Bold', fontSize=13, textColor=AZUL_HEADER,
        leading=16, alignment=TA_CENTER, spaceAfter=2)
    E['section_header'] = ParagraphStyle('section_header',
        fontName='Helvetica-Bold', fontSize=9, textColor=BLANCO,
        leading=11, alignment=TA_LEFT)
    E['field_label'] = ParagraphStyle('field_label',
        fontName='Helvetica-Bold', fontSize=8.5, textColor=AZUL_HEADER,
        leading=11)
    E['field_value'] = ParagraphStyle('field_value',
        fontName='Helvetica', fontSize=9, textColor=NEGRO,
        leading=13)
    E['field_value_bold'] = ParagraphStyle('field_value_bold',
        fontName='Helvetica-Bold', fontSize=9, textColor=NEGRO,
        leading=13)
    E['cell_header'] = ParagraphStyle('cell_header',
        fontName='Helvetica-Bold', fontSize=8.5, textColor=BLANCO,
        leading=11, alignment=TA_CENTER)
    E['cell_body'] = ParagraphStyle('cell_body',
        fontName='Helvetica', fontSize=8.5, textColor=GRIS_TEXTO,
        leading=12, alignment=TA_JUSTIFY)
    E['cell_body_bold'] = ParagraphStyle('cell_body_bold',
        fontName='Helvetica-Bold', fontSize=8.5, textColor=NEGRO,
        leading=12)
    E['bullet'] = ParagraphStyle('bullet',
        fontName='Helvetica', fontSize=8.5, textColor=GRIS_TEXTO,
        leading=12, leftIndent=10, firstLineIndent=-8)
    E['momento'] = ParagraphStyle('momento',
        fontName='Helvetica-Bold', fontSize=9, textColor=AZUL_HEADER,
        leading=12, spaceBefore=4)
    E['actividad'] = ParagraphStyle('actividad',
        fontName='Helvetica', fontSize=8.5, textColor=GRIS_TEXTO,
        leading=12, alignment=TA_JUSTIFY)
    E['actividad_bold'] = ParagraphStyle('actividad_bold',
        fontName='Helvetica-Bold', fontSize=8.5, textColor=NEGRO, leading=12)
    E['footer'] = ParagraphStyle('footer',
        fontName='Helvetica', fontSize=7.5, textColor=GRIS_LINEA,
        leading=10, alignment=TA_CENTER)
    E['titulo_sesion_label'] = ParagraphStyle('tsl',
        fontName='Helvetica-Bold', fontSize=9, textColor=AZUL_HEADER, leading=12)
    E['titulo_sesion_value'] = ParagraphStyle('tsv',
        fontName='Helvetica-Bold', fontSize=11, textColor=NEGRO,
        leading=14, alignment=TA_CENTER)
    return E

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def section_bar(text, E, width=None):
    """Barra de sección azul oscuro con texto blanco."""
    W = width or W_PAGE
    t = Table([[Paragraph(text, E['section_header'])]], colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AZUL_HEADER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def empty_lines(n=1):
    """Celdas vacías para que el docente complete a mano si imprime."""
    return "\n".join(["_" * 80] * n)

def bullet_list(items, E):
    """Lista de párrafos con viñeta."""
    return [Paragraph(f"• {item}", E['bullet']) for item in items]

def activity_block(label, content_paragraphs):
    """Bloque de actividad con etiqueta bold + contenido."""
    return content_paragraphs

# ─── GENERADOR PRINCIPAL ──────────────────────────────────────────────────────
def generate_sesion(data: dict, output_path: str = "sesion_aprendizaje.pdf"):
    """
    Genera el PDF de la sesión de aprendizaje.

    CAMPOS ESPERADOS EN data (todos opcionales, se muestran vacíos si faltan):
    ─────────────────────────────────────────────────────────────────────────
    # DATOS GENERALES
    data['ie']              → str  : Nombre de la I.E.
    data['ugel']            → str  : UGEL
    data['fecha']           → str  : Fecha de la sesión (ej: "16/05/2026")
    data['grado']           → str  : Grado (ej: "2° Secundaria")
    data['ciclo']           → str  : Ciclo (ej: "Ciclo VI")
    data['seccion']         → str  : Sección (ej: "A")
    data['duracion']        → str  : Duración (ej: "90 minutos")
    data['docente']         → str  : Nombre del docente
    data['unidad']          → str  : N° y nombre de la unidad didáctica
    data['sesion_num']      → str  : "Sesión N° X de Y"
    data['area']            → str  : Área curricular (ej: "Matemática")

    # PREPARACIÓN
    data['actividades_previas']   → list[str] : actividades antes de la sesión
    data['recursos_materiales']   → list[str] : recursos y materiales

    # TÍTULO
    data['titulo']          → str  : Título de la sesión

    # PROPÓSITOS
    data['proposito_aprendizaje'] → str : propósito en lenguaje amigable

    # COMPETENCIAS Y CAPACIDADES (lista de dicts)
    data['competencias'] → list[dict]:
        [{ 'competencia': str, 'capacidades': list[str] }]

    # DESEMPEÑOS
    data['desempenos']      → list[str] : desempeños por grado

    # CRITERIOS DE EVALUACIÓN
    data['criterios_evaluacion'] → list[str]

    # EVIDENCIA DE APRENDIZAJE
    data['evidencia']       → str  : descripción de la evidencia
    data['instrumento']     → str  : instrumento de evaluación

    # ENFOQUE TRANSVERSAL
    data['enfoque_transversal']   → str  : nombre del enfoque
    data['actitudes_observables'] → str  : actitudes o acciones observables

    # INICIO (list[dict] con 'tipo' y 'texto' o 'items')
    data['inicio']          → list[dict]
    # DESARROLLO
    data['desarrollo']      → list[dict]
    # CIERRE
    data['cierre']          → list[dict]

    # ACTIVIDAD DE EXTENSIÓN
    data['extension']       → str

    # METADATA
    data['lugar']           → str  : Ciudad / lugar
    ─────────────────────────────────────────────────────────────────────────
    """

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.6*cm, bottomMargin=1.8*cm
    )
    E = estilos()
    story = []

    def v(key, default=""):
        val = data.get(key, default)
        if val is None or str(val).strip() == "" or str(val).strip() == "—vacío—":
            return str(default)
        return str(val)

    def vlist(key):
        val = data.get(key, []) or []
        if isinstance(val, str):
            import re
            items = re.split(r'\n|\s*\d+\.\s*', val)
            return [x.strip() for x in items if x.strip() and x.strip() != "—vacío—"]
        if isinstance(val, list):
            cleaned = []
            for x in val:
                if isinstance(x, str):
                    if x.strip() != "—vacío—":
                        cleaned.append(x)
                else:
                    cleaned.append(x)
            return cleaned
        return val

    # ── ENCABEZADO ────────────────────────────────────────────────────────────
    header_logo_cell = Paragraph(
        '<font color="#1565C0"><b>🎓 MINEDU</b></font>',
        ParagraphStyle('logo', fontName='Helvetica-Bold', fontSize=9,
                       textColor=AZUL_HEADER, leading=12, alignment=TA_CENTER))

    header_title = Paragraph(
        "SESIÓN DE APRENDIZAJE",
        E['doc_title'])

    sesion_str = f'  ·  Sesión: <b>{v("sesion_num")}</b>' if v("sesion_num") else ''
    header_area = Paragraph(
        f'Área: <b>{v("area", "Matemática")}</b>  ·  '
        f'Unidad: <b>{v("unidad", "")}</b>'
        f'{sesion_str}',
        ParagraphStyle('ha', fontName='Helvetica', fontSize=8.5,
                       textColor=AZUL_MED, leading=12, alignment=TA_CENTER))

    header_t = Table([
        [header_logo_cell, header_title, header_logo_cell],
        ['', header_area, ''],
    ], colWidths=[2.5*cm, W_PAGE-5*cm, 2.5*cm])
    header_t.setStyle(TableStyle([
        ('SPAN', (1,0),(1,1)),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('LINEBELOW',(0,1),(-1,1),1.5,AZUL_HEADER),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,1),(-1,1),6),
    ]))
    story.append(header_t)
    story.append(Spacer(1, 8))

    # ── BLOQUE 1: DATOS GENERALES ─────────────────────────────────────────────
    story.append(section_bar("I.  DATOS DE LA SESIÓN", E))
    story.append(Spacer(1, 3))

    lbl = E['field_label']
    val = E['field_value']

    datos_row1 = [
        [Paragraph("I.E.:", lbl),
         Paragraph(v('ie'), val),
         Paragraph("UGEL:", lbl),
         Paragraph(v('ugel'), val)],
    ]
    datos_row2 = [
        [Paragraph("DOCENTE:", lbl),
         Paragraph(v('docente'), val),
         Paragraph("FECHA:", lbl),
         Paragraph(v('fecha'), val)],
    ]
    datos_row3 = [
        [Paragraph("GRADO / CICLO:", lbl),
         Paragraph(f"{v('grado')}  —  {v('ciclo')}", val),
         Paragraph("SECCIÓN:", lbl),
         Paragraph(v('seccion'), val)],
    ]
    datos_row4 = [
        [Paragraph("DURACIÓN:", lbl),
         Paragraph(v('duracion'), val),
         Paragraph("N° ESTUDIANTES:", lbl),
         Paragraph(v('num_estudiantes'), val)],
    ]
    datos_row5 = [
        [Paragraph("LUGAR:", lbl),
         Paragraph(v('lugar'), val),
         Paragraph("", lbl),
         Paragraph("", val)],
    ]

    col_w = [2.9*cm, W_PAGE/2-2.9*cm, 3.1*cm, W_PAGE/2-3.1*cm]

    def datos_table(rows):
        t = Table(rows, colWidths=col_w)
        t.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),5),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),6),
            ('RIGHTPADDING',(0,0),(-1,-1),6),
            ('LINEBELOW',(0,0),(-1,-1),0.4,GRIS_LINEA),
            ('ROWBACKGROUNDS',(0,0),(-1,-1),[BLANCO]),
        ]))
        return t

    story.append(datos_table(datos_row1))
    story.append(datos_table(datos_row2))
    story.append(datos_table(datos_row3))
    story.append(datos_table(datos_row4))
    story.append(datos_table(datos_row5))
    story.append(Spacer(1, 8))

    # ── BLOQUE 2: PREPARACIÓN ─────────────────────────────────────────────────
    story.append(section_bar("II.  PREPARACIÓN DE LA SESIÓN", E))
    story.append(Spacer(1, 3))

    act_prev = vlist('actividades_previas')
    rec_mat  = vlist('recursos_materiales')

    prev_items = bullet_list(act_prev, E) if act_prev else [Paragraph("", E['cell_body'])]
    rec_items  = bullet_list(rec_mat, E)  if rec_mat  else [Paragraph("", E['cell_body'])]

    prep_header = Table([
        [Paragraph("¿QUÉ ACTIVIDADES HACER ANTES DE LA SESIÓN?", E['cell_header']),
         Paragraph("¿QUÉ RECURSOS O MATERIALES SE UTILIZARÁN?", E['cell_header'])],
    ], colWidths=[W_PAGE/2, W_PAGE/2])
    prep_header.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), AZUL_MED),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('LINEAFTER',(0,0),(0,-1),0.5,BLANCO),
    ]))

    prep_body = Table([
        [[p for p in prev_items], [p for p in rec_items]],
    ], colWidths=[W_PAGE/2, W_PAGE/2])
    prep_body.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('BOX',(0,0),(-1,-1),0.5,GRIS_LINEA),
        ('LINEAFTER',(0,0),(0,-1),0.5,GRIS_LINEA),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[AZUL_PALIDO]),
    ]))

    story.append(prep_header)
    story.append(prep_body)
    story.append(Spacer(1, 8))

    # ── BLOQUE 3: TÍTULO ──────────────────────────────────────────────────────
    titulo_t = Table([
        [Paragraph("TÍTULO DE LA SESIÓN:", E['titulo_sesion_label']),
         Paragraph(v('titulo').upper(), E['titulo_sesion_value'])],
    ], colWidths=[4.5*cm, W_PAGE-4.5*cm])
    titulo_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BACKGROUND',(0,0),(-1,-1), AZUL_PALIDO),
        ('BOX',(0,0),(-1,-1),1, AZUL_HEADER),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(titulo_t)
    story.append(Spacer(1, 4))

    # Propósito amigable
    prop_t = Table([
        [Paragraph("PROPÓSITO:", E['field_label']),
         Paragraph(v('proposito_aprendizaje'), E['field_value'])],
    ], colWidths=[2.8*cm, W_PAGE-2.8*cm])
    prop_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BACKGROUND',(0,0),(-1,-1), BLANCO),
        ('BOX',(0,0),(-1,-1),0.5, GRIS_LINEA),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(prop_t)
    story.append(Spacer(1, 8))

    # ── BLOQUE 4: PROPÓSITOS Y EVIDENCIAS ────────────────────────────────────
    story.append(section_bar("III.  PROPÓSITOS DE APRENDIZAJE Y EVIDENCIAS", E))
    story.append(Spacer(1, 3))

    # Encabezado tabla
    prop_head = Table([[
        Paragraph("ÁREA, COMPETENCIAS\nY CAPACIDADES", E['cell_header']),
        Paragraph("DESEMPEÑOS\n(por grado)", E['cell_header']),
        Paragraph("CRITERIOS DE\nEVALUACIÓN", E['cell_header']),
        Paragraph("EVIDENCIA DE\nAPRENDIZAJE", E['cell_header']),
    ]], colWidths=[4.2*cm, 5.8*cm, 3.8*cm, 3.2*cm])
    prop_head.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), AZUL_MED),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('LINEAFTER',(0,0),(2,-1),0.5,BLANCO),
    ]))

    # Contenido competencias
    comps = vlist('competencias')
    comp_text_parts = []
    for c in comps:
        comp_text_parts.append(
            Paragraph(f"<b>{c.get('competencia','')}</b>", E['cell_body_bold']))
        for cap in c.get('capacidades', []):
            comp_text_parts.append(Paragraph(f"• {cap}", E['bullet']))
    if not comp_text_parts:
        comp_text_parts = [Paragraph("", E['cell_body'])]

    desempenos = vlist('desempenos')
    desemp_parts = [Paragraph(f"• {d}", E['bullet']) for d in desempenos] \
                   if desempenos else [Paragraph("", E['cell_body'])]

    criterios = vlist('criterios_evaluacion')
    crit_parts = [Paragraph(f"• {c}", E['bullet']) for c in criterios] \
                 if criterios else [Paragraph("", E['cell_body'])]

    evidencia_parts = [
        Paragraph(v('evidencia'), E['cell_body']),
        Spacer(1, 6),
        Paragraph("<b>Instrumento:</b>", E['cell_body_bold']),
        Paragraph(v('instrumento'), E['cell_body']),
    ]

    prop_body = Table([[
        comp_text_parts,
        desemp_parts,
        crit_parts,
        evidencia_parts,
    ]], colWidths=[4.2*cm, 5.8*cm, 3.8*cm, 3.2*cm])
    prop_body.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('BOX',(0,0),(-1,-1),0.5, GRIS_LINEA),
        ('LINEAFTER',(0,0),(2,-1),0.5, GRIS_LINEA),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[AZUL_PALIDO]),
    ]))

    story.append(prop_head)
    story.append(prop_body)
    story.append(Spacer(1, 4))

    # Enfoque transversal
    enf_head = Table([[
        Paragraph("ENFOQUE TRANSVERSAL", E['cell_header']),
        Paragraph("ACTITUDES O ACCIONES OBSERVABLES", E['cell_header']),
    ]], colWidths=[5*cm, W_PAGE-5*cm])
    enf_head.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), AZUL_MED),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('LINEAFTER',(0,0),(0,-1),0.5,BLANCO),
    ]))
    enf_body = Table([[
        Paragraph(v('enfoque_transversal'), E['cell_body_bold']),
        Paragraph(v('actitudes_observables'), E['cell_body']),
    ]], colWidths=[5*cm, W_PAGE-5*cm])
    enf_body.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('BOX',(0,0),(-1,-1),0.5,GRIS_LINEA),
        ('LINEAFTER',(0,0),(0,-1),0.5,GRIS_LINEA),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[BLANCO]),
    ]))
    story.append(enf_head)
    story.append(enf_body)
    story.append(Spacer(1, 8))

    # ── BLOQUE 5: DESARROLLO DE LA SESIÓN ────────────────────────────────────
    story.append(section_bar("IV.  SECUENCIA DIDÁCTICA (DESARROLLO DE LA SESIÓN)", E))
    story.append(Spacer(1, 4))

    def momento_block(label, color_bg, items_data, tiempo=""):
        """Genera un bloque de momento (Inicio/Desarrollo/Cierre)."""
        tiempo_str = f"  ({tiempo})" if tiempo else ""
        header = Table([[
            Paragraph(f"{label}{tiempo_str}", E['section_header']),
        ]], colWidths=[W_PAGE])
        header.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), color_bg),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),8),
        ]))

        content_parts = []
        for item in items_data:
            tipo = item.get('tipo', 'texto')
            if tipo == 'subtitulo':
                content_parts.append(
                    Paragraph(item.get('texto',''), E['actividad_bold']))
            elif tipo == 'lista':
                for li in item.get('items', []):
                    content_parts.append(Paragraph(f"• {li}", E['bullet']))
            elif tipo == 'pregunta':
                for q in item.get('items', []):
                    content_parts.append(Paragraph(f"— {q}", E['bullet']))
            else:  # texto plano
                content_parts.append(
                    Paragraph(item.get('texto',''), E['actividad']))
            content_parts.append(Spacer(1, 3))

        if not content_parts:
            content_parts = [Paragraph("", E['actividad'])]

        body = Table([[content_parts]], colWidths=[W_PAGE])
        body.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
            ('BOX',(0,0),(-1,-1),0.5, GRIS_LINEA),
            ('LINEABOVE',(0,0),(-1,0),0,BLANCO),
        ]))
        return [header, body, Spacer(1,6)]

    # INICIO
    inicio_data  = vlist('inicio')
    has_acuerdos = any(isinstance(i, dict) and "acuerdos" in str(i.get('texto', '')).lower() for i in inicio_data)
    if not has_acuerdos and inicio_data:
        inicio_data.append({"tipo": "subtitulo", "texto": "Acuerdos de convivencia"})
        inicio_data.append({"tipo": "lista", "items": [
            "Escuchar y respetar las ideas de los demás.",
            "Participar activamente en las actividades.",
            "Levantar la mano para participar."
        ]})

    inicio_dur   = v('duracion_inicio', '10 min')
    for el in momento_block("INICIO", AZUL_HEADER, inicio_data, inicio_dur):
        story.append(el)

    # DESARROLLO
    desarrollo_data = vlist('desarrollo')
    des_dur = v('duracion_desarrollo', '70 min')
    for el in momento_block("DESARROLLO", AZUL_MED, desarrollo_data, des_dur):
        story.append(el)

    # CIERRE
    cierre_data = vlist('cierre')
    processed_cierre = []
    has_meta = False
    for item in cierre_data:
        if isinstance(item, dict) and item.get('tipo') == 'texto':
            txt = item.get('texto', '')
            if '¿' in txt and '?' in txt and ('metacogn' in txt.lower() or 'aprend' in txt.lower()):
                import re
                questions = re.findall(r'¿[^?]+?\?', txt)
                if len(questions) >= 1:
                    has_meta = True
                    non_q_text = re.sub(r'¿[^?]+?\?', '', txt).strip()
                    if non_q_text:
                        processed_cierre.append({"tipo": "texto", "texto": non_q_text})
                    processed_cierre.append({"tipo": "subtitulo", "texto": "Reflexión metacognitiva"})
                    processed_cierre.append({"tipo": "pregunta", "items": questions})
                    continue
        if isinstance(item, dict) and item.get('tipo') in ['pregunta', 'lista'] and ('aprend' in str(item).lower() or 'meta' in str(item).lower()):
            has_meta = True
        processed_cierre.append(item)
    
    if not has_meta and processed_cierre:
        processed_cierre.append({"tipo": "subtitulo", "texto": "Reflexión metacognitiva"})
        processed_cierre.append({"tipo": "pregunta", "items": [
            "¿Qué aprendí hoy?",
            "¿Para qué me sirve lo aprendido?",
            "¿Qué dificultades tuve y cómo las superé?"
        ]})

    cierre_dur  = v('duracion_cierre', '10 min')
    for el in momento_block("CIERRE", colors.HexColor("#0D47A1"), processed_cierre, cierre_dur):
        story.append(el)

    story.append(Spacer(1, 6))

    # ── BLOQUE 6: ACTIVIDAD DE EXTENSIÓN ─────────────────────────────────────
    ext_t = Table([
        [Paragraph("V.  ACTIVIDAD DE EXTENSIÓN (TAREA):", E['field_label']),
         Paragraph(v('extension'), E['field_value'])],
    ], colWidths=[5.5*cm, W_PAGE-5.5*cm])
    ext_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BACKGROUND',(0,0),(-1,-1), AZUL_PALIDO),
        ('BOX',(0,0),(-1,-1),0.5, GRIS_LINEA),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(ext_t)
    story.append(Spacer(1, 16))

    # ── BLOQUE 7: INSTRUMENTO DE EVALUACIÓN ──────────────────────────────────
    inst_gen = data.get('instrumento_evaluacion_generado')
    if inst_gen:
        tipo_inst = inst_gen.get('tipo_instrumento', 'INSTRUMENTO').upper()
        
        criterios = inst_gen.get('criterios_o_items', [])
        escalas = inst_gen.get('escalas_o_niveles', [])
        
        if "COTEJO" in tipo_inst and len(escalas) > 2:
            escalas = ["SÍ", "NO"]
            
        def render_instrument(suffix=""):
            elements = []
            elements.append(section_bar(f"VI.  INSTRUMENTO DE EVALUACIÓN: {tipo_inst}{suffix}", E))
            elements.append(Spacer(1, 4))
            
            if criterios:
                inst_head_row = [Paragraph("CRITERIOS / ÍTEMS A EVALUAR", E['cell_header'])]
                for esc in escalas:
                    inst_head_row.append(Paragraph(esc, E['cell_header']))
                    
                inst_table_data = [inst_head_row]
                for crit in criterios:
                    row = [Paragraph(f"• {crit}", E['cell_body'])]
                    for _ in escalas:
                        row.append(Paragraph("", E['cell_body']))
                    inst_table_data.append(row)
                    
                col_w_crit = W_PAGE * 0.6 if escalas else W_PAGE
                col_w_rest = (W_PAGE - col_w_crit) / max(len(escalas), 1)
                col_widths = [col_w_crit] + [col_w_rest] * len(escalas)
                
                inst_t = Table(inst_table_data, colWidths=col_widths)
                inst_t.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0), AZUL_MED),
                    ('ALIGN',(1,0),(-1,-1),'CENTER'),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                    ('LEFTPADDING',(0,0),(0,-1),8),
                    ('BOX',(0,0),(-1,-1),0.5, GRIS_LINEA),
                    ('GRID',(0,0),(-1,-1),0.5, GRIS_LINEA),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[BLANCO, AZUL_PALIDO]),
                ]))
                elements.append(inst_t)
                elements.append(Spacer(1, 16))
            return elements

        story.extend(render_instrument())
        
        if "COTEJO" in tipo_inst:
            story.extend(render_instrument(" (Para el estudiante)"))

    # ── BLOQUE 8: FIRMAS ─────────────────────────────────────────────────────
    firma_t = Table([[
        Table([[
            Paragraph("", E['field_value']),
            HRFlowable(width=5*cm, thickness=0.8, color=NEGRO),
            Paragraph(f"<b>{v('docente', 'Docente')}</b>", ParagraphStyle('fn',
                fontName='Helvetica-Bold', fontSize=9, textColor=NEGRO,
                leading=12, alignment=TA_CENTER)),
            Paragraph("Docente del Área", E['footer']),
        ]], colWidths=[5*cm], style=[
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),3),
            ('BOTTOMPADDING',(0,0),(-1,-1),3),
        ]),
        Table([[
            Paragraph("", E['field_value']),
            HRFlowable(width=5*cm, thickness=0.8, color=NEGRO),
            Paragraph("V°B° Director(a)", ParagraphStyle('fn2',
                fontName='Helvetica-Bold', fontSize=9, textColor=NEGRO,
                leading=12, alignment=TA_CENTER)),
            Paragraph("Dirección I.E.", E['footer']),
        ]], colWidths=[5*cm], style=[
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),3),
            ('BOTTOMPADDING',(0,0),(-1,-1),3),
        ]),
    ]], colWidths=[W_PAGE/2, W_PAGE/2])
    firma_t.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
        ('TOPPADDING',(0,0),(-1,-1),20),
    ]))
    story.append(firma_t)
    story.append(Spacer(1, 12))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=W_PAGE, thickness=0.5, color=GRIS_LINEA))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generado con EduMath IA  ·  Alineado al CNEB 2016 (RM 649-2016-MINEDU)  ·  "
        f"{v('fecha')}",
        E['footer']))

    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(AZUL_HEADER)
        canvas.setFillAlpha(0.06)  # Opacidad muy baja (marca de agua suave)
        canvas.setFont('Helvetica-Bold', 130)
        
        # Centrar y rotar 45 grados en el medio de la hoja
        canvas.translate(A4[0] / 2, A4[1] / 2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "SESION+")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
    print(f"PDF generado exitosamente: {output_path}")
    return output_path


# ─── DATOS DE EJEMPLO (para probar el microservicio) ──────────────────────────
EJEMPLO = {
    # DATOS GENERALES
    "ie": "I.E. 7096 Príncipe de Asturias",
    "ugel": "UGEL 01 — San Juan de Miraflores",
    "fecha": "16/05/2026",
    "grado": "2° Secundaria",
    "ciclo": "Ciclo VI",
    "seccion": "A",
    "duracion": "90 minutos (2 horas pedagógicas)",
    "docente": "María Elena Quispe Huanca",
    "unidad": "Unidad 3 — Matemática en mi vida cotidiana",
    "sesion_num": "Sesión N° 5 de 8",
    "area": "Matemática",
    "lugar": "Lima, Perú",

    # PREPARACIÓN
    "actividades_previas": [
        "Revisar los desempeños del grado según el Programa Curricular de Secundaria.",
        "Preparar las fichas de trabajo y los materiales para la dinámica de inicio.",
        "Imprimir los anexos con situaciones problemáticas de contexto real.",
        "Verificar que el aula cuente con plumones y papelógrafo.",
    ],
    "recursos_materiales": [
        "Fichas de trabajo impresas (Anexo 1 y 2).",
        "Papelógrafo, plumones, cinta adhesiva.",
        "Calculadora básica (una por grupo).",
        "Recibos de compra del mercado (material no estructurado).",
        "Pizarra y tizas de colores.",
    ],

    # TÍTULO Y PROPÓSITO
    "titulo": "Calculando descuentos y porcentajes en las compras del mercado",
    "proposito_aprendizaje": (
        "Hoy aprenderemos a calcular porcentajes y descuentos en situaciones de compra y venta, "
        "usando estrategias de estimación y cálculo para tomar decisiones financieras inteligentes."
    ),

    # COMPETENCIAS Y CAPACIDADES
    "competencias": [
        {
            "competencia": "Resuelve problemas de cantidad",
            "capacidades": [
                "Traduce cantidades a expresiones numéricas.",
                "Comunica su comprensión sobre los números y las operaciones.",
                "Usa estrategias y procedimientos de estimación y cálculo.",
                "Argumenta afirmaciones sobre las relaciones numéricas y las operaciones.",
            ]
        }
    ],

    # DESEMPEÑOS
    "desempenos": [
        "Establece relaciones entre datos y acciones de ganar, perder, comparar e igualar cantidades.",
        "Transforma estas relaciones a expresiones numéricas que incluyen operaciones con números "
        "enteros, decimales y aumentos o descuentos porcentuales sucesivos.",
        "Selecciona y emplea estrategias de cálculo para realizar operaciones con expresiones "
        "fraccionarias, decimales y porcentuales, así como para calcular aumentos y descuentos.",
        "Plantea afirmaciones sobre las propiedades de los números y las operaciones, y las justifica.",
    ],

    # CRITERIOS DE EVALUACIÓN
    "criterios_evaluacion": [
        "Traduce correctamente situaciones de descuento a expresiones porcentuales.",
        "Calcula el precio final tras aplicar descuentos porcentuales sucesivos.",
        "Justifica el procedimiento utilizado con lenguaje matemático.",
        "Verifica si el resultado obtenido cumple las condiciones del problema.",
    ],

    # EVIDENCIA
    "evidencia": (
        "Ficha de trabajo resuelta: el estudiante calcula precios con descuento "
        "en situaciones del mercado local y explica el procedimiento usado."
    ),
    "instrumento": "Lista de cotejo",

    # ENFOQUE TRANSVERSAL
    "enfoque_transversal": "Enfoque de Orientación al Bien Común",
    "actitudes_observables": (
        "Los estudiantes comparten sus estrategias de cálculo con sus compañeros y reflexionan "
        "sobre la importancia de tomar decisiones financieras informadas para el bienestar "
        "familiar y de la comunidad."
    ),

    # DURACIONES POR MOMENTO
    "duracion_inicio": "15 min",
    "duracion_desarrollo": "60 min",
    "duracion_cierre": "15 min",

    # INICIO
    "inicio": [
        {"tipo": "subtitulo", "texto": "Motivación y recojo de saberes previos"},
        {"tipo": "texto", "texto":
            "El docente saluda a los estudiantes y presenta en la pizarra dos recibos de "
            "compra del mercado: uno sin descuento y uno con 20% de descuento. Pregunta:"},
        {"tipo": "pregunta", "items": [
            "¿Cuánto pagaron en cada caso?",
            "¿Cuánto ahorraron con el descuento?",
            "¿Cómo calcularías rápidamente el 20% de un precio?",
        ]},
        {"tipo": "texto", "texto":
            "Los estudiantes comentan sus respuestas en pareja. El docente recoge ideas "
            "en la pizarra y conecta con el propósito de la sesión."},
        {"tipo": "subtitulo", "texto": "Propósito de la sesión"},
        {"tipo": "texto", "texto":
            "'Hoy aprenderemos a calcular porcentajes y descuentos en compras del mercado "
            "para tomar decisiones financieras inteligentes.'"},
        {"tipo": "subtitulo", "texto": "Acuerdos de convivencia"},
        {"tipo": "lista", "items": [
            "Escuchar y respetar las ideas de todos.",
            "Participar activamente en los grupos.",
            "Usar el lenguaje matemático en las explicaciones.",
        ]},
    ],

    # DESARROLLO
    "desarrollo": [
        {"tipo": "subtitulo", "texto": "Planteamiento de la situación significativa"},
        {"tipo": "texto", "texto":
            "Se presenta el Anexo 1: 'La feria del mercado de San Juan tiene ofertas especiales "
            "este fin de semana. Una chaqueta que cuesta S/. 150 tiene un descuento del 30%. "
            "¿Cuánto pagas finalmente? Si la semana siguiente hay un descuento adicional del "
            "10%, ¿cuánto pagarías?'"},
        {"tipo": "subtitulo", "texto": "Búsqueda y ejecución de estrategias"},
        {"tipo": "texto", "texto":
            "Los estudiantes trabajan en grupos de 4. Cada grupo resuelve la situación "
            "usando la estrategia que elija (regla de tres, multiplicación directa, "
            "operaciones sucesivas). El docente acompaña y hace preguntas orientadoras."},
        {"tipo": "pregunta", "items": [
            "¿Qué significa aplicar un descuento del 30%?",
            "¿Es lo mismo aplicar 30%+10% que aplicar 40%? ¿Por qué?",
            "¿Cómo comprobarías que tu resultado es correcto?",
        ]},
        {"tipo": "subtitulo", "texto": "Socialización y formalización"},
        {"tipo": "texto", "texto":
            "Un representante de cada grupo expone su procedimiento en el papelógrafo. "
            "El docente formaliza el concepto de descuentos porcentuales sucesivos y "
            "diferencia entre descuento simple y sucesivo con contraejemplos."},
        {"tipo": "subtitulo", "texto": "Aplicación individual"},
        {"tipo": "texto", "texto":
            "Los estudiantes resuelven la Ficha de Trabajo (Anexo 2) de forma individual: "
            "5 problemas de cálculo de porcentajes y descuentos en contextos de compra, "
            "ahorro e impuestos (IGV). Tiempo: 20 minutos."},
    ],

    # CIERRE
    "cierre": [
        {"tipo": "subtitulo", "texto": "Reflexión metacognitiva"},
        {"tipo": "texto", "texto":
            "El docente invita a los estudiantes a reflexionar respondiendo en su cuaderno:"},
        {"tipo": "pregunta", "items": [
            "¿Qué aprendí hoy sobre los porcentajes?",
            "¿Qué estrategia me resultó más fácil y por qué?",
            "¿En qué situaciones de mi vida puedo usar lo que aprendí?",
            "¿Qué aún me genera duda?",
        ]},
        {"tipo": "texto", "texto":
            "El docente cierra felicitando la participación y recuerda la tarea para casa."},
    ],

    # EXTENSIÓN
    "extension": (
        "Busca en casa 3 recibos, facturas o etiquetas de precios. Calcula el precio real "
        "si aplicaras un descuento del 15% a cada uno. Trae los recibos y tus cálculos "
        "para la próxima sesión."
    ),
}


if __name__ == "__main__":
    generate_sesion(EJEMPLO, "sesion_aprendizaje_template_test.pdf")
