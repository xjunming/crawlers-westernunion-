#encoding: utf-8
import os
import csv
import time
import random
from datetime import date

from lxml import etree
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.common import exceptions

csv_headers = ['Time', 'Country', 'Limit', 'Receive_method', 'Pay_method1', 'Pay_method2', 'State', 'Exchange-Fee-Service_time']

# base_dir = os.path.join(os.getenv('SPIDER_LOGOUT_DIR'), 'westernunion')
base_dir = './'
if not os.path.exists(base_dir):
    os.makedirs(base_dir)
fw = open(os.path.join(base_dir, 'data.csv'), 'a', encoding='utf-8-sig', newline='')
writer = csv.DictWriter(fw, csv_headers)
if not os.path.getsize('data.csv'):
    writer.writeheader()
    fw.flush()

def get_etree(driver):
    return etree.HTML(driver.page_source)

def wait_loading(driver):
    WebDriverWait(driver, 60, .5).until_not(EC.visibility_of_element_located((By.ID, 'Oval')))

def choose_how_to_pay(driver, method1, data):
    data['Receive_method'] = method1
    pay_ele_id = ['fundsIn_CreditCard', 'fundsIn_DebitCard', 'fundsIn_ACH']
    pay_ele = ['Credit Card', 'Debit Card', 'Bank account']
    targetElem = driver.find_element_by_xpath('//label[@amplitude-id="radio-button-pay-online"]')
    driver.execute_script("arguments[0].focus();", targetElem)
    driver.find_element_by_xpath('//label[@amplitude-id="radio-button-pay-online"]').click()
    #How would you like to pay?  Online
    data['Pay_method1'] = 'Pay online'
    for i, ele_id in enumerate(pay_ele_id):
        time.sleep(random.uniform(1, 3))
        #Online分三种方式
        data['Pay_method2'] = pay_ele[i]
        time.sleep(random.uniform(1, 3))
        try:
            driver.find_element_by_id(ele_id).click()
        except exceptions.NoSuchElementException:
            pass
        else:
            time.sleep(random.uniform(1, 3))
            tree = get_etree(driver)
            result = tree.xpath('//section[@class="trxn-summary sum-wid-ff"]')[0].xpath('string(.)')
            data['Exchange-Fee-Service_time'] = result
            writer.writerow(data)
            fw.flush()

    time.sleep(random.uniform(1, 3))
    #How would you like to pay?  pay cash in-store
    data['Pay_method1'] = 'Pay cash in-store'
    data['Pay_method2'] = 'Pay cash in-store'
    data['State'] = 'New York'
    try:
        driver.find_element_by_id('radio-button-pay-instore').click()
    except Exception as e:
        print(e)
    else:
        time.sleep(random.uniform(1, 5))
        driver.find_element_by_id('button-continue-payin').click()
        time.sleep(random.uniform(1, 5))
        try:
            selector = Select(driver.find_element_by_xpath('//div[@class="wu-field select-wrapper"]/select'))
        except Exception as e:
            print(e)
            time.sleep(random.uniform(1, 5))
            # try:
            #     selector = Select(driver.find_element_by_xpath('//div[@class="wu-field select-wrapper"]/select'))
            # except:
            # time.sleep(random.uniform(1, 3))
            tree = get_etree(driver)
            result = tree.xpath('//section[@class="trxn-summary sum-wid-ff"]')[0].xpath('string(.)')
            data['Exchange-Fee-Service_time'] = result
            writer.writerow(data)
            fw.flush()
        else:
            time.sleep(random.uniform(1, 3))
            selector.select_by_visible_text('New York')
            wait_loading(driver)
            tree = get_etree(driver)
            result = tree.xpath('//section[@class="trxn-summary sum-wid-ff"]')[0].xpath('string(.)')
            data['Exchange-Fee-Service_time'] = result
            writer.writerow(data)
            fw.flush()


def get_detail(driver, tree, i, country):
    # i = 2
    # country = country_list[9]
    print('start ', country)
    data = {}
    data['Country'] = country
    i = i + 8
    driver.find_element_by_id('country').click()
    time.sleep(random.uniform(1, 2))
    # 点击对应的国家
    driver.find_element_by_xpath('//ul[@class="hy-drop dropdown-menu show-panel"]/li[{}]'.format(i)).click()
    # 等待loading界面
    wait_loading(driver)
    # driver.find_element_by_id('txtSendAmount').clear()
    time.sleep(random.uniform(1, 2))
    driver.find_element_by_id('txtSendAmount').click()
    time.sleep(random.uniform(0, 1))
    driver.execute_script('$("#txtSendAmount").val(100);')
    driver.execute_script('$("#txtSendAmount").blur();')
    # driver.find_element_by_id('txtSendAmount').send_keys(500)
    # time.sleep(.3)
    # driver.find_element_by_id('txtSendAmount').send_keys(0)
    # time.sleep(.1)
    # driver.find_element_by_id('txtSendAmount').send_keys(0)
    wait_loading(driver)
    crawl_date = str(date.today())
    data['Time'] = crawl_date
    if tree.xpath('//span[@class="animation-info"]/span/text()'):
        limit = tree.xpath('//span[@class="animation-info"]/span/text()')[0].strip()
        data['Limit'] = limit
    else:
        data['Limit'] = 'Send up to 19,000.00 USD'
    time.sleep(random.uniform(0, 2))
    # How does your receiver want the money? 选择 Cash pick up

    try:
        targetElem = driver.find_element_by_id('fundsOut_AG')
        driver.execute_script("arguments[0].focus();", targetElem)
        driver.find_element_by_id('fundsOut_AG').click()
        driver.execute_script('$("#txtSendAmount").val(100);')
        driver.execute_script('$("#txtSendAmount").blur();')
        wait_loading(driver)
    except exceptions.NoSuchElementException as e:
        print(e)
    else:
        choose_how_to_pay(driver, 'Cash pick up', data)

    time.sleep(random.uniform(1, 3))
    # How does your receiver want the money? 选择 Bank account
    try:
        driver.find_element_by_id('fundsOut_BA').click()
        wait_loading(driver)
    except exceptions.NoSuchElementException as e:
        print(e)
    else:
        choose_how_to_pay(driver, 'Bank account', data)
    time.sleep(random.uniform(1, 3))

def init_driver():
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    # opts.add_argument('headless')
    # opts.add_argument('no-sandbox')
    # opts.add_argument('disable-dev-shm-usage')
    driver = webdriver.Chrome(options=opts)
    # driver.get('https://www.westernunion.com/us/en/home.html')
    url = 'https://www.westernunion.com/us/en/web/send-money/start'
    driver.get(url)
    time.sleep(random.uniform(1, 3))
    try:
        driver.find_element_by_id('button-fraud-warning-accept').click()
    except Exception as e:
        print(e)
        pass
    wait_loading(driver)
    time.sleep(random.uniform(1, 3))
    # WebDriverWait(driver, 180, .5).until(EC.visibility_of_element_located((By.XPATH, '//input[@class="hy-country-input form-control error-behavior ng-pristine ng-valid ng-touched"]')))
    try:
        driver.find_element_by_id('country').click()
    except Exception as e:
        print(e)
        pass
        driver.find_element_by_xpath('//span[@class="typeahead-arrow"]').click()
    js = "var q=document.documentElement.scrollTop=100000"
    driver.execute_script(js)
    time.sleep(random.uniform(1, 3))
    tree = get_etree(driver)
    #读取国家列表
    country_list = tree.xpath('//ul[@class="hy-drop dropdown-menu show-panel"]/li/a/span/text() | //ul[@class="hy-drop dropdown-menu show-panel"]/li/a/span/strong/text()')
    print(country_list)
    return country_list, driver, tree

if __name__ == '__main__':
    start_id = 0   #如果出错了，从这里开始爬取。
    try_time = 0
    country_list, driver, tree = init_driver()
    country_list = ['Afghanistan', 'Afghanistan US Military Base', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antigua And Barbuda', 'Argentina', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Azores', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belgium US Military Base', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'British Virgin Islands', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Ceuta', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo-Brazzaville', 'Congo-Democratic Republic', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Cuba US Military Base', 'Curacao', 'Cyprus', 'Cyprus (Northern)', 'Czech Republic', 'Denmark', 'Djibouti', 'Djibouti US Military Base', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands (Malvinas)', 'Fiji', 'Finland', 'France', 'French Guiana', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Germany US Military Base', 'Ghana', 'Gibraltar', 'Greece', 'Greece US Military Base', 'Grenada', 'Guadeloupe', 'Guam', 'Guam US Military Base', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Honduras US Military Base', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iraq', 'Iraq US Military Base', 'Ireland', 'Israel', 'Italy', 'Italy US Military Base', 'Ivory Coast', 'Jamaica', 'Japan', 'Japan US Military Base', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Korea', 'Korea US Military Base', 'Kosovo', 'Kosovo US Military Base', 'Kuwait', 'Kuwait US Military Base', 'Kyrghyz Republic', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macau', 'Macedonia', 'Madagascar', 'Madeira', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Melilia', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'Netherlands US Military Base', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestinian Authority', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Portugal US Military Base', 'Puerto Rico', 'Qatar', 'Qatar US Military Base', 'Reunion Island', 'Romania', 'Russia', 'Rwanda', 'Saint Barthelemy', 'Saint Kitts And Nevis', 'Saint Lucia', 'Saint Vincent And The Grenadines', 'Samoa', 'Sao Tome And Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia (Somaliland)', 'South Africa', 'South Sudan', 'Spain', 'Spain US Military Base', 'Sri Lanka', 'St. Maarten', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkey US Military Base', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United Kingdom US Military Base', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Virgin Islands (US)', 'Yemen', 'Zambia', 'Zimbabwe']
    for i, country in enumerate(country_list):
        if i < start_id:
            continue
        while 1:
            try:
                get_detail(driver, tree, i, country)
                print('No.%s(%s) has download.' % (i, country))
                break
            except Exception as e:
                print(e)
                # print(try_time)
                try_time = try_time + 1
                if try_time == 2:
                    try_time = 0
                    print('can\'t request %s' % country)
                    break
                print('No.%s(%s) try again.' % (i, country))
                driver.close()
                driver.quit()
                time.sleep(random.uniform(5, 10))
                _, driver, tree = init_driver()



