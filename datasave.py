import os
import string
import random
import time
import pickle
import urllib
from settings import CONTENT_DIR, DATABASE


class DirectoryWork():
    """
    Проверка прав, создание директорий для хранения контента сайта, создание файла для сбора информации по запросам.
    """
    def __init__(self, text, title, url, img=None):
        """
        :param text: текстовя мегастрока
        :param title: заголовок для БД
        :param url: адр. запроса
        :param img: заглушка под картинку
        """
        self.current_dir = None
        self.dir_for_media = None
        self.dict_db = None
        self.url_request = url
        self.title = title
        self.text_for_save = text
        self.img_for_save = img

    def update_status(self):
        """
        Получение текущей директории, проверка прав на запись в ней, проеврка наличия папки media.
        Если требуемая пака отсутствует - создаем.
        """
        self.current_dir = os.getcwd()
        if self.check_rules():
            self.check_folder()
            self.check_pickle()

    @staticmethod
    def check_rules():
        if os.access(os.getcwd(), os.W_OK):
            return True
        else:
            print("Нет прав достпупа на запись в текущий файл")
            return False

    def check_folder(self):
        try:
            os.mkdir('/'.join([self.current_dir, CONTENT_DIR]))
        except OSError:
            pass
        except Exception as err:
            print(err)

    @staticmethod
    def check_pickle():
        try:
            list_files = os.listdir('./'+CONTENT_DIR)
            if DATABASE not in list_files:
                with open('/'.join([CONTENT_DIR, DATABASE]), 'wb') as db_file:
                    pickle.dump({'id_list': [], }, db_file)
                    print("Создали файл для хранения информации по запросам")
        except Exception:
            pass

    def create_dirs(self):
        """
        Создание уникальной директории для записи контента разбираемого сайта
        """
        self.update_status()
        while True:
            try:
                random_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)])
                os.mkdir('/'.join([self.current_dir, CONTENT_DIR, random_name]))
                self.dir_for_media = random_name
                break
            except Exception as err:
                pass

    def insert_img_src(self):
        """
        Так как униакльное имя директории получаем только на стадии записи, добавляем ссылку на изображение
        непосредственно перед записью на диск.
        """
        tmp_str = '/'.join([self.current_dir, CONTENT_DIR, self.dir_for_media, 'main_img.jpg'])
        tmp_str = '\nИзображение: [' + tmp_str + ']'
        self.text_for_save = '\n'.join([self.text_for_save, tmp_str])

    def write_data(self):
        """
        Запись текста в документ content.txt ранее созданной уникальной папки.
        """
        self.create_dirs()
        self.insert_img_src()
        with open('/'.join([self.current_dir, CONTENT_DIR, self.dir_for_media, 'content.txt']), 'w') as text_file:
            text_file.write(self.text_for_save)
        if self.img_for_save:
            try:
                urllib.request.urlretrieve(self.img_for_save,
                                           '/'.join([self.current_dir, CONTENT_DIR, self.dir_for_media,'main_img.jpg']))
            except Exception as err:
                print(err)

    def get_current_dict(self):
        """
        Получаем историю запросов из pickle файлв
        """
        with open('/'.join(['.', CONTENT_DIR, DATABASE]), 'rb') as database:
            self.dict_db = pickle.load(database)

    def update_dict(self):
        """
        Обновляем словарь из базы данных согласно новым записям на диске
        """
        if self.dir_for_media in self.dict_db['id_list']:
            print("Нарушение синхронизации, запись на диске не совпадает с данными в базе.")
        else:
            self.dict_db['id_list'].append(self.dir_for_media)
            if self.img_for_save:
                img_path = '/'.join([CONTENT_DIR, self.dir_for_media, 'main_img.jpg'])
            else:
                img_path = "нет"
            self.dict_db.update({
                self.dir_for_media: {
                    'time': time.time(),
                    'title': self.title,
                    'url': self.url_request,
                    'text_file': '/'.join([CONTENT_DIR, self.dir_for_media, 'content.txt']),
                    'img_file': img_path,
                }
            })

    def update_database(self):
        """
        Закидываем  обновленный словарь базу
        """
        self.get_current_dict()
        self.update_dict()
        with open('/'.join(['.', CONTENT_DIR, DATABASE]), 'wb') as database:
            pickle.dump(self.dict_db, database)

    @classmethod
    def view_database(cls):
        """
        Просмотр содержимого базы данных
        """
        cls.check_rules()
        cls.check_pickle()
        with open('/'.join([CONTENT_DIR, DATABASE]), 'rb') as db_file:
            tmp = pickle.load(db_file)
            db_len = len(tmp.pop('id_list'))
            if not db_len:
                print('База данных пуста.')
            else:
                for file in tmp:
                    print('Запись {0}:\n\t'
                          'URL статьи: {1};\n\t'
                          'Заголовок: {2};\n\t'
                          'Путь к текстовому файлу: {3}\n\t'
                          'Изображение: {4}\n\t'
                          'Дата выполнения запроса: {5}.\n'.format(
                        file,
                        tmp[file]['url'],
                        tmp[file]['title'],
                        tmp[file]['text_file'],
                        tmp[file]['img_file'],
                        time.ctime(tmp[file]['time']),
                    )
                    )

    def save_data(self):
        """
        Созраняем результаты прасинга в директории + "вело" БД
        """
        self.write_data()
        self.update_database()
