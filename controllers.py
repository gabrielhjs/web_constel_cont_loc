import requests
from requests.exceptions import ConnectionError
from tabulate import tabulate

from forms import form
from constants import CONSTEL_WEB_LOGIN_URL, INIT_SPACE, SEPARADOR
from messages import mensagem
from menus import menu, menu_titulo
from user import User
from chromedriver import DRIVER


def controller_menu_inicial(user, *args):
    menu_titulo("Menu inicial")

    if user.is_authenticated:
        return controller_menu_principal(user, *args)

    opcoes = (
        {'texto': 'Sair', 'controller': controller_sair, },
        {'texto': 'autenticar no sistema Constel.tk', 'controller': controller_login_web_constel, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_inicial, *args)


def controller_menu_principal(user, *args):
    menu_titulo("Menu Principal")

    if not user.is_authenticated:
        return controller_menu_inicial(user)

    opcoes = (
        {'texto': 'logout', 'controller': controller_logout, },
        {'texto': 'realizar baixa de ONT\'s', 'controller': controller_psw_login, },
        {'texto': 'Sair', 'controller': controller_sair, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_principal, *args)


def controller_menu_psw_contrato(user, *args):
    menu_titulo("Menu PSW")

    if not user.is_authenticated:
        return controller_menu_inicial(user)

    if not DRIVER.autenticado:
        return controller_psw_login(user)

    opcoes = (
        {'texto': 'Retornar ao menu principal', 'controller': controller_menu_principal, },
        {'texto': 'Buscar outro contrato', 'controller': controller_psw_busca_contrato, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_psw_contrato, *args)


def controller_menu_psw_contrato_sucesso(user, *args):
    menu_titulo("Menu PSW")

    if not user.is_authenticated:
        return controller_menu_inicial(user)

    if not DRIVER.autenticado:
        return controller_psw_login(user)

    opcoes = (
        {'texto': 'Retornar ao menu principal', 'controller': controller_menu_principal, },
        {'texto': 'Realizar baixa da ONT no sistema', 'controller': controller_ont_baixa, },
        {'texto': 'Buscar outro contrato', 'controller': controller_psw_busca_contrato, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_psw_contrato_sucesso, *args)


def controller_menu_psw_contrato_sem_dados(user, *args):
    menu_titulo("Menu PSW")

    if not user.is_authenticated:
        mensagem(({'type': 0, 'texto': 'Usuário não autenticado'}, ))
        return controller_menu_inicial(user)

    if not DRIVER.autenticado:
        mensagem(({'type': 0, 'texto': 'Usuário não autenticado no PSW'},))
        return controller_psw_login(user)

    opcoes = (
        {'texto': 'Retornar ao menu principal', 'controller': controller_menu_principal, },
        {
            'texto': 'Inserir contrato na lista de contratos pendentes de baixa',
            'controller': controller_ont_lista,
        },
        {'texto': 'Buscar outro contrato', 'controller': controller_psw_busca_contrato, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_psw_contrato_sem_dados, *args)


def controller_login_web_constel(user, *args):

    if user.is_authenticated:
        mensagem(({'type': 0, 'texto': 'Usuário logado'},))
        return controller_menu_principal(user, *args)

    fields = (
        {'id': 'username', 'name': 'login', },
        {'id': 'password', 'name': 'senha', },
    )
    response = form(user, fields)

    try:
        response_url = requests.post(CONSTEL_WEB_LOGIN_URL, json=response)

    except ConnectionError:
        mensagem(({'type': 0, 'texto': 'O sistema Constel.tk não está respondendo, contate o administrador'}, ))

        return controller_menu_inicial(user, *args)

    if response_url.status_code == 200:
        user.login = response['username']
        user.password = response['password']
        user.token = response_url.json()['token']
        user.authentidate()
        mensagem(({'type': 2, 'texto': 'Seja bem vindo(a)'}, ))

        return controller_menu_principal(user, *args)

    elif response_url.status_code == 400:
        mensagem(({'type': 0, 'texto': 'Usuário e/ou senha incorretos'}, ))

        return controller_menu_inicial(user, *args)

    else:
        mensagem(({'type': 0, 'texto': 'Falha na conexão com o sistema Constel.tk'}, ))

        return controller_menu_inicial(user, *args)


def controller_psw_login(user, *args):
    if not user.is_authenticated:
        mensagem(({'type': 0, 'texto': 'Usuário não autenticado'},))
        return controller_menu_inicial(user, *args)

    if DRIVER.autenticado:
        mensagem(({'type': 0, 'texto': 'Usuário não autenticado no PSW'},))
        return controller_psw_busca_contrato(user, *args)

    fields = (
        {'id': 'username', 'name': 'Chave da Copel', },
        {'id': 'password', 'name': 'Senha da Copel', },
    )
    response = form(user, fields)
    DRIVER.psw_login(response['username'], response['password'])

    return controller_psw_busca_contrato(user, *args)


def controller_psw_busca_contrato(user, *args):

    if not user.is_authenticated:
        mensagem(({'type': 0, 'texto': 'Usuário não autenticado'},))
        return controller_menu_inicial(user, *args)

    if not DRIVER.autenticado:
        mensagem(({'type': 0, 'texto': 'Usuário não autenticado no PSW'},))
        return controller_menu_principal(user, *args)

    fields = (
        {'id': 'contrato', 'name': 'Contrato', },
    )
    response = form(user, fields)
    dados = DRIVER.psw_contrato(response['contrato'])

    if len(dados) < 2:
        return controller_psw_busca_contrato(user, *args)

    print(INIT_SPACE + 'INFORMAÇÕES DO CONTRATO:')
    print(tabulate(dados['informacoes'], tablefmt="fancy_grid"))
    print()
    print(INIT_SPACE + 'DADOS DO CONTRATO:')
    print(tabulate(dados['dados'], tablefmt="fancy_grid"))

    dados['dados'].append({'id': 'contrato', 'nome': 'contrato', 'valor': response['contrato']})

    if len(dados['dados']) == 2:
        return controller_menu_psw_contrato_sem_dados(user, dados['dados'])

    else:
        return controller_menu_psw_contrato_sucesso(user, dados['dados'])


def controller_ont_baixa(user, *args):

    headers = {
        "Authorization": 'Token ' + user.token,
    }
    json = {}
    dados = args[0]

    for dado in dados:
        # print(dado)
        json[dado['id']] = dado['valor']

    json['token'] = user.token

    try:
        response_url = requests.post(
            'http://127.0.0.1:8000/almoxarifado/cont/api/ont/baixa/',
            json=json,
            headers=headers
        )

    except ConnectionError:
        mensagem(({'type': 0, 'texto': 'O sistema Constel.tk não está respondendo, contate o administrador'}, ))

        return controller_menu_principal(user, *args)

    print()
    print(SEPARADOR)

    if response_url.status_code == 201:
        user = response_url.json()['username']
        user_name = response_url.json()['first_name'] + " " + response_url.json()['last_name']

        print(INIT_SPACE + "Ont baixada de:")
        print(INIT_SPACE + "Matrícula: " + user)
        print(INIT_SPACE + "Nome: " + user_name)

    elif response_url.status_code == 400:
        errors = response_url.json()['non_field_errors']

        for error in errors:
            print(INIT_SPACE + "ERRO: " + error)

    else:
        print(INIT_SPACE + "Ocorreu um erro desconhecido, entre em contato com o administrador")
        print(response_url.json())

    print(SEPARADOR)

    return controller_menu_psw_contrato(user, *args)


def controller_ont_lista(user, *args):

    mensagem(({'type': 0, 'texto': 'Função indisponível no momento'},))

    return controller_menu_psw_contrato(user, *args)


def controller_sair(user, *args):

    del user
    del args

    return 0


def controller_logout(user, *args):

    del user
    user = User()

    return controller_menu_inicial(user, *args)
