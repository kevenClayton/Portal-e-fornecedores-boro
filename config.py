global cliente
global fundo

# cliente = 'boro'
cliente = 'madeforte'
# cliente = 'rttransportes'
#
# fundo = '#011a41' #boro
fundo = '#2b6600' #madeforte
# fundo = '#fc9917' #rttransportes

conexoes = {
    'madeforte': {
        'host': 'mysql.madeforte.maranatatecnologia.com.br',
        'user': 'madeforte',
        'password': 'Secpol2',
        'database': 'madeforte',
    },
    'boro': {
        'host': 'mysql.boro.maranatatecnologia.com.br',
        'user': 'boro',
        'password': 'Secpol2',
        'database': 'boro',
    },
    'rttransportes': {
        'host': 'mysql.rttransportes.maranatatecnologia.com.br',
        'user': 'rttransportes',
        'password': 'Secpol2',
        'database': 'rttransportes',
    }
    # Adicione mais clientes conforme necessário
}