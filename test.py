import PySimpleGUI as sg

layout = [[sg.Text("Olá mundo!")], [sg.Button("OK")]]
window = sg.Window("Janela de Teste", layout)
event, values = window.read()
window.close()
