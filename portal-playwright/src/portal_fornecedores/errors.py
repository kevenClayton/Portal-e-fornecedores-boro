"""Erros de domínio do robô."""


class CredencialPortalInvalida(RuntimeError):
  """Usuário/senha do portal rejeitados — exige correção manual e novo start."""
