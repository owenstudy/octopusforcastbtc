# Copyright (c) 2013 Alan McIntyre


class KeyData(object):
    def __init__(self, secret):
        self.secret = secret

class KeyHandler(object):
    def __init__(self, filename=None):
        """
        The given file is assumed to be a text file with two lines (key, secret).
        """

class KeyHandler(object):
    def __initX__(self, filename=None):
        """
        The given file is assumed to be a text file with two lines (key, secret).
        """
        self._keys = {}
        #bter key/secret
        key = '11433508-C612-43D4-BED2-DB28DDC7B883'
        secret = '82ecfee19c20b9603dca5b87ccf5cdecd0a282676bc399d7e7646026fc6a0ee2'
        self.addKey(key, secret)
    #ready to remove, since it may raise error
    def __init__(self, filename=None):
        """
        The given file is assumed to be a text file with two lines (key, secret).
        """
        self._keys = {}
        self.filename = filename
        if filename is not None:
            f = open(filename, "rt")
            while True:
                key = f.readline().strip()
                if not key:
                    break
                secret = f.readline().strip()
                self.addKey(key, secret)

    @property
    def keys(self):
        return list(self._keys.keys())

    def getKeys(self):
        return list(self._keys.keys())

    def save(self, filename):
        f = open(filename, "wt")
        for k, data in self._keys.items():
            f.write("%s\n%s\n" % (k, data.secret))

    def addKey(self, key, secret):
        self._keys[key] = KeyData(secret)

    def getSecret(self, key):
        data = self._keys.get(key)
        if data is None:
            raise Exception("Key not found: %r" % key)

        return data.secret
