#!/usr/bin/env python3
"""
Debug detalhado do executável - Identifica problemas específicos
"""

import os
import sys
import subprocess
import time
import traceback

def verificar_arquivos_necessarios():
    """Verifica se todos os arquivos necessários existem"""
    print("🔍 Verificando arquivos necessários...")
    
    arquivos_necessarios = [
        'main.py',
        'config.py',
        'proxies.txt',
        'model/db.py',
        'fazendoLogin.py',
        'ListandoRotas2.py',
        'enviarEmail.py',
        'pegarValorObservacao.py',
        'validarLetraProduto.py',
        'icone.ico'
    ]
    
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"\n⚠️  Arquivos faltando: {', '.join(arquivos_faltando)}")
        return False
    
    return True

def testar_imports_python():
    """Testa se todos os imports funcionam no Python"""
    print("\n🔍 Testando imports Python...")
    
    imports_para_testar = [
        ('tkinter', 'tkinter'),
        ('PySimpleGUI', 'PySimpleGUI'),
        ('selenium', 'selenium'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('unidecode', 'unidecode'),
        ('bs4', 'beautifulsoup4'),
        ('requests', 'requests'),
        ('lxml', 'lxml'),
        ('webdriver_manager', 'webdriver_manager')
    ]
    
    imports_faltando = []
    
    for nome_import, nome_pacote in imports_para_testar:
        try:
            __import__(nome_import)
            print(f"✅ {nome_pacote}")
        except ImportError as e:
            print(f"❌ {nome_pacote} - {e}")
            imports_faltando.append(nome_pacote)
    
    if imports_faltando:
        print(f"\n⚠️  Imports faltando: {', '.join(imports_faltando)}")
        return False
    
    return True

def testar_main_python():
    """Testa se main.py executa no Python"""
    print("\n🔍 Testando execução do main.py no Python...")
    
    try:
        # Testar import do main
        print("   Testando import...")
        
        # Fazer backup do config.py original
        if os.path.exists('config.py'):
            with open('config.py', 'r', encoding='utf-8') as f:
                config_original = f.read()
        else:
            config_original = ""
        
        # Criar config temporário para teste
        config_teste = '''global cliente
global fundo

cliente = 'madeforte'
fundo = '#2b6600'

conexoes = {
    'madeforte': {
        'host': 'mysql.madeforte.maranatatecnologia.com.br',
        'user': 'madeforte',
        'password': 'Secpol2',
        'database': 'madeforte',
    }
}

# Dados de login para teste (mock)
dados = {
    'login': [('usuario_teste', 'senha_teste', 'https://teste.com')],
    'destinos': [],
    'motoristas': [],
    'motorista_destino': [],
    'motorista_origem': [],
    'origens': [],
    'parametros': [],
    'motoristas_tipo_veiculo': [],
    'motoristas_tipo_veiculo_carreta': [],
    'tipo_veiculo': [],
    'select_destinos_motoristas_ativos': []
}
'''
        
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_teste)
        
        print("   ✅ Config temporário criado")
        
        # Testar execução básica (sem GUI)
        print("   Testando execução básica...")
        
        # Executar com timeout
        processo = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar 10 segundos
        time.sleep(10)
        
        if processo.poll() is None:
            print("   ✅ main.py está executando (GUI deve estar aberta)")
            processo.terminate()
            time.sleep(2)
            if processo.poll() is None:
                processo.kill()
        else:
            stdout, stderr = processo.communicate()
            print(f"   ❌ main.py terminou com código: {processo.returncode}")
            if stderr:
                print(f"   STDERR: {stderr[:500]}...")
            return False
        
        # Restaurar config original
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_original)
        
        print("   ✅ Config original restaurado")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao testar main.py: {e}")
        traceback.print_exc()
        return False

def testar_executavel_detalhado():
    """Testa o executável com debug detalhado"""
    print("\n🔍 Testando executável com debug detalhado...")
    
    # Verificar se existe executável
    executaveis = []
    if os.path.exists('dist'):
        for arquivo in os.listdir('dist'):
            if arquivo.endswith('.exe'):
                executaveis.append(arquivo)
    
    if not executaveis:
        print("   ❌ Nenhum executável encontrado em dist/")
        print("   💡 Execute primeiro: python build_exe_tkinter.py")
        return False
    
    print(f"   📁 Executáveis encontrados: {', '.join(executaveis)}")
    
    # Testar primeiro executável
    exe_path = f"dist/{executaveis[0]}"
    print(f"   🧪 Testando: {exe_path}")
    
    try:
        # Teste 1: Execução com debug
        print("   Teste 1: Execução com debug...")
        
        comando_debug = [
            exe_path,
            '--debug',
            '--verbose'
        ]
        
        processo = subprocess.Popen(
            comando_debug,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("   Aguardando 15 segundos...")
        time.sleep(15)
        
        if processo.poll() is None:
            print("   ✅ Executável está rodando com debug")
            processo.terminate()
            time.sleep(2)
            if processo.poll() is None:
                processo.kill()
        else:
            stdout, stderr = processo.communicate()
            print(f"   ❌ Executável terminou com código: {processo.returncode}")
            if stdout:
                print(f"   STDOUT: {stdout[:500]}...")
            if stderr:
                print(f"   STDERR: {stderr[:500]}...")
        
        # Teste 2: Execução direta
        print("   Teste 2: Execução direta...")
        
        processo = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("   Aguardando 10 segundos...")
        time.sleep(10)
        
        if processo.poll() is None:
            print("   ✅ Executável está rodando")
            processo.terminate()
            time.sleep(2)
            if processo.poll() is None:
                processo.kill()
            return True
        else:
            stdout, stderr = processo.communicate()
            print(f"   ❌ Executável terminou com código: {processo.returncode}")
            if stdout:
                print(f"   STDOUT: {stdout[:500]}...")
            if stderr:
                print(f"   STDERR: {stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao testar executável: {e}")
        traceback.print_exc()
        return False

def criar_script_teste_simples():
    """Cria script de teste simples para verificar funcionalidade básica"""
    print("\n📝 Criando script de teste simples...")
    
    script_teste = '''#!/usr/bin/env python3
"""
Script de teste simples para verificar funcionalidade básica
"""

import sys
import os

def main():
    print("🚀 Script de teste simples iniciado!")
    print(f"Python: {sys.version}")
    print(f"Diretório: {os.getcwd()}")
    
    # Testar imports básicos
    try:
        import tkinter
        print("✅ tkinter importado com sucesso")
        
        # Testar criação de janela
        root = tkinter.Tk()
        root.title("Teste - Sistema de Rotas")
        root.geometry("400x300")
        
        label = tkinter.Label(root, text="Teste de Interface", font=("Arial", 16))
        label.pack(pady=50)
        
        button = tkinter.Button(root, text="Fechar", command=root.destroy)
        button.pack(pady=20)
        
        print("✅ Interface criada com sucesso")
        print("💡 Se você viu uma janela, o tkinter está funcionando!")
        
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Erro ao importar tkinter: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    with open('teste_simples.py', 'w', encoding='utf-8') as f:
        f.write(script_teste)
    
    print("✅ teste_simples.py criado")

def main():
    """Função principal"""
    print("🔍 Debug Detalhado do Executável - Sistema de Rotas")
    print("=" * 60)
    
    # Verificar arquivos
    if not verificar_arquivos_necessarios():
        print("\n❌ Arquivos necessários faltando!")
        return False
    
    # Testar imports
    if not testar_imports_python():
        print("\n❌ Imports Python falharam!")
        return False
    
    # Testar main.py
    if not testar_main_python():
        print("\n❌ main.py falhou no Python!")
        return False
    
    # Testar executável
    if not testar_executavel_detalhado():
        print("\n❌ Executável falhou!")
        return False
    
    # Criar script de teste
    criar_script_teste_simples()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG CONCLUÍDO!")
    print("\n💡 Próximos passos:")
    print("   1. Teste o script simples: python teste_simples.py")
    print("   2. Se funcionar, o problema está no PyInstaller")
    print("   3. Se não funcionar, o problema está no Python/tkinter")
    print("   4. Execute: python build_exe_tkinter.py para rebuild")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Debug falhou!")
            print("🔧 Verifique os erros acima")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        traceback.print_exc()
        sys.exit(1)
