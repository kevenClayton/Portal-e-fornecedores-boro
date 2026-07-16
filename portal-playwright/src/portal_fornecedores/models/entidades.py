from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DadosRota:
  numero_documento: str
  data: str
  compartilhado: str
  prioridade: str
  tipo_transporte: str
  peso_total: str
  unidade_peso: str
  planta_origem: str
  cluster: str
  estado: str
  observacoes: str = ""
  valor_carga: str = ""
  tem_letra_b: bool = False
  clientes_mesmo_destino: str = ""
  mais_de_um_destino: bool = False


@dataclass
class DadosMotorista:
  id_banco: int
  placa: str
  cpf: str
  nome: str
  aceita_bobina: bool
  situacao: bool
  ordem_motorista: int = 100
  placa_carreta: str = ""


@dataclass
class ParametrosOperacao:
  limite_valor_truck: float
  limite_valor_toco: float
  limite_valor_carreta: float
  modo_teste: bool
  email_notificacao: str
  intervalo_espera_seg: int = 30


@dataclass
class ConfiguracaoBusca:
  verificar_valor_carga: bool = True
  verificar_bobina: bool = True
  verificar_multiplos_destinos: bool = True
  tempo_espera_seg: int = 30
