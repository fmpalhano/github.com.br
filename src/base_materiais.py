from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialBase:
    codigo: str
    descricao: str
    unidade: str
    valor_unitario: float


BASE_MATERIAIS: tuple[MaterialBase, ...] = (
    MaterialBase("CC11400", "POSTE C11/400", "UN", 1850.00),
    MaterialBase("IPOS.044", "INST. POSTE METÁLICO CLIENTE REG", "UN", 920.00),
    MaterialBase("IPOS.298", "POSTES RETIRADOS COM LINHA VIVA 10 A 12", "UN", 540.00),
    MaterialBase("IPOS.299", "POSTES RETIRADOS COM LINHA VIVA 13 A 15", "UN", 570.00),
    MaterialBase("IPOS.296", "N1/M1/B1/T1/E1 ENERGIZADA PRIMÁRIA", "UN", 760.00),
    MaterialBase("IPOS.297", "N2/M2/B2/T2/E2 ENERGIZADA PRIMÁRIA", "UN", 810.00),
    MaterialBase("IPOS.010", "N3/M3/B3/T3/E3 ENERGIZADA PRIMÁRIA", "UN", 890.00),
    MaterialBase("IPOS.014", "N4/B4/M4/T4/E4 ENERGIZADA PRIMÁRIA", "UN", 980.00),
    MaterialBase("IEMT170", "2CUF3", "UN", 450.00),
    MaterialBase("IEMT100", "B1", "UN", 390.00),
    MaterialBase("SECS1IMF", "S1", "UN", 210.00),
    MaterialBase("SECS3IMF", "S3", "UN", 230.00),
    MaterialBase("ICA1002", "1/0 AWG (Poppy)", "M", 13.75),
    MaterialBase("ICA1007", "1/0 AWG (Raven)", "M", 14.20),
    MaterialBase("ICA1001", "2 AWG (Iris)", "M", 9.80),
    MaterialBase("ICA1006", "2 AWG (Sparrow)", "M", 10.10),
    MaterialBase("ICA1073", "246,9 MCM 7FI (Allience)", "M", 29.40),
    MaterialBase("TRIMF45", "TRAFO 45 KVA", "UN", 18600.00),
    MaterialBase("TRIMF75", "TRAFO 75 KVA", "UN", 24500.00),
    MaterialBase("KITMONOREG", "MEDIDOR/MONO/UC", "UN", 180.00),
    MaterialBase("KITBIREG", "MEDIDOR/BI/UC", "UN", 240.00),
    MaterialBase("POSTEMONOREG", "POSTE/MONO/UC", "UN", 530.00),
    MaterialBase("POSTEBIREG", "POSTE/BI/UC", "UN", 690.00),
)
