from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup as Bs
import lxml  # É importante para a biblioteca do BeautifulSoap
import re
import os

from messages import mensagem

PSW_URL_LOGIN = 'https://www.copel.com/pswweb/paginas/inicio.jsf'
PSW_URL = 'https://www.copel.com/pswweb/paginas/campoatendimentoativacao.jsf'


class ChromeDriver(object):
    """
        Este obejeto é responsável por iniciar um browser virtual e accessar o site do PSW da Copel para realizar a
    checagem da ativação do cliente, bem como a ONT em utilização em tempo real. Isso é feito utilizando-se o webdriver
    da biblioteca Selenium, juntamente com um binário do Google Chrome.
    """

    def __init__(self):
        """
            Aqui são feitas as configurações iniciais para a inicialização do webdriver bem como a inicialização do
        mesmo. Nestas configurações o navegador é aberto de forma invisível no servidor.
            - Deverão ser realizados testes futuros para verificar capacidade de o servidor executar vários navegadores
            de forma simultânea, que é o que ocorrerá na prática.
        """
        _chrome_options = webdriver.ChromeOptions()
        # _chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        # _chrome_options.binary_location = "/bin/chromium"
        _chrome_options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        _chrome_options.add_argument("--headless")
        _chrome_options.add_argument("--disable-dev-shm-usage")
        _chrome_options.add_argument("--no-sandbox")
        _chrome_options.add_argument("--silent-launch")
        _chrome_options.add_argument("--log-level=3")
        # self._driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=_chrome_options)
        self._driver = webdriver.Chrome(executable_path="chromedriver/chromedriver", options=_chrome_options)
        self.autenticado = False

    def psw_login(self, username, password):
        """
            Aqui o webdriver já iniciado acessa a URL do site do PSW e envia as informações de login e senha do usuário
        para então realizar a autenticação no sistema.
        :param username: string com o nome de usuário que é fornecido pelo usuário no formuário de login do PSW
        :param password: string com o nome de usuário que é fornecido pelo usuário no formuário de login do PSW
        :return: True para usuário autenticado com sucesso, e False para falha na autenticação
        """
        self._driver.get(PSW_URL)
        self._driver.implicitly_wait(1)

        try:
            usuario = self._driver.find_element_by_name('j_username')
            usuario.send_keys(username)
            senha = self._driver.find_element_by_name('j_password')
            senha.send_keys(password)
            senha.submit()

        except NoSuchElementException:
            try:
                self._driver.find_element_by_name('form:contrato')

            except NoSuchElementException:
                self.autenticado = False
                mensagem(({'type': 0, 'texto': 'Falha ao conectar-se com o PSW'},))

            else:
                self.autenticado = True

                return self.autenticado

        else:
            self._driver.implicitly_wait(1)

            if self._driver.current_url == 'https://www.copel.com/pswweb/paginas/j_security_check':
                self.autenticado = False
                mensagem(({'type': 0, 'texto': 'Chave Copel e/ou senha incorretos'}, ))

                return self.autenticado

            elif self._driver.current_url == PSW_URL:
                self.autenticado = True

                return self.autenticado

            else:

                return False

    def psw_contrato(self, contrato):
        """
            Aqui o webdriver que já deve estar com o usuário autenticado, realiza a busca do contrato informado pelo
            usuário no sistema da Copel; E obtem de volta as informações pertinentes, são elas:
            - Nome do cliente;
            - Status do contrato;
            - Porta;
            - Estado do Link;
            - Nível ONT [dB];
            - Nível OLT [dB];
            - Nível OLT TX:;
            - Número Serial;
            - Modelo ONT; dentre outras.
            A principal informação requisitada é o núemro de serial e o modelo da ONT, pois com esses é realizada a
        a baixa do equipamento da carga do técnico que realizou a instalação, no sistema principal (Constel.tk).
        Porém todas as informações são enviadas para o sistema principal e armazenadas no banco de dados.
        :param contrato: string contendo o contrato informado pelo usuário no formulário de busca de contrato
        :return: returna um dicionário com as informações pertinentes ao contrato informado
        """

        if not self.autenticado:
            return False

        self._driver.get(PSW_URL)
        self._driver.implicitly_wait(2)

        try:
            self._driver.find_element_by_name('form:contrato').send_keys(contrato)
            self._driver.find_element_by_name('form:j_idt115').click()

        except NoSuchElementException:

            try:
                self._driver.find_element_by_name('j_username')
                self.autenticado = False
                mensagem(({'type': 0, 'texto': 'Seção expirada, faça login novamente'},))

            except NoSuchElementException:
                self.autenticado = False
                mensagem(({'type': 0, 'texto': 'Falha ao conectar-se com o PSW'},))

            return False

        self._driver.implicitly_wait(2)

        tempo_maximo = 20
        tempo = 0
        carregado = None
        informacoes = []
        dados = []

        while tempo <= tempo_maximo and carregado is None:
            response_info = Bs(self._driver.page_source, 'lxml')
            informacoes = response_info.find('div', {"id": 'form:painel_content'})
            carregado = informacoes.find_next('span', string='Estado técnico: ')
            informacoes = informacoes.findAllNext('span', {'style': re.compile('.*font-weight:bold.*')})
            sleep(0.2)
            tempo += 0.2

        info_cliente = []

        for i in informacoes:
            info_cliente.append([i.text, ])

        tempo = 0
        tempo_maximo = 30

        while tempo <= tempo_maximo and dados == []:
            response = self._driver.page_source
            self._driver.implicitly_wait(1)
            response_info = Bs(response, 'lxml')
            dados = response_info.find('tbody', {'id': 'form:cli_data'})
            sleep(0.2)
            tempo += 0.2

        dados_cliente = []

        if dados:
            celulas = dados.findAllNext('td')
            rotulos = [
                ['porta', 'Porta:', ],
                ['estado_link', 'Estado do Link', ],
                ['nivel_ont', 'Nível ONT [dB]', ],
                ['nivel_olt', 'Nível OLT [dB]', ],
                ['nivel_olt_tx', 'Nível OLT TX', ],
                ['serial', 'Número Serial', ],
                ['modelo', 'Modelo ONT', ],
            ]

            for i in range(7):
                dados_cliente.append({'id': rotulos[i][0], 'nome': rotulos[i][1], 'valor': celulas[i].text})

        if not len(info_cliente):
            info_cliente = [['Não foi possível carregar informações', ], ]

        if not len(dados_cliente):
            dados_cliente = [{'nome': 'Não foi possível carregar dados'}]

        context = {
            'informacoes': info_cliente,
            'dados': dados_cliente,
        }

        return context


DRIVER = ChromeDriver()
