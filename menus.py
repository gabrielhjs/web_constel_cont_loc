from constants import INIT_SPACE, SEPARADOR
from messages import mensagem
from internal_functions import limpa_tela


def menu(user, context, controller, *args):
    assert context['opcoes'], 'Você deve fornecer opções para o menu'

    for i in range(len(context['opcoes'])):
        print(INIT_SPACE + '(' + str(i) + ') ' + context['opcoes'][i]['texto'])

    print()
    opcao_usuario = str(input(INIT_SPACE + 'Escolha uma das opções acima: '))

    if opcao_usuario.isdigit():
        opcao_usuario = int(opcao_usuario)

        if (opcao_usuario + 1) > len(context['opcoes']) or opcao_usuario < 0:
            mensagem(({'type': 0, 'texto': 'Digite uma opção válida'}, ))

            return controller(user, *args)

        limpa_tela()

        return context['opcoes'][opcao_usuario]['controller'](user, *args)

    else:
        mensagem((
            {'type': 0, 'texto': 'Digite apenas números'},
            {'type': 0, 'texto': 'Digite uma opção válida'},
        ))

        return controller(user, *args)


def menu_titulo(titulo):
    print()
    print(INIT_SPACE + titulo)
    print(SEPARADOR)
