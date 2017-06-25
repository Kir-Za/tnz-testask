import unicodedata
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from settings import MIN_P_TAG, STR_LEN


class GetTargetContent():
    """
    Получение целевого контента из запроса
    """
    def __init__(self, binobj):
        """
        :param binobj: содержимое запроса по url сайта
        """
        self.raw = binobj
        self.soup_objects = None
        self.target_object = None
        self.text_for_save = []
        self.title = None
        self.image_list = None
        self.target_img = None

    def get_soup_objects(self):
        """
        Получить все теги р, отдельно сохрнать тег h1
        """
        soup = BeautifulSoup(self.raw, 'html.parser')
        self.title = soup.find('h1').getText()
        self.soup_objects = soup.findAll('p')
        self.image_list = [img for img in soup.findAll('img') if img.has_attr('itemprop')]

    def get_target_object(self):
        """
        Определеяем тег div, содержащий наибольшее колличество тегов р
        """
        for element in self.soup_objects:
            parent_obj = element.findParent()
            num_p_tag = len(parent_obj.findAll('p'))
            if num_p_tag > MIN_P_TAG:
                self.target_object = parent_obj.findAll('p')
                break
        if len(self.image_list) > 1:
            for element in self.image_list:
                if len(element.get('alt')):
                    self.target_img = element.get('src')
                    break
        else:
            try:
                self.target_img = self.image_list[0].get('src')
            except IndexError:
                print('Подходящих для загрузки изображений не обнаружено.')


    def clear_target_object(self):
        """
        В некоторых статьях, оформление ссылок идет не через тег <a> а через div с сылкой на внутренний ресурс.
        Удаляем эти div.
        Метод требует расширения в случае увеличения тестируемых url.
        """
        for text in self.target_object:
            try:
                dump = text.find('div')
                dump.extract()
            except Exception:
                pass

    def remove_tag(self, obj_soup, collector):
        """
        Удаляем теги, получая их содержимое
        :param obj_soup: разбираемый объект
        :param collector: временный список для сбора строки
        """
        for chunk_soup in obj_soup:
            if type(chunk_soup) is NavigableString:
                collector.append(unicodedata.normalize("NFKD", chunk_soup))
            elif type(chunk_soup) is Tag:
                if chunk_soup.has_attr('href'):
                    collector.append(
                        '[' +
                        chunk_soup.attrs['href'] +
                        '] ' +
                        unicodedata.normalize("NFKD", chunk_soup.getText())
                    )
                else:
                    self.remove_tag(chunk_soup, collector)
            else:
                print('Неопределенный элемент')

    def compil_text(self):
        """
        Собираем отдельные параграфы в единые списки.
        """
        for element in self.target_object:
            tmp = []
            self.remove_tag(element, tmp)
            self.text_for_save.append(tmp)
        self.text_for_save.insert(0, [self.title])
        for num_element, element in enumerate(self.text_for_save):
            if len(element) > 1:
                tmp = ''.join(element)
                self.text_for_save[num_element] = [tmp]

    def get_text_raw(self):
        """
        Получение списка, каждый элемент которого представляет собой отдельный абзац или заголовок
        """
        self.get_soup_objects()
        self.get_target_object()
        self.clear_target_object()
        self.compil_text()
        return self.text_for_save, self.target_img


class TextFormat():
    """
    Форматируем текст под условия в settings
    """
    def __init__(self, list_of_string):
        """
        :param list_of_string: список, содержащий список, каждый элемент кторого - абзац
        """
        self.raw_string_list = list_of_string
        self.correct_string_list = []

    def make_correct_len(self, string_work, position, space_pointer):
        """
        Проверяем длину строки, режем ее на куски, согласно STR_LEN
        :param string_work: исходная строка
        :param position: указатель на абзац
        :param space_pointer: последний пробел (режем по пробелам)

        >>> tmp1 = TextFormat(['*' * (STR_LEN - 2)])
        >>> tmp1.correct_string_list = [[]]
        >>> tmp1.make_correct_len('*' * (STR_LEN - 2), 0, 0)
        >>> len(tmp1.correct_string_list[0])
        1
        """
        tmp_string = string_work[space_pointer:(space_pointer + STR_LEN)]
        if len(tmp_string) < (STR_LEN - 1):  # 1 позиция на символ перевода строки
            tmp_string += '\n'
            self.correct_string_list[position].append(tmp_string)
        else:
            last_space = tmp_string.rfind(' ')
            tmp_string = tmp_string[:last_space]
            self.correct_string_list[position].append(tmp_string)
            space_pointer += (last_space + 1)  # затираем первый в строке пробел
            self.make_correct_len(string_work, position, space_pointer)

    def assembler(self):
        """
        Сборка текста в единую строку с форматированием через \n
        :return: целевой текст, заголовок для БД
        """
        for num_string, list_string_in_p in enumerate(self.raw_string_list):
            self.correct_string_list.append([])
            for string in list_string_in_p:
                self.make_correct_len(string, num_string, 0)
        fin_list = []
        for element in self.correct_string_list:
            for string_with_correct_len in element:
                fin_list.append(string_with_correct_len)
        fin_text = '\n'.join(fin_list)
        return fin_text, self.correct_string_list[0][0][:-1]

if __name__ == "__main__":
    import doctest
    doctest.testmod()