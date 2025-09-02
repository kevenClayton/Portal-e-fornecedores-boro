#!/usr/bin/env python3
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
