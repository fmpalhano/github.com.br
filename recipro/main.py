import json
import os
import tempfile
from datetime import datetime

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from analysis.chat_analyzer import (
    AnalysisError,
    analyze_conversation,
    compute_interest_hp,
    dumps_json,
    hearts_from_hp,
    parse_whatsapp_text,
)
from models.database import Base, SessionLocal, engine
from models.entities import Analysis, Crush
from utils.pdf_report import build_pdf
from utils.security import check_daily_limit

app = FastAPI(title="Recipro Evolution")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sanitize_name(name: str) -> str:
    cleaned = "".join(ch for ch in name.strip() if ch.isalnum() or ch in " -_")
    if not cleaned:
        raise HTTPException(status_code=400, detail="Nome inválido.")
    return cleaned[:120]


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    crushes = db.query(Crush).order_by(Crush.created_at.desc()).all()
    cards = []
    for crush in crushes:
        latest = (
            db.query(Analysis)
            .filter(Analysis.crush_id == crush.id)
            .order_by(Analysis.data_analise.desc())
            .first()
        )
        hp = 0
        if latest:
            hp = compute_interest_hp(latest.score_reciprocidade, latest.score_investimento, latest.score_profundidade)
        cards.append({"crush": crush, "latest": latest, "hp": hp, "hearts": hearts_from_hp(hp)})
    return templates.TemplateResponse("index.html", {"request": request, "cards": cards})


@app.post("/crush")
def create_crush(name: str = Form(...), db: Session = Depends(get_db)):
    crush = Crush(nome=sanitize_name(name))
    db.add(crush)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível criar crush (talvez já exista).")
    db.refresh(crush)
    return RedirectResponse(url=f"/crush/{crush.id}", status_code=303)


@app.get("/crush/{crush_id}", response_class=HTMLResponse)
def crush_detail(crush_id: int, request: Request, db: Session = Depends(get_db)):
    crush = db.query(Crush).filter(Crush.id == crush_id).first()
    if not crush:
        raise HTTPException(status_code=404, detail="Crush não encontrado")
    analyses = db.query(Analysis).filter(Analysis.crush_id == crush_id).order_by(Analysis.data_analise.asc()).all()

    chart_points = []
    rows = []
    latest_metrics = None
    for a in analyses:
        hp = compute_interest_hp(a.score_reciprocidade, a.score_investimento, a.score_profundidade)
        chart_points.append({"date": a.data_analise.strftime("%d/%m/%Y"), "hp": hp})
        rows.append({"date": a.data_analise.strftime("%d/%m/%Y %H:%M"), "hp": hp, "rec": a.score_reciprocidade, "inv": a.score_investimento, "depth": a.score_profundidade})
    if analyses:
        a = analyses[-1]
        hp = compute_interest_hp(a.score_reciprocidade, a.score_investimento, a.score_profundidade)
        latest_metrics = {
            "hp": hp,
            "reciprocity": a.score_reciprocidade,
            "investment": a.score_investimento,
            "depth": a.score_profundidade,
            "response": a.tempo_medio_resposta,
            "insights": json.loads(a.insights_json),
            "small_warning": a.total_mensagens < 500,
            "weekly": json.loads(a.tendencia_semana_json),
        }
    variation = None
    if len(analyses) >= 2:
        prev = compute_interest_hp(analyses[-2].score_reciprocidade, analyses[-2].score_investimento, analyses[-2].score_profundidade)
        cur = latest_metrics["hp"]
        if prev > 0:
            pct = ((cur - prev) / prev) * 100
        else:
            pct = 100.0 if cur > 0 else 0.0
        symbol = "↑" if pct > 1 else "↓" if pct < -1 else "→"
        variation = f"{symbol} {pct:+.1f}% Interesse"

    return templates.TemplateResponse(
        "crush.html",
        {
            "request": request,
            "crush": crush,
            "latest": latest_metrics,
            "variation": variation,
            "history": rows,
            "history_json": json.dumps(chart_points, ensure_ascii=False),
            "hearts": hearts_from_hp(latest_metrics["hp"] if latest_metrics else 0),
        },
    )


@app.post("/crush/{crush_id}/analyze")
async def analyze_file(crush_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    crush = db.query(Crush).filter(Crush.id == crush_id).first()
    if not crush:
        raise HTTPException(status_code=404, detail="Crush não encontrado")

    ip = request.client.host if request.client else "unknown"
    if not check_daily_limit(ip, limit=5):
        raise HTTPException(status_code=429, detail="Limite diário de 5 análises por IP atingido.")

    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .txt são aceitos.")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo excede limite de 20MB.")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        text = content.decode("utf-8", errors="ignore")
        df = parse_whatsapp_text(text)
        data = analyze_conversation(df)

        analysis = Analysis(
            crush_id=crush.id,
            data_analise=datetime.utcnow(),
            total_mensagens=data["total_messages"],
            score_reciprocidade=data["reciprocity_score"],
            score_investimento=data["investment_score"],
            score_profundidade=data["depth_score"],
            tempo_medio_resposta=data["avg_response_total"],
            percentual_mensagens_usuario=data["percent_user_messages"],
            tendencia_semana_json=dumps_json(data["weekly_trend"]),
            insights_json=dumps_json(data["insights"]),
        )
        db.add(analysis)
        db.commit()
    except AnalysisError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return RedirectResponse(url=f"/crush/{crush.id}", status_code=303)


@app.get("/crush/{crush_id}/pdf")
def export_pdf(crush_id: int, db: Session = Depends(get_db)):
    crush = db.query(Crush).filter(Crush.id == crush_id).first()
    if not crush:
        raise HTTPException(status_code=404, detail="Crush não encontrado")
    analyses = db.query(Analysis).filter(Analysis.crush_id == crush_id).order_by(Analysis.data_analise.asc()).all()
    if not analyses:
        raise HTTPException(status_code=400, detail="Sem análises para exportar.")
    last = analyses[-1]
    hp = compute_interest_hp(last.score_reciprocidade, last.score_investimento, last.score_profundidade)
    metrics = {
        "hp": hp,
        "reciprocity_score": last.score_reciprocidade,
        "investment_score": last.score_investimento,
        "depth_score": last.score_profundidade,
        "avg_response_total": last.tempo_medio_resposta,
        "insights": json.loads(last.insights_json),
    }
    history = [
        {
            "date": a.data_analise.strftime("%d/%m/%Y"),
            "hp": compute_interest_hp(a.score_reciprocidade, a.score_investimento, a.score_profundidade),
            "rec": a.score_reciprocidade,
            "inv": a.score_investimento,
            "depth": a.score_profundidade,
        }
        for a in analyses
    ]
    pdf_bytes = build_pdf(crush.nome, metrics, history)
    return Response(pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=recipro_{crush.id}.pdf"})
