

if __name__ == '__main__':
    from internal_functions import limpa_tela
    from user import User
    from controllers import controller_menu_inicial

    user = User()
    limpa_tela()

    controller_menu_inicial(user)
