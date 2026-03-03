from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_pdf(crush_name: str, metrics: dict, history: list[dict]) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = 800
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, f"Relatório Recipro Evolution - {crush_name}")
    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 30

    for key, label in [
        ("hp", "Interesse Real (HP)"),
        ("reciprocity_score", "Reciprocidade"),
        ("investment_score", "Investimento"),
        ("depth_score", "Profundidade"),
        ("avg_response_total", "Tempo médio de resposta (min)"),
    ]:
        c.drawString(40, y, f"{label}: {metrics.get(key)}")
        y -= 20

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Insights")
    y -= 20
    c.setFont("Helvetica", 11)
    for insight in metrics.get("insights", []):
        c.drawString(50, y, f"- {insight[:100]}")
        y -= 18

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Histórico resumido")
    y -= 20
    c.setFont("Helvetica", 10)
    for item in history[-8:]:
        c.drawString(50, y, f"{item['date']}: HP {item['hp']} | Rec {item['rec']} | Inv {item['inv']} | Prof {item['depth']}")
        y -= 16
        if y < 70:
            c.showPage()
            y = 800
    c.save()
    return buffer.getvalue()
