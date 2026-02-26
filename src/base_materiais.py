from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class MaterialBase:
    codigo: str
    descricao: str
    unidade: str
    valor_unitario: float
    cod_servico: str = ""
    cod_simulador: str = ""


def materiais_padrao() -> list[dict[str, object]]:
    base = [
        MaterialBase("CC11400", "POSTE C11/400", "UN", 1850.00, "OBR.001", "SIM.001"),
        MaterialBase("IPOS.044", "INST. POSTE METÁLICO CLIENTE REG", "UN", 920.00, "OBR.002", "SIM.002"),
        MaterialBase("IPOS.298", "POSTES RETIRADOS COM LINHA VIVA 10 A 12", "UN", 540.00, "OBR.003", "SIM.003"),
        MaterialBase("IPOS.299", "POSTES RETIRADOS COM LINHA VIVA 13 A 15", "UN", 570.00, "OBR.004", "SIM.004"),
        MaterialBase("IEMT170", "2CUF3", "UN", 450.00, "ATV.001", "SIM.101"),
        MaterialBase("SECS1IMF", "S1", "UN", 210.00, "ATV.002", "SIM.102"),
        MaterialBase("ICA1002", "1/0 AWG (Poppy)", "M", 13.75, "CAB.001", "SIM.201"),
        MaterialBase("ICA1007", "1/0 AWG (Raven)", "M", 14.20, "CAB.002", "SIM.202"),
        MaterialBase("TRIMF45", "TRAFO 45 KVA", "UN", 18600.00, "OBR.010", "SIM.010"),
        MaterialBase("TRIMF75", "TRAFO 75 KVA", "UN", 24500.00, "OBR.011", "SIM.011"),
        MaterialBase("KITMONOREG", "MEDIDOR/MONO/UC", "UN", 180.00, "ATV.010", "SIM.110"),
        MaterialBase("POSTEMONOREG", "POSTE/MONO/UC", "UN", 530.00, "ATV.020", "SIM.120"),
    ]
    return [asdict(item) for item in base]
