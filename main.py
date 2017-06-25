#! /usr/bin/python3
import optparse
from netconnect import NetMiner
from dataanalysis import GetTargetContent, TextFormat
from datasave import DirectoryWork
from settings import TEST_PAGE_1, TEST_PAGE_2, TEST_PAGE_3, CONTENT_DIR, DATABASE

def circle(num_test):
    # Быстрый парсинг тестовых страниц или парсинг уникальной страницы
    if num_test == 1:
        target_url = TEST_PAGE_1
    elif num_test == 2:
        target_url = TEST_PAGE_2
    elif num_test == 3:
        target_url = TEST_PAGE_3
    else:
        target_url = num_test

    http_request = NetMiner(target_url)
    print('Содержимое страницы загружено.')
    site_content = GetTargetContent(http_request.get_content())
    raw_obj, img_url = site_content.get_text_raw()
    site_text = TextFormat(raw_obj)
    target_content_text, target_content_title = site_text.assembler()
    print('Выполенен разбор содержимого страницы.')
    obj_for_save = DirectoryWork(target_content_text, target_content_title, target_url, img_url)
    obj_for_save.save_data()
    print('Данные сохранены.')


if __name__ == '__main__':
    p = optparse.OptionParser()
    p.add_option('-t', '--test', action ='store', type ='int', dest ='test_page', help='Номер тестовой страницы (1-3).')
    p.add_option('-u', '--url', action='store', type='string', dest='url', help='URL разбираемой страницы.')
    p.add_option('-v', '--view', action='store_true', dest='view', help='Отобразить содержимое БД.')
    opt, args = p.parse_args()
    if opt.test_page:
        circle(opt.test_page)
    elif opt.url:
        circle(opt.url)
    elif opt.view:
        DirectoryWork.view_database()
    else:
        print("Oшибка ввода параметров запуска. Выполните программу с ключом -h")
