import json
import os
import random
import time
from urllib import error, request
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class DemonRecord:
    name: str
    rank: str
    legions: Optional[int]
    domains: List[str]
    source: str


class SystemConfig:
    VERSION = "v2.2.0"
    DEMON_COUNT = 72
    GLITCH_CHANCE = 0.08
    TYPE_DELAY = 0.01
    ENABLE_COLORS = True
    ENABLE_BELL = True
    SESSION_FILE = Path("session_goetia.json")

    # Integração opcional com API local Ollama (DeepSeek).
    ENABLE_LLM = os.getenv("GOETIA_ENABLE_LLM", "1") == "1"
    OLLAMA_URL = os.getenv("GOETIA_OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    OLLAMA_MODEL = os.getenv("GOETIA_MODEL", "deepseek-r1:8b")
    OLLAMA_TIMEOUT_S = int(os.getenv("GOETIA_OLLAMA_TIMEOUT", "45"))


class GrimoireDatabase:
    """
    Base baseada em referências históricas reais:
    - The Lesser Key of Solomon, Ars Goetia (S. L. MacGregor Mathers; Aleister Crowley, 1904).
    - Pseudomonarchia Daemonum (Johann Weyer, 1563).
    - Dictionnaire Infernal (Collin de Plancy, 1818/1863).

    Observação:
    - A lista de 72 nomes e hierarquias segue a tradição da Ars Goetia.
    - Alguns números de legiões variam por edição/tradução; quando incerto, usamos None.
    """

    def __init__(self):
        self.demons = self._load_demon_data()
        self.texts = self._load_grimoire_texts()
        self.references = self._load_references()

    def _load_references(self) -> Dict[str, str]:
        return {
            "ars_goetia": "Mathers, S. L. MacGregor; Crowley, A. (1904). The Lesser Key of Solomon - Ars Goetia.",
            "weyer": "Weyer, J. (1563). Pseudomonarchia Daemonum.",
            "plancy": "de Plancy, J. C. (1863). Dictionnaire Infernal.",
        }

    def _base_goetia_names(self) -> List[str]:
        return [
            "BAEL", "AGARES", "VASSAGO", "SAMIGINA", "MARBAS", "VALEFOR", "AMON", "BARBATOS",
            "PAIMON", "BUER", "GUSION", "SITRI", "BELETH", "LERAJE", "ELIGOS", "ZEPAR",
            "BOTIS", "BATHIN", "SALLOS", "PURSON", "MARAX", "IPOS", "AIM", "NABERIUS",
            "GLASYA_LABOLAS", "BUNE", "RONOVE", "BERITH", "ASTAROTH", "FORNEUS", "FORAS", "ASMODAY",
            "GAAP", "FURFUR", "MARCHOSIAS", "STOLAS", "PHENEX", "HALPHAS", "MALPHAS", "RAUM",
            "FOCALOR", "VEPAR", "SABNOCK", "SHAX", "VINE", "BIFRONS", "UVALL", "HAAGENTI",
            "CROCELL", "FURCAS", "BALAM", "ALLOCES", "CAIM", "MURMUR", "OROBAS", "GREMORY",
            "OSÉ", "AMY", "ORIAS", "VAPULA", "ZAGAN", "VALAC", "ANDRAS", "FLAUROS",
            "ANDREALPHUS", "CIMEJES", "AMDUSCIAS", "BELIAL", "DECARABIA", "SEERE", "DANTALION", "ANDROMALIUS",
        ]

    def _load_demon_data(self) -> Dict[str, Dict[str, Any]]:
        # Dados principais (rank + legiões) para maior fidelidade histórica.
        canonical: Dict[str, DemonRecord] = {
            "BAEL": DemonRecord("BAEL", "Rei", 66, ["invisibilidade", "estratégia"], "ars_goetia"),
            "AGARES": DemonRecord("AGARES", "Duque", 31, ["linguagens", "movimento"], "ars_goetia"),
            "VASSAGO": DemonRecord("VASSAGO", "Príncipe", 26, ["adivinhação", "segredos"], "ars_goetia"),
            "SAMIGINA": DemonRecord("SAMIGINA", "Marquês", 30, ["artes liberais", "necromancia"], "ars_goetia"),
            "MARBAS": DemonRecord("MARBAS", "Presidente", 36, ["cura", "mecânica"], "ars_goetia"),
            "VALEFOR": DemonRecord("VALEFOR", "Duque", 10, ["astúcia", "alianças"], "ars_goetia"),
            "AMON": DemonRecord("AMON", "Marquês", 40, ["reconciliação", "profecia"], "ars_goetia"),
            "BARBATOS": DemonRecord("BARBATOS", "Duque", 30, ["natureza", "tesouros"], "ars_goetia"),
            "PAIMON": DemonRecord("PAIMON", "Rei", 200, ["artes", "ciências"], "ars_goetia"),
            "BUER": DemonRecord("BUER", "Presidente", 50, ["filosofia", "medicina"], "ars_goetia"),
            "GUSION": DemonRecord("GUSION", "Duque", 40, ["respostas", "honra"], "ars_goetia"),
            "SITRI": DemonRecord("SITRI", "Príncipe", 60, ["paixão", "segredos"], "ars_goetia"),
            "BELETH": DemonRecord("BELETH", "Rei", 85, ["afeição", "autoridade"], "ars_goetia"),
            "LERAJE": DemonRecord("LERAJE", "Marquês", 30, ["conflito", "arqueria"], "ars_goetia"),
            "ELIGOS": DemonRecord("ELIGOS", "Duque", 60, ["estratégia", "guerra"], "ars_goetia"),
            "ZEPAR": DemonRecord("ZEPAR", "Duque", 26, ["romance", "desafios"], "ars_goetia"),
            "BOTIS": DemonRecord("BOTIS", "Presidente/Conde", 60, ["mediação", "futuro"], "ars_goetia"),
            "BATHIN": DemonRecord("BATHIN", "Duque", 30, ["herbalismo", "viagens"], "ars_goetia"),
            "SALLOS": DemonRecord("SALLOS", "Duque", 30, ["amor", "diplomacia"], "ars_goetia"),
            "PURSON": DemonRecord("PURSON", "Rei", 22, ["tesouros", "segredos"], "ars_goetia"),
            "MARAX": DemonRecord("MARAX", "Conde/Presidente", 30, ["astronomia", "pedras"], "ars_goetia"),
            "IPOS": DemonRecord("IPOS", "Conde/Príncipe", 36, ["coragem", "insight"], "ars_goetia"),
            "AIM": DemonRecord("AIM", "Duque", 26, ["retórica", "fogo simbólico"], "ars_goetia"),
            "NABERIUS": DemonRecord("NABERIUS", "Marquês", 19, ["retórica", "restauração"], "ars_goetia"),
            "GLASYA_LABOLAS": DemonRecord("GLASYA_LABOLAS", "Presidente/Conde", 36, ["estratégia", "informação"], "ars_goetia"),
            "BUNE": DemonRecord("BUNE", "Duque", 30, ["eloquência", "riqueza"], "ars_goetia"),
            "RONOVE": DemonRecord("RONOVE", "Marquês/Conde", 19, ["línguas", "retórica"], "ars_goetia"),
            "BERITH": DemonRecord("BERITH", "Duque", 26, ["alquimia", "dignidades"], "ars_goetia"),
            "ASTAROTH": DemonRecord("ASTAROTH", "Duque", 40, ["conhecimento", "passado"], "ars_goetia"),
            "FORNEUS": DemonRecord("FORNEUS", "Marquês", 29, ["línguas", "reputação"], "ars_goetia"),
            "FORAS": DemonRecord("FORAS", "Presidente", 29, ["lógica", "tesouros"], "ars_goetia"),
            "ASMODAY": DemonRecord("ASMODAY", "Rei", 72, ["matemática", "artes"], "ars_goetia"),
            "GAAP": DemonRecord("GAAP", "Príncipe/Presidente", 66, ["filosofia", "transição"], "ars_goetia"),
            "FURFUR": DemonRecord("FURFUR", "Conde", 26, ["tempestades", "amor"], "ars_goetia"),
            "MARCHOSIAS": DemonRecord("MARCHOSIAS", "Marquês", 30, ["combate", "lealdade"], "ars_goetia"),
            "STOLAS": DemonRecord("STOLAS", "Príncipe", 26, ["astronomia", "botânica"], "ars_goetia"),
            "PHENEX": DemonRecord("PHENEX", "Marquês", 20, ["poesia", "música"], "ars_goetia"),
            "HALPHAS": DemonRecord("HALPHAS", "Conde", 26, ["fortificações", "estratégia"], "ars_goetia"),
            "MALPHAS": DemonRecord("MALPHAS", "Presidente", 40, ["arquitetura", "informação"], "ars_goetia"),
            "RAUM": DemonRecord("RAUM", "Conde", 30, ["diplomacia", "segredos"], "ars_goetia"),
            "FOCALOR": DemonRecord("FOCALOR", "Duque", 30, ["mares", "ventos"], "ars_goetia"),
            "VEPAR": DemonRecord("VEPAR", "Duque", 29, ["mares", "navegação"], "ars_goetia"),
            "SABNOCK": DemonRecord("SABNOCK", "Marquês", 50, ["defesa", "arquitetura"], "ars_goetia"),
            "SHAX": DemonRecord("SHAX", "Marquês", 30, ["percepção", "objetos"], "ars_goetia"),
            "VINE": DemonRecord("VINE", "Rei/Conde", 36, ["descoberta", "estratégia"], "ars_goetia"),
            "BIFRONS": DemonRecord("BIFRONS", "Conde", 6, ["ciências", "geometria"], "ars_goetia"),
            "UVALL": DemonRecord("UVALL", "Duque", 37, ["amizade", "passado"], "ars_goetia"),
            "HAAGENTI": DemonRecord("HAAGENTI", "Presidente", 33, ["alquimia", "sabedoria"], "ars_goetia"),
            "CROCELL": DemonRecord("CROCELL", "Duque", 48, ["geometria", "águas"], "ars_goetia"),
            "FURCAS": DemonRecord("FURCAS", "Cavaleiro", 20, ["filosofia", "retórica"], "ars_goetia"),
            "BALAM": DemonRecord("BALAM", "Rei", 40, ["insight", "estratégia"], "ars_goetia"),
            "ALLOCES": DemonRecord("ALLOCES", "Duque", 36, ["astronomia", "ética"], "ars_goetia"),
            "CAIM": DemonRecord("CAIM", "Presidente", 30, ["compreensão", "vozes"], "ars_goetia"),
            "MURMUR": DemonRecord("MURMUR", "Duque/Conde", 30, ["filosofia", "espíritos"], "ars_goetia"),
            "OROBAS": DemonRecord("OROBAS", "Príncipe", 20, ["verdade", "futuro"], "ars_goetia"),
            "GREMORY": DemonRecord("GREMORY", "Duque", 26, ["afeto", "tesouros"], "ars_goetia"),
            "OSÉ": DemonRecord("OSÉ", "Presidente", 30, ["insight", "ciências"], "ars_goetia"),
            "AMY": DemonRecord("AMY", "Presidente", 36, ["astrologia", "tesouros"], "ars_goetia"),
            "ORIAS": DemonRecord("ORIAS", "Marquês", 30, ["astrologia", "dignidades"], "ars_goetia"),
            "VAPULA": DemonRecord("VAPULA", "Duque", 36, ["artesanato", "filosofia"], "ars_goetia"),
            "ZAGAN": DemonRecord("ZAGAN", "Rei/Presidente", 33, ["alquimia", "transformação"], "ars_goetia"),
            "VALAC": DemonRecord("VALAC", "Presidente", 38, ["tesouros", "serpentes"], "ars_goetia"),
            "ANDRAS": DemonRecord("ANDRAS", "Marquês", 30, ["discórdia", "estratégia"], "ars_goetia"),
            "FLAUROS": DemonRecord("FLAUROS", "Duque", 36, ["verdade", "proteção"], "ars_goetia"),
            "ANDREALPHUS": DemonRecord("ANDREALPHUS", "Marquês", 30, ["geometria", "astronomia"], "ars_goetia"),
            "CIMEJES": DemonRecord("CIMEJES", "Marquês", 20, ["gramática", "descoberta"], "ars_goetia"),
            "AMDUSCIAS": DemonRecord("AMDUSCIAS", "Duque", 29, ["música", "harmonia"], "ars_goetia"),
            "BELIAL": DemonRecord("BELIAL", "Rei", 80, ["retórica", "influência"], "ars_goetia"),
            "DECARABIA": DemonRecord("DECARABIA", "Marquês", 30, ["aves", "pedras"], "ars_goetia"),
            "SEERE": DemonRecord("SEERE", "Príncipe", 26, ["velocidade", "logística"], "ars_goetia"),
            "DANTALION": DemonRecord("DANTALION", "Duque", 36, ["psicologia", "persuasão"], "ars_goetia"),
            "ANDROMALIUS": DemonRecord("ANDROMALIUS", "Conde", 36, ["justiça", "recuperação"], "ars_goetia"),
        }

        final_data: Dict[str, Dict[str, Any]] = {}
        for name in self._base_goetia_names():
            rec = canonical.get(name)
            if rec is None:
                rec = DemonRecord(
                    name=name,
                    rank="Não especificado",
                    legions=None,
                    domains=["ver referência histórica"],
                    source="ars_goetia",
                )

            final_data[name] = {
                "rank": rec.rank,
                "legions": rec.legions,
                "attributes": rec.domains,
                "description": f"Ser infernal catalogado na tradição goética ({rec.rank}).",
                "sigil": self._procedural_sigil(name),
                "lore": f"{name} consta entre os 72 espíritos infernais da Ars Goetia; variantes textuais existem por edição.",
                "source": self.references_key_to_text(rec.source),
                "nature": "espírito infernal (tradição goética)",
            }

        return final_data

    def references_key_to_text(self, key: str) -> str:
        refs = self._load_references()
        return refs.get(key, key)

    def _procedural_sigil(self, name: str) -> str:
        # Sigilo textual procedural em grade (melhor legibilidade em terminais e .bat).
        digest = sha1(name.encode("utf-8")).hexdigest()
        bits = "".join(f"{int(ch, 16):04b}" for ch in digest[:16])
        size = 9
        canvas = [[" " for _ in range(size)] for _ in range(size)]

        idx = 0
        for y in range(size):
            for x in range((size + 1) // 2):
                on = bits[idx % len(bits)] == "1"
                idx += 1
                char = "✦" if on else "·"
                canvas[y][x] = char
                canvas[y][size - 1 - x] = char

        lines = ["┌" + "─" * size + "┐"]
        for row in canvas:
            lines.append("│" + "".join(row) + "│")
        lines.append("└" + "─" * size + "┘")
        lines.append(f"⟮{name}⟯")
        return "\n".join(lines)

    def _load_grimoire_texts(self) -> Dict[str, str]:
        return {
            "ars_goetia": (
                "A Ars Goetia descreve 72 espíritos com títulos, legiões e instruções rituais. "
                "Edições diferem em ortografia, ordenação e detalhes de legiões."
            ),
            "pseudomonarchia": (
                "A Pseudomonarchia Daemonum (1563) antecede a redação moderna da Goetia e "
                "apresenta catálogo parcialmente sobreposto de entidades e atributos."
            ),
            "dictionnaire_infernal": (
                "O Dictionnaire Infernal de de Plancy compila demonologia europeia e iconografia "
                "do século XIX, útil como comparação histórica, não como fonte única."
            ),
        }

    def get_demon(self, name: str) -> Dict[str, Any]:
        return self.demons.get(name.upper(), {})

    def list_all_demons(self) -> List[str]:
        return list(self.demons.keys())


class DarkTerminal:
    def __init__(self):
        self.colors = self._init_colors()
        self.glitch_chars = "▓▒░╬╣║╗╝╚╔╩╦╠═╒▄▌▐▀"

    def _init_colors(self) -> Dict[str, str]:
        if not SystemConfig.ENABLE_COLORS:
            return {k: "" for k in ["blood", "dark_red", "green", "yellow", "blue", "purple", "cyan", "white", "reset"]}
        return {
            "blood": "\033[91m",
            "dark_red": "\033[31m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m",
        }

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def beep(self):
        if SystemConfig.ENABLE_BELL:
            print("\a", end="", flush=True)

    def typewriter_effect(self, text: str, delay: Optional[float] = None):
        delay = SystemConfig.TYPE_DELAY if delay is None else delay
        for char in text:
            if random.random() < SystemConfig.GLITCH_CHANCE:
                print(random.choice(self.glitch_chars), end="", flush=True)
                print("\b", end="", flush=True)
            print(char, end="", flush=True)
            time.sleep(delay)
        print()

    def print_blood_text(self, text: str):
        print(f"{self.colors['blood']}{text}{self.colors['reset']}")

    def print_error(self, text: str):
        print(f"{self.colors['dark_red']}>>> ERRO: {text}{self.colors['reset']}")

    def print_banner(self):
        print(f"{self.colors['blood']}\n=== SISTEMA GOÉTICO DIGITAL {SystemConfig.VERSION} ==={self.colors['reset']}")


class RitualSystem:
    def __init__(self, terminal: DarkTerminal):
        self.terminal = terminal
        self.rituals = {
            "full_invocation": {"steps": 5, "duration": 4.0},
            "simple_contact": {"steps": 3, "duration": 2.0},
            "divination": {"steps": 4, "duration": 3.0},
        }

    def perform_ritual(self, ritual_type: str, demon_name: str) -> bool:
        ritual = self.rituals.get(ritual_type)
        if not ritual:
            return False

        self.terminal.typewriter_effect(f"INICIANDO RITUAL [{ritual_type}] PARA {demon_name}...")
        step_texts = [
            "PREPARANDO CÍRCULO...",
            "ENTOANDO CHAMADO...",
            "TRAÇANDO SIGILO...",
            "ESTABELECENDO CONTATO...",
            "RITUAL FINALIZADO.",
        ]

        for idx in range(ritual["steps"]):
            text = step_texts[min(idx, len(step_texts) - 1)]
            self.terminal.print_blood_text(f"PASSO {idx + 1}/{ritual['steps']}: {text}")
            self.terminal.beep()
            time.sleep(ritual["duration"] / ritual["steps"])
        return True


class DemonPersonality:
    def __init__(self, grimoire_db: GrimoireDatabase):
        self.db = grimoire_db
        self.rank_voice = {
            "Rei": "majestoso, imperativo, soberano",
            "Duque": "diplomático, estratégico, aristocrático",
            "Príncipe": "oracular, enigmático, elevado",
            "Marquês": "bélico, cortante, tático",
            "Conde": "calculista, reservado, observador",
            "Presidente": "instrutivo, racional, técnico",
            "Cavaleiro": "severo, disciplinado, direto",
        }

    def build_prompt(self, demon_name: str, user_message: str) -> Dict[str, str]:
        demon = self.db.get_demon(demon_name)
        if not demon:
            return {
                "system": "Você é um oráculo textual infernal da tradição goética.",
                "user": user_message,
            }

        attrs = ", ".join(demon.get("attributes", [])[:4])
        rank = demon.get("rank", "Entidade")
        voice = self.rank_voice.get(rank.split("/")[0], "ritualístico e sombrio")
        lore = demon.get("lore", "")
        system_prompt = (
            f"Você deve responder em português, em primeira pessoa como {demon_name}, "
            f"ser infernal da Ars Goetia. Rank: {rank}. Voz: {voice}. "
            f"Domínios: {attrs}. Lore: {lore}. "
            "Mantenha tom ritualístico, coerente com tradição infernal, sem quebrar personagem. "
            "Seja conciso (4-8 linhas), evocativo e objetivo."
        )
        return {"system": system_prompt, "user": user_message}

    def get_demon_response(self, demon_name: str, user_message: str) -> str:
        demon = self.db.get_demon(demon_name)
        if not demon:
            return "ENTIDADE NÃO REGISTRADA NO GRIMÓRIO."

        attrs = demon.get("attributes", [])
        rank = demon.get("rank", "Entidade")
        style = attrs[0] if attrs else "mistério"
        style2 = attrs[1] if len(attrs) > 1 else "sabedoria"

        openings = [
            "Escuto tua pergunta através do círculo.",
            "As linhas do selo respondem ao teu chamado.",
            "A consulta foi recebida no domínio ritual.",
            "Teu verbo ecoou no triângulo da arte.",
            "Sob o selo, tua intenção tornou-se audível.",
        ]
        closings = [
            "Age com disciplina ritual e registra os sinais.",
            "Não rompas o círculo sem concluir tua intenção.",
            "Confirma o resultado por prática e observação.",
            "Firme tua vontade e evita contradições no rito.",
            "Sela a operação com clareza e silêncio.",
        ]

        idx = abs(hash(f"{demon_name}:{user_message.lower()}")) % len(openings)
        cidx = abs(hash(f"{user_message.lower()}:{demon_name}")) % len(closings)
        opening = openings[idx]
        closing = closings[cidx]

        return (
            f"[{demon_name} | {rank}] {opening} "
            f"Sou tratado na tradição como entidade infernal, atuando em {style} e {style2}. "
            f"Sobre tua pergunta '{user_message}', respondo no enquadramento ritual. "
            f"{closing}"
        )


class SessionStore:
    @staticmethod
    def save(path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}


class GoeticChatSystem:
    def __init__(self):
        self.grimoire_db = GrimoireDatabase()
        self.terminal = DarkTerminal()
        self.ritual_sys = RitualSystem(self.terminal)
        self.demon_personality = DemonPersonality(self.grimoire_db)
        self.active_demon: Optional[str] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.participants: List[str] = ["Operador"]
        self.last_response_source = "fallback"
        self._load_session()

    def _serialize(self) -> Dict[str, Any]:
        return {
            "active_demon": self.active_demon,
            "conversation_history": self.conversation_history,
            "participants": self.participants,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

    def _load_session(self):
        data = SessionStore.load(SystemConfig.SESSION_FILE)
        if not data:
            return
        self.active_demon = data.get("active_demon")
        self.conversation_history = data.get("conversation_history", [])
        self.participants = data.get("participants", ["Operador"])

    def _save_session(self):
        SessionStore.save(SystemConfig.SESSION_FILE, self._serialize())

    def _ollama_available(self) -> bool:
        if not SystemConfig.ENABLE_LLM:
            return False

        payload = {
            "model": SystemConfig.OLLAMA_MODEL,
            "prompt": "responda apenas: ok",
            "stream": False,
            "options": {"temperature": 0},
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            SystemConfig.OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=min(8, SystemConfig.OLLAMA_TIMEOUT_S)) as resp:
                parsed = json.loads(resp.read().decode("utf-8"))
                return bool((parsed.get("response") or "").strip())
        except (error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return False

    def _query_ollama(self, demon_name: str, user_message: str) -> Optional[str]:
        if not SystemConfig.ENABLE_LLM:
            return None

        prompt_pack = self.demon_personality.build_prompt(demon_name, user_message)
        payload = {
            "model": SystemConfig.OLLAMA_MODEL,
            "prompt": f"[SYSTEM] {prompt_pack['system']}\n[USER] {prompt_pack['user']}\n[ASSISTANT]",
            "stream": False,
            "options": {"temperature": 0.8, "top_p": 0.9},
        }

        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            SystemConfig.OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=SystemConfig.OLLAMA_TIMEOUT_S) as resp:
                parsed = json.loads(resp.read().decode("utf-8"))
                text = (parsed.get("response") or "").strip()
                return text or None
        except (error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return None

    def generate_response(self, demon_name: str, message: str) -> str:
        llm_text = self._query_ollama(demon_name, message)
        if llm_text:
            self.last_response_source = "ollama"
            return llm_text
        self.last_response_source = "fallback"
        return self.demon_personality.get_demon_response(demon_name, message)

    def startup_sequence(self):
        self.terminal.clear_screen()
        self.terminal.print_banner()
        self.terminal.typewriter_effect("Base carregada com 72 entidades da Ars Goetia.")
        self.terminal.typewriter_effect("Use HELP para comandos e REFERENCES para fontes históricas.")
        self.main_menu()

    def main_menu(self):
        while True:
            try:
                cmd = input("\nGOETIA:// ").strip()
            except (EOFError, KeyboardInterrupt):
                self.shutdown_sequence()
                break

            if not cmd:
                continue
            upper = cmd.upper()

            if upper == "QUIT":
                self.shutdown_sequence()
                break
            if upper == "HELP":
                self.show_help()
            elif upper == "LIST":
                self.list_demons()
            elif upper.startswith("INVOKE "):
                self.invoke_demon(cmd.split(maxsplit=1)[1])
            elif upper == "CHAT":
                self.chat_with_demon()
            elif upper.startswith("ASK "):
                self.ask_once(cmd.split(maxsplit=1)[1])
            elif upper.startswith("PROFILE "):
                self.show_demon_profile(cmd.split(maxsplit=1)[1])
            elif upper == "GRIMOIRE":
                self.consult_grimoire()
            elif upper == "HISTORY":
                self.show_history()
            elif upper == "CLEAR":
                self.clear_session()
            elif upper == "REFERENCES":
                self.show_references()
            elif upper == "RITUAL":
                self.start_ritual_menu()
            elif upper == "MULTI":
                self.multiplayer_mode()
            elif upper == "SAVE":
                self._save_session()
                self.terminal.typewriter_effect("Sessão salva.")
            elif upper == "LOAD":
                self._load_session()
                self.terminal.typewriter_effect("Sessão carregada.")
            elif upper == "MODEL":
                self.show_model_status()
            elif upper == "HEALTH":
                self.health_check()
            else:
                self.terminal.print_error("Comando inválido. Digite HELP.")

    def show_help(self):
        print(
            "\nComandos: LIST | PROFILE <nome> | INVOKE <nome> | ASK <mensagem> | RITUAL | CHAT | MULTI | GRIMOIRE | REFERENCES | "
            "HISTORY | SAVE | LOAD | CLEAR | MODEL | HEALTH | HELP | QUIT"
        )

    def ask_once(self, message: str):
        message = message.strip()
        if not message:
            self.terminal.print_error("Mensagem vazia em ASK.")
            return

        # Para facilitar a conversa real imediata: se não houver ativo, usa PAIMON por padrão.
        if not self.active_demon:
            self.active_demon = "PAIMON"

        response = self.generate_response(self.active_demon, message)
        print(f"{self.active_demon} [{self.last_response_source}]: {response}")
        self.conversation_history.append(
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "type": "ASK",
                "demon": self.active_demon,
                "message": message,
                "response": response,
            }
        )
        self._save_session()


    def show_demon_profile(self, demon_name: str):
        key = demon_name.strip().upper()
        demon = self.grimoire_db.get_demon(key)
        if not demon:
            self.terminal.print_error(f"'{key}' não está no catálogo.")
            return

        self.terminal.print_blood_text(f"PERFIL GOÉTICO: {key}")
        print(f"Natureza: {demon.get('nature', 'N/D')}")
        print(f"Rank: {demon.get('rank', 'N/D')}")
        print(f"Legiões: {demon.get('legions', 'N/D')}")
        print(f"Domínios: {', '.join(demon.get('attributes', []))}")
        print(f"Descrição: {demon.get('description', '')}")
        print(f"Lore: {demon.get('lore', '')}")
        print(f"Fonte: {demon.get('source', '')}")
        print("Sigilo:")
        print(demon.get("sigil", ""))


    def show_model_status(self):
        state = "ATIVO" if SystemConfig.ENABLE_LLM else "INATIVO"
        api_online = self._ollama_available()
        print(f"LLM (config): {state}")
        print(f"API Ollama (conectividade): {'ONLINE' if api_online else 'OFFLINE'}")
        print(f"Modelo: {SystemConfig.OLLAMA_MODEL}")
        print(f"Endpoint: {SystemConfig.OLLAMA_URL}")
        print(f"Última fonte de resposta: {self.last_response_source}")
        if SystemConfig.ENABLE_LLM and not api_online:
            print("Dica: inicie o Ollama e rode o modelo DeepSeek localmente para sair do fallback.")

    def health_check(self):
        print("[HEALTH] Verificando subsistemas...")
        print(f"- Entidades carregadas: {len(self.grimoire_db.list_all_demons())}/{SystemConfig.DEMON_COUNT}")
        print(f"- LLM habilitado (config): {SystemConfig.ENABLE_LLM}")
        if self._ollama_available():
            print("- API Ollama: ONLINE (respondeu)")
        else:
            print("- API Ollama: OFFLINE/indisponível (usando fallback local)")

    def show_references(self):
        self.terminal.print_blood_text("REFERÊNCIAS HISTÓRICAS")
        for _, ref in self.grimoire_db.references.items():
            print(f"- {ref}")

    def list_demons(self):
        demons = self.grimoire_db.list_all_demons()
        self.terminal.print_blood_text(f"REGISTRO GOÉTICO: {len(demons)} ENTIDADES")
        for i, demon in enumerate(demons, start=1):
            info = self.grimoire_db.get_demon(demon)
            legions = info.get("legions")
            legions_txt = str(legions) if legions is not None else "N/D"
            print(f"{i:02d}. {demon:<14} | {info.get('rank','N/D'):<18} | legiões: {legions_txt}")

    def invoke_demon(self, demon_name: str):
        demon_name = demon_name.strip().upper()
        demon = self.grimoire_db.get_demon(demon_name)
        if not demon:
            self.terminal.print_error(f"'{demon_name}' não está no catálogo.")
            return

        ok = self.ritual_sys.perform_ritual("full_invocation", demon_name)
        if not ok:
            self.terminal.print_error("Falha ritualística.")
            return

        self.active_demon = demon_name
        self.terminal.print_blood_text(f"{demon_name} ATIVO")
        print(demon["sigil"])
        print(f"Fonte: {demon.get('source')}")
        self.conversation_history.append(
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "type": "INVOCATION",
                "demon": demon_name,
                "message": f"{demon_name} invocado",
            }
        )
        self._save_session()

    def start_ritual_menu(self):
        if not self.active_demon:
            self.terminal.print_error("Ative um demônio com INVOKE <nome> primeiro.")
            return

        print("\n1) Invocação completa\n2) Contato simples\n3) Divinação")
        choice = input("Escolha: ").strip()
        mapping = {"1": "full_invocation", "2": "simple_contact", "3": "divination"}
        ritual = mapping.get(choice)
        if not ritual:
            self.terminal.print_error("Opção inválida.")
            return
        self.ritual_sys.perform_ritual(ritual, self.active_demon)

    def chat_with_demon(self):
        if not self.active_demon:
            self.terminal.print_error("Nenhum demônio ativo.")
            return

        print("Digite SAIR para voltar.")
        while True:
            msg = input("VOCÊ: ").strip()
            if msg.upper() == "SAIR":
                break
            if not msg:
                continue

            response = self.generate_response(self.active_demon, msg)
            print(f"{self.active_demon} [{self.last_response_source}]: {response}")
            self.conversation_history.append(
                {
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "type": "CHAT",
                    "demon": self.active_demon,
                    "message": msg,
                    "response": response,
                }
            )
        self._save_session()

    def multiplayer_mode(self):
        if not self.active_demon:
            self.terminal.print_error("Nenhum demônio ativo.")
            return

        print("Modo multiplayer local (turnos). Nomes atuais:", ", ".join(self.participants))
        add = input("Adicionar participantes (separados por vírgula) ou ENTER: ").strip()
        if add:
            extras = [p.strip() for p in add.split(",") if p.strip()]
            self.participants.extend(extras)
            self.participants = sorted(set(self.participants))

        print("Digite SAIR para encerrar MULTI.")
        turn = 0
        while True:
            player = self.participants[turn % len(self.participants)]
            msg = input(f"{player}: ").strip()
            if msg.upper() == "SAIR":
                break
            if not msg:
                turn += 1
                continue

            response = self.generate_response(self.active_demon, msg)
            print(f"{self.active_demon} [{self.last_response_source}] -> {player}: {response}")
            self.conversation_history.append(
                {
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "type": "MULTI_CHAT",
                    "player": player,
                    "demon": self.active_demon,
                    "message": msg,
                    "response": response,
                }
            )
            turn += 1

        self._save_session()

    def consult_grimoire(self):
        self.terminal.print_blood_text("BIBLIOTECA")
        for title, text in self.grimoire_db.texts.items():
            print(f"\n--- {title.upper()} ---\n{text}")

    def show_history(self):
        if not self.conversation_history:
            print("Sem histórico nesta sessão.")
            return

        for item in self.conversation_history[-30:]:
            print(f"[{item.get('timestamp')}] {item.get('type')} - {item.get('demon', '-')}: {item.get('message', '')}")

    def clear_session(self):
        self.active_demon = None
        self.conversation_history = []
        self.participants = ["Operador"]
        self._save_session()
        self.terminal.typewriter_effect("Sessão limpa.")

    def shutdown_sequence(self):
        self._save_session()
        self.terminal.typewriter_effect("Encerrando portal e salvando sessão...")


def main():
    system = GoeticChatSystem()
    system.startup_sequence()


if __name__ == "__main__":
    main()
