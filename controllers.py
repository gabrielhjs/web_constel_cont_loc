import requests
from tabulate import tabulate

from forms import form
from constants import CONSTEL_WEB_LOGIN_URL, INIT_SPACE
from messages import mensagem
from menus import menu
from user import User
from chromedriver import DRIVER


def controller_menu_inicial(user):

    if user.is_authenticated:
        return None

    opcoes = (
        {'texto': 'Sair', 'controller': controller_sair, },
        {'texto': 'autenticar no sistema Constel.tk', 'controller': controller_login_web_constel, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_inicial)


def controller_menu_principal(user):

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

    return menu(user, context, controller_menu_principal)


def controller_menu_psw_contrato_sucesso(user, *args):

    if not user.is_authenticated:
        return controller_menu_inicial(user)

    if not DRIVER.autenticado:
        return controller_psw_login(user)

    opcoes = (
        {'texto': 'Realizar baixa da ONT no sistema', 'controller': controller_ont_baixa, },
        {'texto': 'Buscar outro contrato', 'controller': controller_psw_busca_contrato, },
        {'texto': 'Retornar ao menu principal', 'controller': controller_menu_principal, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_psw_contrato_sucesso, *args)


def controller_menu_psw_contrato_sem_dados(user, *args):
    if not user.is_authenticated:
        return controller_menu_inicial(user)

    if not DRIVER.autenticado:
        return controller_psw_login(user)

    opcoes = (
        {
            'texto': 'Inserir contrato na lista de contratos pendentes de baixa',
            'controller': controller_ont_lista,
        },
        {'texto': 'Buscar outro contrato', 'controller': controller_psw_busca_contrato, },
        {'texto': 'Retornar ao menu principal', 'controller': controller_menu_principal, },
    )

    context = {
        'opcoes': opcoes,
    }

    return menu(user, context, controller_menu_psw_contrato_sem_dados, *args)


def controller_login_web_constel(user):

    if user.is_authenticated:
        return None

    fields = (
        {'id': 'username', 'name': 'login', },
        {'id': 'password', 'name': 'senha', },
    )
    response = form(user, fields)
    response_url = requests.post(CONSTEL_WEB_LOGIN_URL, json=response)

    if response_url.status_code == 200:
        user.login = response['username']
        user.password = response['password']
        user.token = response_url.json()['token']
        user.authentidate()

        return controller_menu_principal(user)

    elif response_url.status_code == 400:
        mensagem(({'type': 0, 'texto': 'Usuário e/ou senha incorretos'}, ))

        return controller_menu_inicial(user)

    else:
        mensagem(({'type': 0, 'texto': 'Falha na conexão com o sistema Constel.tk'}, ))

        return controller_menu_inicial(user)


def controller_psw_login(user):
    if not user.is_authenticated:
        return controller_menu_inicial(user)

    if DRIVER.autenticado:
        return controller_psw_busca_contrato(user)

    fields = (
        {'id': 'username', 'name': 'Chave da Copel', },
        {'id': 'password', 'name': 'Senha da Copel', },
    )
    response = form(user, fields)
    DRIVER.psw_login(response['username'], response['password'])

    return controller_psw_busca_contrato(user)


def controller_psw_busca_contrato(user, *args):

    if not user.is_authenticated:
        return controller_menu_inicial(user)

    if not DRIVER.autenticado:
        return controller_menu_principal(user)

    fields = (
        {'id': 'contrato', 'name': 'Contrato', },
    )
    response = form(user, fields)
    dados = DRIVER.psw_contrato(response['contrato'])

    if not dados:
        return controller_psw_busca_contrato(user)

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

    print(json)

    response_url = requests.post('http://127.0.0.1:8000/almoxarifado/cont/api/ont/baixa/', json=json, headers=headers)
    print(response_url.json())


def controller_ont_lista(user, *args):
    pass


def controller_sair(user):

    return 0


def controller_logout(user):

    del user
    user = User()

    return controller_menu_inicial(user)
