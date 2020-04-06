from constants import INIT_SPACE, SEPARADOR
from internal_functions import limpa_tela


def mensagem(mensagens=(), next_function=None):
    limpa_tela()
    print()

    for m in mensagens:

        if m['type'] == 0:
            tipo = 'Erro'

        elif m['type'] == 1:
            tipo = 'Aviso'

        elif m['type'] == 2:
            tipo = 'Sucesso'

        else:
            tipo = str(m['type'])

        print(INIT_SPACE + tipo + ': ' + m['texto'] + '!')

    print(SEPARADOR)

    if next_function is not None:

        return next_function()
