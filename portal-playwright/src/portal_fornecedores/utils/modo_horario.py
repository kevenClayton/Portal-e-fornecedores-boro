"""Ritmo reduzido em horário de baixo uso (madrugada BR)."""

from __future__ import annotations

import random
from datetime import datetime
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")

# Defaults: 21:00 → 05:59 (America/Sao_Paulo)
HORA_INICIO_PADRAO = 21
HORA_FIM_PADRAO = 6
CADENCIA_NOTURNA_SEG = 180
FATOR_PAUSA_NOTURNO = 2.5
REUSO_PESQUISA_NOTURNO_SEG = 600


def agora_brasil() -> datetime:
  return datetime.now(FUSO_BRASIL)


def em_horario_reduzido(
  agora: Optional[datetime] = None,
  inicio_hora: int = HORA_INICIO_PADRAO,
  fim_hora: int = HORA_FIM_PADRAO,
) -> bool:
  """True de inicio_hora (inclusive) até fim_hora (exclusive), cruzando meia-noite."""
  momento = agora or agora_brasil()
  if momento.tzinfo is None:
    momento = momento.replace(tzinfo=FUSO_BRASIL)
  else:
    momento = momento.astimezone(FUSO_BRASIL)

  hora = momento.hour
  inicio = int(inicio_hora) % 24
  fim = int(fim_hora) % 24
  if inicio == fim:
    return False
  if inicio > fim:
    return hora >= inicio or hora < fim
  return inicio <= hora < fim


def _config_horario() -> Tuple[int, int, int, float, int]:
  """Lê settings se disponíveis; senão usa defaults."""
  try:
    from portal_fornecedores.config.settings import get_settings

    settings = get_settings()
    return (
      int(getattr(settings, "modo_noturno_inicio_hora", HORA_INICIO_PADRAO) or HORA_INICIO_PADRAO),
      int(getattr(settings, "modo_noturno_fim_hora", HORA_FIM_PADRAO) or HORA_FIM_PADRAO),
      int(getattr(settings, "modo_noturno_cadencia_seg", CADENCIA_NOTURNA_SEG) or CADENCIA_NOTURNA_SEG),
      float(getattr(settings, "modo_noturno_fator_pausa", FATOR_PAUSA_NOTURNO) or FATOR_PAUSA_NOTURNO),
      int(
        getattr(settings, "modo_noturno_reuso_pesquisa_seg", REUSO_PESQUISA_NOTURNO_SEG)
        or REUSO_PESQUISA_NOTURNO_SEG
      ),
    )
  except Exception:
    return (
      HORA_INICIO_PADRAO,
      HORA_FIM_PADRAO,
      CADENCIA_NOTURNA_SEG,
      FATOR_PAUSA_NOTURNO,
      REUSO_PESQUISA_NOTURNO_SEG,
    )


def modo_reduzido_ativo() -> bool:
  inicio, fim, *_resto = _config_horario()
  return em_horario_reduzido(inicio_hora=inicio, fim_hora=fim)


def cadencia_efetiva(cadencia_base: int) -> int:
  """De dia: cadência do painel. De noite: no mínimo a cadência noturna (~3 min)."""
  base = max(1, int(cadencia_base or 30))
  inicio, fim, cadencia_noite, *_resto = _config_horario()
  if not em_horario_reduzido(inicio_hora=inicio, fim_hora=fim):
    return base
  return max(base, max(60, int(cadencia_noite)))


def fator_pausa() -> float:
  inicio, fim, _cadencia, fator, _reuso = _config_horario()
  if not em_horario_reduzido(inicio_hora=inicio, fim_hora=fim):
    return 1.0
  return max(1.0, float(fator))


def reuso_pesquisa_efetivo(reuso_base: int) -> int:
  """Intervalo entre Pesquisar cheio; de noite força intervalo maior."""
  base = max(0, int(reuso_base or 0))
  inicio, fim, _cadencia, _fator, reuso_noite = _config_horario()
  if not em_horario_reduzido(inicio_hora=inicio, fim_hora=fim):
    return base
  return max(base, max(180, int(reuso_noite)))


def intervalo_aleatorio_ms(minimo_ms: int, maximo_ms: int) -> int:
  fator = fator_pausa()
  minimo = max(0, int(minimo_ms * fator))
  maximo = max(minimo, int(maximo_ms * fator))
  return random.randint(minimo, maximo)
