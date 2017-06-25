import validators
from urllib import request, error
from settings import PING_PAGE, TEST_PAGE_1


class NetMiner():
    """
    Полученеи информации из сети
    """
    def __init__(self, target_url=TEST_PAGE_1, ping_ulr=PING_PAGE):
        """
        :param target_url: откуда получили
        :param ping_ulr: проверка соединения с сетью
        """
        self.html_request = None
        self.ping = ping_ulr
        self.url_page = target_url

    def ping_net(self):
        """
        Проверка соединения
        
        >>> tmp_obj = NetMiner()
        >>> tmp_obj.ping_net()
        Доступ к сети есть.
        """
        try:
            request.urlopen(PING_PAGE).read()
        except Exception as err:
            print(err)
        else:
            print('Доступ к сети есть.')

    def check_url(self):
        """
        Проверка введенного пользовательского url
        
        >>> tmp_obj = NetMiner(target_url='bad url')
        >>> tmp_obj.check_url()
        Ошибка в url: bad url
        False

        """
        if not validators.url(self.url_page):
            print('Ошибка в url: ' + self.url_page)
            return False
        return True

    def get_content(self):
        """
        Получение данных с целевой страницы
        """
        try:
            if self.check_url():
                html = request.urlopen(self.url_page).read()
                return html
        except error.HTTPError as err:
            print(err)
            return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
