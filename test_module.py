import unittest
import os
import pickle
from urllib import request
from netconnect import NetMiner
from datasave import DirectoryWork
from dataanalysis import GetTargetContent, TextFormat
from settings import CONTENT_DIR, DATABASE
from fixture import DUMMY, DUMMY_TEXT



class NetTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp_obj_good = NetMiner(target_url='https://yandex.ru/')

    def test_positive_content(self):
        ya_ru = self.tmp_obj_good.get_content().decode()
        current_ya_ru = request.urlopen('https://yandex.ru/').read().decode()
        self.assertTrue(('aria-label="Яндекс"' in ya_ru) & ('aria-label="Яндекс"' in current_ya_ru))


class DirectoryTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp_obj = DirectoryWork('Test is correct!', 'Title test', 'www.requestnews.ru')
        self.tmp_obj.save_data()

    def test_create_folder_positive(self):
        list_test_files = os.listdir('./'+CONTENT_DIR)
        self.assertTrue(self.tmp_obj.dir_for_media in list_test_files)

    def test_create_content_positive(self):
        with open("/".join(['.', CONTENT_DIR, self.tmp_obj.dir_for_media, 'content.txt']), 'r') as content_file:
            tmp_text = content_file.readline().strip('\n')
            self.assertEqual(tmp_text, 'Test is correct!')

    def test_pickle_positive(self):
        with open('/'.join(['.', CONTENT_DIR, DATABASE]), 'rb') as database:
            tmp_dict = pickle.load(database)
            self.assertTrue(self.tmp_obj.dir_for_media in tmp_dict['id_list'])

    def tearDown(self):
        os.remove("/".join(['.', CONTENT_DIR, self.tmp_obj.dir_for_media, 'content.txt']))
        os.removedirs("/".join(['.', CONTENT_DIR, self.tmp_obj.dir_for_media]))
        with open('/'.join(['.', CONTENT_DIR, DATABASE]), 'rb') as database:
            tmp_dict = pickle.load(database)
        with open('/'.join(['.', CONTENT_DIR, DATABASE]), 'wb') as database:
            tmp_dict['id_list'].remove(self.tmp_obj.dir_for_media)
            tmp_dict.pop(self.tmp_obj.dir_for_media)
            pickle.dump(tmp_dict, database)


class GetTargetContenTestCase(unittest.TestCase):
    def setUp(self):
        self.test_obj = GetTargetContent(DUMMY)

    def test_get_soup_obj(self):
        self.test_obj.get_soup_objects()
        self.assertEqual(self.test_obj.title, 'В Китае разработана технология получения бензина из углекислого газа')
        self.assertEqual(len(self.test_obj.soup_objects), 16)

    def test_get_target_obj(self):
        self.test_obj.get_soup_objects()
        self.test_obj.get_target_object()
        self.assertEqual(len(self.test_obj.target_object), 5)

    def test_compil_text(self):
        self.test_obj.get_soup_objects()
        self.test_obj.get_target_object()
        self.test_obj.clear_target_object()
        self.test_obj.compil_text()
        self.assertEqual(self.test_obj.text_for_save[1][0][:48], 'ШАНХАЙ, 13 июня. /Корр. ТАСС Иван Каргапольцев/')


class TextFormatTestCase(unittest.TestCase):
    def setUp(self):
        self.test_obj = TextFormat(DUMMY_TEXT)

    def test_assembler(self):
        target_text, target_title = self.test_obj.assembler()
        self.assertEqual(target_text[302: 316], 'Shanghai Daily')
        self.assertEqual(target_title, 'В Китае разработана технология получения бензина из углекислого газа')
