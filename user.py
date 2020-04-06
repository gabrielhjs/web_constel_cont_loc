

class User(object):

    def __init__(self, login='', password='', token=''):
        self.login = login
        self.password = password
        self.token = token
        self.is_authenticated = False

    def authentidate(self):

        if self.login and self.password and self.token:
            self.is_authenticated = True

        else:
            self.is_authenticated = False

        return self.is_authenticated
