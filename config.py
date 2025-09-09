global cliente
global fundo

cliente = 'boro'
# cliente = 'jslogistica'
# cliente = 'madeforte'
# cliente = 'rttransportes'
#
# fundo = '#011a41' #jslogistica
fundo = '#011a41' #boro
# fundo = '#2b6600' #madeforte
# fundo = '#fc9917' #rttransportes

conexoes = {
    'madeforte': {
        'host': 'mysql.madeforte.maranatatecnologia.com.br',
        'user': 'madeforte',
        'password': 'Secpol2',
        'database': 'madeforte',
    },
    'boro': {
        'host': 'reservaai-data.cgns57eoufkz.us-east-1.rds.amazonaws.com',
        'user': 'robo',
        'password': 'D41D8CD98F00B204E9800998ECF8427E',
        'database': 'boro',
    },
    'rttransportes': {
        'host': 'mysql.rttransportes.maranatatecnologia.com.br',
        'user': 'rttransportes',
        'password': 'Secpol2',
        'database': 'rttransportes',
    },
    'jslogistica': {
        'host': 'reservaai.cgns57eoufkz.us-east-1.rds.amazonaws.com',
        'user': 'robo',
        'password': 'D41D8CD98F00B204E9800998ECF8427E',
        'database': 'jslogistica',
    }
    # Adicione mais clientes conforme necessário
}