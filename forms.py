from constants import INIT_SPACE, SEPARADOR
from internal_functions import limpa_tela


def form(user, fields=()):
    limpa_tela()
    print()
    print(SEPARADOR)
    print()

    response = {}

    for field in fields:
        response[field['id']] = str(input(INIT_SPACE + field['name'] + ': '))

    assert response, "Você deve fornecer ao menos um campo para o formulário!"

    return response
