import json
import re
from collections import Counter
from datetime import datetime
from typing import Any

import pandas as pd
import spacy
from textblob import TextBlob

WHATSAPP_PATTERN = re.compile(r"^(\d{2}/\d{2}/\d{4}),\s(\d{2}:\d{2})\s-\s([^:]+):\s(.*)$")
OPEN_QUESTION_PATTERN = re.compile(r"\b(como|por que|porque|o que|qual|quais)\b", re.IGNORECASE)
AFFECTIVE_WORDS = {
    "amor", "carinho", "saudade", "abraço", "beijo", "fofo", "lindo", "linda", "gosto", "feliz", "querido", "querida"
}

try:
    NLP = spacy.load("pt_core_news_sm")
except OSError:
    NLP = spacy.blank("pt")


class AnalysisError(Exception):
    pass


def parse_whatsapp_text(text: str) -> pd.DataFrame:
    rows = []
    for line in text.splitlines():
        match = WHATSAPP_PATTERN.match(line.strip())
        if not match:
            continue
        date_str, hour_str, author, message = match.groups()
        try:
            timestamp = datetime.strptime(f"{date_str} {hour_str}", "%d/%m/%Y %H:%M")
        except ValueError as exc:
            raise AnalysisError("Foram encontrados timestamps inválidos no arquivo.") from exc
        rows.append({"timestamp": timestamp, "author": author.strip(), "message": message.strip()})

    if not rows:
        raise AnalysisError("Formato inválido. Use exportação WhatsApp: DD/MM/YYYY, HH:MM - Nome: Mensagem")
    df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
    if len(df["author"].unique()) > 2:
        raise AnalysisError("A análise suporta apenas conversas com 2 participantes.")
    return df


def _safe_balance(v1: float, v2: float) -> float:
    base = max((v1 + v2) / 2, 1e-9)
    return min(abs(v1 - v2) / base * 100, 100)


def _weekly_trend(df: pd.DataFrame) -> list[dict[str, Any]]:
    weekly = df.assign(week=df["timestamp"].dt.to_period("W").astype(str)).groupby(["week", "author"]).size().reset_index(name="count")
    result = []
    for week, group in weekly.groupby("week"):
        payload = {"week": week}
        for _, row in group.iterrows():
            payload[row["author"]] = int(row["count"])
        result.append(payload)
    return result


def analyze_conversation(df: pd.DataFrame) -> dict[str, Any]:
    participants = list(df["author"].unique())
    if len(participants) != 2:
        raise AnalysisError("Não foi possível identificar exatamente dois participantes.")

    p1, p2 = participants
    counts = df["author"].value_counts().to_dict()

    # Lógica: identifica quem inicia cada dia para representar iniciativa relacional.
    starters = df.sort_values("timestamp").groupby(df["timestamp"].dt.date).first()["author"].value_counts().to_dict()

    response_gaps = {p1: [], p2: []}
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        if prev["author"] != curr["author"]:
            # Fórmula: diferença temporal entre mensagens alternadas em minutos.
            gap = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 60
            response_gaps[curr["author"]].append(max(gap, 0))

    avg_response = {k: (sum(v) / len(v) if v else 0.0) for k, v in response_gaps.items()}
    msg_sizes = df.assign(length=df["message"].str.len()).groupby("author")["length"].mean().to_dict()

    question_counts = df.assign(is_question=df["message"].str.contains(r"\?")).groupby("author")["is_question"].sum().to_dict()
    open_questions = df.assign(open_q=df["message"].str.contains(OPEN_QUESTION_PATTERN)).groupby("author")["open_q"].sum().to_dict()

    sentiments = {}
    lexical = {}
    affective = {}
    for author in participants:
        texts = df.loc[df["author"] == author, "message"].tolist()
        if texts:
            polarities = [TextBlob(t).sentiment.polarity for t in texts]
            sentiments[author] = float(sum(polarities) / len(polarities))
            doc = NLP(" ".join(texts).lower())
            tokens = [t.text for t in doc if t.is_alpha]
            unique_ratio = len(set(tokens)) / max(len(tokens), 1)
            lexical[author] = unique_ratio
            affective[author] = sum(1 for tok in tokens if tok in AFFECTIVE_WORDS)
        else:
            sentiments[author] = 0.0
            lexical[author] = 0.0
            affective[author] = 0

    # Score de reciprocidade: mede equilíbrio de troca, tempo e curiosidade.
    diff_messages = _safe_balance(counts.get(p1, 0), counts.get(p2, 0))
    diff_response = _safe_balance(avg_response.get(p1, 0), avg_response.get(p2, 0))
    diff_questions = _safe_balance(question_counts.get(p1, 0), question_counts.get(p2, 0))
    reciprocity = max(0.0, 100 - ((diff_messages + diff_response + diff_questions) / 3))

    # Score de investimento: profundidade afetiva percebida por extensão, afeto e valência positiva.
    invest_raw = (
        (sum(msg_sizes.values()) / 2) * 0.6
        + (sum(affective.values()) / max(len(df), 1) * 100) * 0.25
        + ((sum(sentiments.values()) / 2 + 1) * 50) * 0.15
    )
    investimento = max(0.0, min(invest_raw, 100.0))

    # Score de profundidade: abertura dialógica + elaboração + variedade lexical.
    total_open_q = sum(open_questions.values())
    open_q_ratio = total_open_q / max(sum(question_counts.values()), 1)
    avg_len = sum(msg_sizes.values()) / 2
    avg_lex = sum(lexical.values()) / 2
    profundidade = max(0.0, min(open_q_ratio * 50 + min(avg_len, 120) * 0.25 + avg_lex * 35, 100))

    weekly = _weekly_trend(df)
    small_sample_warning = len(df) < 500

    return {
        "participants": participants,
        "total_messages": int(len(df)),
        "message_counts": counts,
        "starters": starters,
        "avg_response": avg_response,
        "avg_message_size": msg_sizes,
        "questions": question_counts,
        "open_questions": open_questions,
        "sentiments": sentiments,
        "reciprocity_score": round(reciprocity, 2),
        "investment_score": round(investimento, 2),
        "depth_score": round(profundidade, 2),
        "weekly_trend": weekly,
        "percent_user_messages": round((counts.get(p1, 0) / max(len(df), 1)) * 100, 2),
        "avg_response_total": round(sum(avg_response.values()) / 2, 2),
        "small_sample_warning": small_sample_warning,
        "insights": generate_insights(
            reciprocity,
            investimento,
            profundidade,
            weekly,
            open_q_ratio,
            diff_messages,
        ),
    }


def generate_insights(reciprocity: float, investment: float, depth: float, weekly: list[dict[str, Any]], open_q_ratio: float, diff_messages: float) -> list[str]:
    insights = []
    if diff_messages > 20:
        insights.append("Há indícios de assimetria na dinâmica de comunicação.")
    if len(weekly) >= 3:
        totals = [sum(v for k, v in week.items() if k != "week") for week in weekly]
        if len(totals) >= 2 and totals[-1] < totals[-2]:
            insights.append("O engajamento recente apresenta leve desaceleração.")
    if open_q_ratio < 0.10:
        insights.append("As conversas estão mais funcionais do que exploratórias.")
    if reciprocity > 70:
        insights.append("A troca emocional mostra sinais de equilíbrio consistente.")
    if investment > 65 and depth > 60:
        insights.append("Há boa combinação entre presença afetiva e profundidade de diálogo.")
    if not insights:
        insights.append("A conexão está estável no momento, com espaço para evolução gradual.")
    return insights


def compute_interest_hp(reciprocity: float, investment: float, depth: float) -> float:
    return round((reciprocity * 0.40) + (investment * 0.35) + (depth * 0.25), 2)


def hearts_from_hp(hp: float) -> list[str]:
    hearts = []
    for i in range(10):
        threshold = i * 10
        if hp >= threshold + 10:
            hearts.append("full")
        elif hp >= threshold + 5:
            hearts.append("half")
        else:
            hearts.append("empty")
    return hearts


def dumps_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)
