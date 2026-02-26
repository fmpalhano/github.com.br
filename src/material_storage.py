from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.base_materiais import materiais_padrao


@dataclass(frozen=True)
class Material:
    codigo: str
    descricao: str
    unidade: str
    valor_unitario: float
    cod_servico: str = ""
    cod_simulador: str = ""


def _to_material(item: dict[str, object]) -> Material:
    return Material(
        codigo=str(item.get("codigo", "")).strip(),
        descricao=str(item.get("descricao", "")).strip(),
        unidade=str(item.get("unidade", "")).strip(),
        valor_unitario=float(item.get("valor_unitario", 0.0)),
        cod_servico=str(item.get("cod_servico", "")).strip(),
        cod_simulador=str(item.get("cod_simulador", "")).strip(),
    )


class MaterialStorage:
    def __init__(self, caminho: Path) -> None:
        self.caminho = caminho

    def carregar(self) -> list[Material]:
        if not self.caminho.exists():
            self.salvar([_to_material(item) for item in materiais_padrao()])
        dados = json.loads(self.caminho.read_text(encoding="utf-8"))
        return [_to_material(item) for item in dados]

    def salvar(self, materiais: list[Material]) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        serializado = [
            {
                "codigo": m.codigo,
                "descricao": m.descricao,
                "unidade": m.unidade,
                "valor_unitario": m.valor_unitario,
                "cod_servico": m.cod_servico,
                "cod_simulador": m.cod_simulador,
            }
            for m in materiais
        ]
        self.caminho.write_text(json.dumps(serializado, ensure_ascii=False, indent=2), encoding="utf-8")
