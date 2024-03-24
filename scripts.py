def scripts():
    cod = "var bg = document.getElementById('ctlLoadedControl_tbResultado');bg.style.backgroundColor = 'black';"

    return cod
def verificarCadaLinhaEClicarJavascript(driver):
    driver.execute_script(
        'var table = document.getElementById("ctlLoadedControl_dgRight")'
        'alert(table.rows)'

    )


