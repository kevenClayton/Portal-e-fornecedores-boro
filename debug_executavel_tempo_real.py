#!/usr/bin/env python3
"""
Debug em tempo real do executável - Identifica exatamente onde está falhando
"""

import os
import sys
import subprocess
import time
import traceback

def verificar_executavel():
    """Verifica se existe executável"""
    print("🔍 Verificando executável...")
    
    if not os.path.exists('dist/madeforte.exe'):
        print("❌ Executável não encontrado!")
        print("💡 Execute primeiro: python build_exe_ultra_conservador.py")
        return False
    
    tamanho = os.path.getsize('dist/madeforte.exe') / (1024*1024)
    print(f"✅ Executável encontrado: dist/madeforte.exe")
    print(f"📏 Tamanho: {tamanho:.2f} MB")
    return True

def debug_tempo_real():
    """Debug em tempo real do executável"""
    print("\n🚀 Debug em tempo real do executável...")
    
    try:
        # Teste 1: Execução com debug completo
        print("   Teste 1: Execução com debug completo...")
        
        comando_debug = [
            'dist/madeforte.exe',
            '--debug',
            '--verbose',
            '--log-level', 'DEBUG'
        ]
        
        print(f"   Comando: {' '.join(comando_debug)}")
        print("   ⚠️  Aguardando 20 segundos para debug completo...")
        
        processo = subprocess.Popen(
            comando_debug,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Aguardar 20 segundos para debug completo
        time.sleep(20)
        
        if processo.poll() is None:
            print("   ✅ Executável está rodando com debug")
            processo.terminate()
            time.sleep(2)
            if processo.poll() is None:
                processo.kill()
            return True
        else:
            stdout, stderr = processo.communicate()
            print(f"   ❌ Executável terminou com código: {processo.returncode}")
            
            if stdout:
                print(f"   STDOUT: {stdout[:1000]}...")
            if stderr:
                print(f"   STDERR: {stderr[:1000]}...")
            
            # Analisar código de erro
            if processo.returncode == -1073741819:
                print("   🚨 ERRO CRÍTICO: Access Violation (0xC0000005)")
                print("   💡 Este é um erro de nível do sistema, não do Python")
                print("   🔧 Possíveis causas:")
                print("      - DLLs faltando ou corrompidas")
                print("      - Conflitos de versão do Windows")
                print("      - Problemas com drivers de vídeo")
                print("      - Memória insuficiente ou corrompida")
            
            return False
        
    except Exception as e:
        print(f"   ❌ Erro ao testar executável: {e}")
        traceback.print_exc()
        return False

def criar_script_teste_minimo():
    """Cria script de teste mínimo para verificar funcionalidade básica"""
    print("\n📝 Criando script de teste mínimo...")
    
    script_teste = '''#!/usr/bin/env python3
"""
Script de teste mínimo - Verifica funcionalidade básica
"""

import sys
import os

def main():
    print("🚀 Script de teste mínimo iniciado!")
    print(f"Python: {sys.version}")
    print(f"Diretório: {os.getcwd()}")
    
    # Testar imports básicos
    try:
        import tkinter
        print("✅ tkinter importado com sucesso")
        
        # Testar criação de janela
        root = tkinter.Tk()
        root.title("Teste Mínimo - Sistema de Rotas")
        root.geometry("400x300")
        
        label = tkinter.Label(root, text="Teste Mínimo", font=("Arial", 16))
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    with open('teste_minimo.py', 'w', encoding='utf-8') as f:
        f.write(script_teste)
    
    print("✅ teste_minimo.py criado")

def main():
    """Função principal"""
    print("🔍 Debug em Tempo Real - Sistema de Rotas MadeForte")
    print("=" * 60)
    
    # Verificar executável
    if not verificar_executavel():
        return False
    
    # Debug em tempo real
    if not debug_tempo_real():
        print("\n❌ Debug em tempo real falhou!")
        print("🔧 O executável está falhando com erro crítico")
    
    # Criar script de teste mínimo
    criar_script_teste_minimo()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG EM TEMPO REAL CONCLUÍDO!")
    print("\n💡 Próximos passos:")
    print("   1. Teste o script mínimo: python teste_minimo.py")
    print("   2. Se funcionar, o problema está no executável")
    print("   3. Se não funcionar, o problema está no Python/tkinter")
    print("   4. Considere reinstalar o Python ou usar uma versão diferente")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Debug em tempo real falhou!")
            print("🔧 Verifique os erros acima")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        traceback.print_exc()
        sys.exit(1)
