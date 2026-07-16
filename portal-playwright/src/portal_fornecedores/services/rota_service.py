import logging
from typing import Callable, Optional

from portal_fornecedores.browser.pages.cargas_page import CargasPage
from portal_fornecedores.browser.pages.detalhes_carga_page import DetalhesCargaPage
from portal_fornecedores.browser.pages.login_page import LoginPage
from portal_fornecedores.browser.pages.vinculacao_page import VinculacaoPage
from portal_fornecedores.database.repositories.dados_repository import DadosRepository
from portal_fornecedores.models.entidades import ConfiguracaoBusca, DadosRota, ParametrosOperacao
from portal_fornecedores.services.email_service import EmailService
from portal_fornecedores.services.vinculacao_service import VinculacaoService

logger = logging.getLogger(__name__)


class RotaService:
  """Orquestra o mesmo fluxo do main.py + ListandoRotas2 legado."""

  def __init__(
    self,
    login_page: LoginPage,
    cargas_page: CargasPage,
    detalhes_page: DetalhesCargaPage,
    vinculacao_page: VinculacaoPage,
    repository: DadosRepository,
    email_service: EmailService,
    on_status: Optional[Callable[[str], None]] = None,
  ):
    self._login = login_page
    self._cargas = cargas_page
    self._detalhes = detalhes_page
    self._vinculacao_page = vinculacao_page
    self._repo = repository
    self._email = email_service
    self._on_status = on_status or (lambda msg: None)
    self._parametros: Optional[ParametrosOperacao] = None
    self._ativo = True

  def parar(self) -> None:
    self._ativo = False

  def executar_ciclo(self, config: ConfiguracaoBusca) -> None:
    """
    Espelha o loop do main.py legado:
      1. Verifica se está logado
      2. Se não → login
      3. listarTodasRotas (empresa 85 → SUCargaProgramada → Pesquisa)
      4. verificarSeExisteDestinoEFiltrar (clusters do portal ∩ banco)
      5. Para cada carga: detalhes → validar → vincular
    """
    if not self._ativo:
      return

    self._parametros = self._repo.obter_parametros()
    self._repo.limpar_processados_antigos(horas=24)
    usuario, senha = self._repo.obter_login()

    # --- 1) Login (igual fazendoLogin.py + main.py) ---
    self._status("Verificando se esta logado...")
    logado = self._login.esta_logado()

    if not logado:
      if not self._ativo:
        return
      self._status("Fazendo login...")
      self._login.fazer_login(usuario, senha)
    else:
      self._status("Sessao ativa")

    if not self._ativo:
      return

    # --- 2) listarTodasRotas ---
    self._cargas.listar_todas_rotas(config.tempo_espera_seg, on_status=self._status)

    if not self._ativo:
      return

    # --- 3) verificarSeExisteDestinoEFiltrar ---
    self._verificar_destinos_e_filtrar(config)

  def _verificar_destinos_e_filtrar(self, config: ConfiguracaoBusca) -> None:
    destinos_banco = {
      nome.strip().lower()
      for nome in self._repo.obter_destinos_motoristas_ativos()
    }
    self._status(f"Destinos ativos no banco: {len(destinos_banco)}")

    clusters_portal = self._cargas.obter_clusters_portal()
    if not clusters_portal:
      self._status("Nenhum cluster encontrado no portal")
      return

    existentes = 0
    inexistentes = 0

    for cluster in clusters_portal:
      if not self._ativo:
        return

      cluster_limpo = cluster.strip()
      if not cluster_limpo:
        continue

      if cluster_limpo.lower() not in destinos_banco:
        inexistentes += 1
        self._status(f"Cluster nao existente na base: {cluster_limpo}")
        continue

      existentes += 1
      self._status(f"Verificando cluster existente: {cluster_limpo}")

      if not self._cargas.selecionar_cluster(cluster_limpo):
        logger.warning("Nao foi possivel selecionar cluster: %s", cluster_limpo)
        continue

      self._cargas.aplicar_filtro()
      self._processar_resultados_rota(cluster_limpo, config)

    self._status(
      f"Resumo filtros — existentes: {existentes} | inexistentes: {inexistentes} | total: {len(clusters_portal)}"
    )

    if existentes == 0:
      self._status("Nenhuma planta do portal e atendida por motorista ativo no banco.")

  def _processar_resultados_rota(self, destino: str, config: ConfiguracaoBusca) -> None:
    vinculacao = VinculacaoService(
      self._cargas,
      self._detalhes,
      self._vinculacao_page,
      self._repo,
      self._email,
      self._parametros,
      self._on_status,
    )

    rotas = self._cargas.extrair_rotas_tabela()
    if not rotas:
      self._status(f"Nenhuma carga na tabela para cluster: {destino}")
      return

    self._status(f"{len(rotas)} carga(s) no cluster {destino}")
    tipos_veiculo = self._repo.obter_tipos_veiculo()

    for rota in rotas:
      if not self._ativo:
        return

      if self._repo.documento_ja_processado(rota.numero_documento):
        self._status(f"Ja processou documento: {rota.numero_documento}")
        continue

      self._status(
        f"Processando doc {rota.numero_documento} | {rota.tipo_transporte} | {rota.planta_origem} → {rota.cluster}"
      )
      rota = self._enriquecer_rota(rota, config)
      self._processar_rota_individual(rota, destino, tipos_veiculo, vinculacao)

  def _enriquecer_rota(self, rota: DadosRota, config: ConfiguracaoBusca) -> DadosRota:
    if config.verificar_valor_carga:
      try:
        self._status(f"Buscando valor da carga doc {rota.numero_documento}...")
        rota.valor_carga = self._detalhes.obter_valor_carga(rota.numero_documento)
        self._status(f"Valor carga: {rota.valor_carga or '(vazio)'}")
      except Exception as erro:
        logger.warning("Erro ao obter valor doc %s: %s", rota.numero_documento, erro)
        rota.valor_carga = ""

    if config.verificar_bobina:
      try:
        self._status(f"Verificando bobina doc {rota.numero_documento}...")
        rota.tem_letra_b = self._detalhes.verificar_tem_bobina(rota.numero_documento)
        self._status(f"Bobina (letra B): {rota.tem_letra_b}")
      except Exception as erro:
        logger.warning("Erro ao verificar bobina doc %s: %s", rota.numero_documento, erro)
        rota.tem_letra_b = False

    if config.verificar_multiplos_destinos:
      try:
        self._status(f"Verificando multiplos destinos doc {rota.numero_documento}...")
        mesmo_destino, municipios, contador = self._detalhes.verificar_multiplos_destinos(
          rota.numero_documento
        )
        rota.clientes_mesmo_destino = municipios
        rota.mais_de_um_destino = not mesmo_destino and contador > 1
        self._status(f"Multiplos destinos: {rota.mais_de_um_destino}")
      except Exception as erro:
        logger.warning("Erro ao verificar destinos doc %s: %s", rota.numero_documento, erro)

    return rota

  def _processar_rota_individual(
    self,
    rota: DadosRota,
    destino: str,
    tipos_veiculo: list,
    vinculacao: VinculacaoService,
  ) -> None:
    self._status("VALIDANDO RESULTADOS...")

    for tipo_veiculo in tipos_veiculo:
      self._status(f"TIPO: {tipo_veiculo}")
      if self._validar_compatibilidade(rota, tipo_veiculo):
        vinculacao.tentar_vincular(rota, destino, tipo_veiculo)
        return

    vinculacao.registrar_incompativel(rota, destino, "Nao possui tipo veiculo")

  def _validar_compatibilidade(self, rota: DadosRota, tipo_veiculo: str) -> bool:
    if tipo_veiculo.lower() != rota.tipo_transporte.lower():
      return False

    # Se desligou verificação de valor no legado, liberava direto
    if not rota.valor_carga:
      return True

    try:
      valor_carga = float(rota.valor_carga.replace(".", ""))
    except ValueError:
      return True

    tipo_lower = rota.tipo_transporte.lower()
    if "carreta" in tipo_lower:
      ok = valor_carga <= self._parametros.limite_valor_carreta
      if not ok:
        self._status("Valor maior que o configurado (carreta)")
      return ok
    if "truck" in tipo_lower:
      ok = valor_carga <= self._parametros.limite_valor_truck
      if not ok:
        self._status("Valor maior que o configurado (truck)")
      return ok
    if "toco" in tipo_lower:
      return valor_carga <= self._parametros.limite_valor_toco

    return True

  def _status(self, mensagem: str) -> None:
    logger.info(mensagem)
    self._on_status(mensagem)
