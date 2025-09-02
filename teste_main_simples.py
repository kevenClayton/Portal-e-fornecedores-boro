#!/usr/bin/env python3
"""
Teste simples da interface PySimpleGUI - Sem dependências de banco
"""

import sys
import os

def main():
    print("🚀 Teste da Interface PySimpleGUI")
    print("=" * 40)
    
    try:
        # Testar imports básicos
        import PySimpleGUI as sg
        print("✅ PySimpleGUI importado com sucesso")
        
        import tkinter
        print("✅ tkinter importado com sucesso")
        
        # Criar interface simples similar ao main.py
        layout = [
            [sg.Text("Teste - Sistema de Rotas", font=("Arial", 16))],
            [sg.Text("Buscar e aceitar rotas no e-Fornecedor")],
            [sg.Text(size=(40,2), key='-OUTPUT-')],
            [sg.Button('Teste - Buscar rotas'), sg.Button('Fechar')]
        ]
        
        # Criar janela
        window = sg.Window(
            'Teste - Sistema de Rotas', 
            layout, 
            background_color='#2b6600',
            size=(500, 300)
        )
        
        print("✅ Interface criada com sucesso")
        print("💡 Se você viu uma janela verde, o PySimpleGUI está funcionando!")
        
        # Loop de eventos
        while True:
            event, values = window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'Fechar':
                break
            elif event == 'Teste - Buscar rotas':
                window['-OUTPUT-'].update("✅ Teste funcionando! Interface OK!")
                print("✅ Botão clicado com sucesso!")
        
        window.close()
        print("✅ Interface fechada com sucesso")
        
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎯 TESTE CONCLUÍDO!")
    print("💡 Se tudo funcionou, o problema está no PyInstaller")
    print("💡 Se falhou, o problema está no Python/PySimpleGUI")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Teste falhou!")
        sys.exit(1)
    else:
        print("\n✅ Teste passou com sucesso!")
