"""Selecao portavel de solver para os modelos de otimizacao."""
from __future__ import annotations

import pulp


def resolver(modelo: pulp.LpProblem, msg: bool = False) -> int:
    """Resolve um modelo usando HiGHS e, como alternativa, CBC.

    HiGHS e priorizado por funcionar nativamente em macOS Apple Silicon,
    Linux e Windows. CBC permanece como fallback para ambientes que ja o
    possuem configurado.
    """
    candidatos = [
        ("HiGHS", lambda: pulp.HiGHS(msg=msg)),
        ("CBC", lambda: pulp.PULP_CBC_CMD(msg=msg)),
    ]
    erros = []

    for nome, criar in candidatos:
        try:
            solver = criar()
            if not solver.available():
                erros.append(f"{nome}: indisponivel")
                continue
            return modelo.solve(solver)
        except (OSError, pulp.PulpSolverError) as exc:
            erros.append(f"{nome}: {exc}")

    detalhes = "; ".join(erros) or "nenhum solver configurado"
    raise RuntimeError(
        "Nao foi possivel executar a otimizacao. "
        f"Verifique a instalacao de highspy/PuLP. Detalhes: {detalhes}"
    )
