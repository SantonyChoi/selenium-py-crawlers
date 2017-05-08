#-*- coding: utf-8 -*-
import collections, logging, time, sys

from selenium import webdriver
from selenium.webdriver.support.ui import Select

logging.debug(str(unicode('한글 출력 확인', 'utf-8').encode('utf-8')))

kras_url = 'http://kras.seoul.go.kr/land_info/info/baseInfo/baseInfo.do'
InputValues = collections.namedtuple('InputValues', ['bonnum', 'bunum', 'sido', 'gu', 'dong'])



def read_input(file_d):
    logging.debug('read_input')
    RawInput = unicode(file_d.readline(), 'euc-kr').encode('utf-8').split('|')
    return InputValues(RawInput[8], RawInput[9], RawInput[4], RawInput[5], RawInput[6])



def search_target(driver, inputs):
    logging.debug('search_target')

    select_sido = Select(driver.find_element_by_id('sidonm'))
    select_sido.select_by_visible_text(inputs.sido)

    select_gu = Select(driver.find_element_by_xpath('//*[@id="sggnm"]'))
    select_gu.select_by_visible_text(inputs.gu)

    bonnum = driver.find_element_by_name('textfield')
    bonnum.clear()
    bonnum.send_keys(inputs.bonnum)

    bunum = driver.find_element_by_xpath('//*[@id="textfield2"]')
    bunum.clear()
    bunum.send_keys(inputs.bunum)

    time.sleep(0.1)

    select_dong = Select(driver.find_element_by_id('umdnm'))
    select_dong.select_by_visible_text(inputs.dong)

    search = driver.find_element_by_xpath('//*[@id="searching"]/a/img')
    result = search.click()


def save_result_basic(driver, output_basic_file, inputs):
    logging.debug('save_result_basic')

    # 시,구,동,본번,부번,지목,면적,개별공시지가,건물명칭,주용도,대지면적,연면적,건축물수,건축면적,건폐율,용적율,특이사항
    tabclick = driver.find_element_by_xpath('//*[@id="tab0301"]/li[1]/a')
    tabclick.click()

    result_string = inputs.sido + ',' + inputs.gu + ',' + inputs.dong + ',' + inputs.bonnum + ',' + inputs.bunum + ','

    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[1]/td[1]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[1]/td[2]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[1]/td[3]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[2]/td").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[3]/td").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[4]/td[1]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[4]/td[2]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[4]/td[2]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[5]/td[1]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[5]/td[2]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[5]/td[3]").text.encode('utf-8') + ','
    result_string += driver.find_element_by_xpath("//*[@id=\"baseInfo_print\"]/table[1]/tbody/tr[6]/td").text.encode('utf-8') + '\n'

    #print result_string
    output_basic_file.write(unicode(result_string, 'utf-8').encode('euc-kr'))


def save_result_advanced(driver, output_advanced_file, inputs):
    logging.debug('save_result_advanced')
    # 시,구,동,본번,부번,가격기준년도,토지소재지,지번,개별공시지가,기준일자,공시일자,가격기준년도,토지소재지, ...
    tabclick = driver.find_element_by_xpath('//*[@id="tab0301"]/li[5]/a')
    tabclick.click()

    table_element = driver.find_elements_by_xpath("//*[@id='landPrice_print']/table/tbody/tr")
    row_count = len(table_element)

    result_string = inputs.sido + ',' + inputs.gu + ',' + inputs.dong + ',' + inputs.bonnum + ',' + inputs.bunum + ','

    for row in range(1, row_count + 1):
        for col in range(1, 7):
            this_xpath = "//*[@id=\"landPrice_print\"]/table/tbody/tr[" + str(row) + "]/td[" + str(col) + "]"
            this_entry = driver.find_element_by_xpath(this_xpath).text.encode('utf-8').strip() + ','
            result_string += this_entry

    result_string += '\n'

    #print result_string
    output_advanced_file.write(unicode(result_string, 'utf-8').encode('euc-kr'))

def crawl(start, end):
    driver = webdriver.PhantomJS(executable_path='../../phantomjs')
    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    input_file = open('./input/input.txt', 'r')
    output_basic_file = open('./output_basic_'+str(start)+'_to_'+str(end)+'.txt', 'w')
    output_advanced_file = open('./output_advanced_'+str(start)+'_to_'+str(end)+'.txt', 'w')
    output_error_file = open('./output_error_'+str(start)+'_to_'+str(end)+'.txt', 'w')

    print 'start get'
    driver.get(kras_url)
    print 'finished get'

    for i in range(1, end + 1):
        try:
            print 'i: ' + str(i)
            inputs = read_input(input_file)
            if i < start:
                continue

            search_target(driver, inputs)
            save_result_basic(driver, output_basic_file, inputs)
            save_result_advanced(driver, output_advanced_file, inputs)

        except Exception,e:
            driver.save_screenshot('screenshot' + str(i) + '.png')
            output_error_file.write('failed: raw ' + str(i) + '\n')
            print 'see the screenshot'
            print driver.current_url
            print e
            print 'restart get'
            driver.get(kras_url)
            print 'finished get'


crawl(int(sys.argv[1]), int(sys.argv[2]))
