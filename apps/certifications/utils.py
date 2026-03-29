"""PDF generation utilities for certificates."""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from django.core.files.base import ContentFile


def _build_pdf_buffer(certificado) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.2 * inch,
        leftMargin=1.2 * inch,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch,
    )

    styles = getSampleStyleSheet()
    BLUE = colors.HexColor('#2E3A8C')
    GOLD = colors.HexColor('#C9A84C')

    title_style = ParagraphStyle(
        'CertTitle', fontSize=40, textColor=BLUE,
        alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', fontSize=14, textColor=colors.grey,
        alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica',
    )
    label_style = ParagraphStyle(
        'Label', fontSize=13, textColor=colors.black,
        alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica',
    )
    name_style = ParagraphStyle(
        'Name', fontSize=28, textColor=BLUE,
        alignment=TA_CENTER, spaceAfter=24, fontName='Helvetica-Bold',
    )
    course_style = ParagraphStyle(
        'Course', fontSize=22, textColor=GOLD,
        alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica-Bold',
    )
    small_style = ParagraphStyle(
        'Small', fontSize=9, textColor=colors.grey,
        alignment=TA_CENTER, fontName='Helvetica',
    )

    story = [
        Paragraph('CERTIFICADO DE COMPLETACIÓN', title_style),
        Paragraph('Plataforma Educativa MihiTraining', subtitle_style),
        HRFlowable(width='100%', thickness=2, color=GOLD, spaceAfter=20),
        Paragraph('Este certificado se otorga a:', label_style),
        Paragraph(
            certificado.usuario.get_full_name() or certificado.usuario.username,
            name_style,
        ),
        Paragraph('por completar exitosamente el curso:', label_style),
        Paragraph(certificado.curso.nombre, course_style),
        Spacer(1, 0.2 * inch),
        HRFlowable(width='60%', thickness=1, color=colors.lightgrey, spaceAfter=16),
        Paragraph(
            f'Fecha de emisión: {certificado.fecha_emision.strftime("%d de %B de %Y")}',
            label_style,
        ),
        Spacer(1, 0.3 * inch),
        Paragraph(
            f'Código de verificación: {certificado.codigo_unico}',
            small_style,
        ),
        Paragraph(
            f'Verifica este certificado en: {certificado.get_validation_url()}',
            small_style,
        ),
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer


def generar_y_guardar_certificado(certificado) -> None:
    """Generate certificate PDF and save it to the model's file field."""
    buffer = _build_pdf_buffer(certificado)
    filename = f'certificado_{certificado.codigo_unico}.pdf'
    certificado.pdf.save(filename, ContentFile(buffer.read()), save=True)
