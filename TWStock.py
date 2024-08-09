import requests
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class TWStock:
    @staticmethod
    def get_taiex_info():
        taiex_query_url = 'https://www.stockq.org/index/TWSE.php'
        response = requests.get(taiex_query_url, verify=False)
        if response.status_code != 200:
            print(f'Failed to get ETF info from www.stockq.org, status code: {response.status_code}')
            return None
        page = BeautifulSoup(response.text, 'html.parser')
        taiex_index_page_table = page.find('table', {'class': "indexpagetable"})
        taiex_index_table = taiex_index_page_table.find_all('tr')
        if len(taiex_index_table) != 2:
            print(f'Failed to get TAIEX info from {taiex_query_url}')
            return None
        taiex_index_title = [t.text for t in taiex_index_table[0].find_all('td')]
        taiex_index_value = [v.text for v in taiex_index_table[1].find_all('td')]

        return dict(zip(taiex_index_title, taiex_index_value))


class ETFCategory:
    def __init__(self):
        self.etf_query_url = 'https://www.stockq.org/etf'
        self.root_query_url = 'https://www.stockq.org'
        self.etf_category_url = self.cate_url()
        self.etf_category = self.etf_cate()

    def get_taiex_info(self):
        taiex_query_url = 'https://www.stockq.org/index/TWSE.php'
        response = requests.get(taiex_query_url, verify=False)
        if response.status_code != 200:
            print(f'Failed to get ETF info from www.stockq.org, status code: {response.status_code}')
            return None
        page = BeautifulSoup(response.text, 'html.parser')
        taiex_index_page_table = page.find('table', {'class': "indexpagetable"})
        taiex_index_table = taiex_index_page_table.find_all('tr')
        if len(taiex_index_table) != 2:
            print(f'Failed to get TAIEX info from {self.taiex_query_url}')
            return None
        taiex_index_title = [t.text for t in taiex_index_table[0].find_all('td')]
        taiex_index_value = [v.text for v in taiex_index_table[1].find_all('td')]

        return dict(zip(taiex_index_title, taiex_index_value))


    def cate_url(self):
        response = requests.get(self.etf_query_url, verify=False)
        if response.status_code != 200:
            print(f'Failed to get ETF info from www.stockq.org, status code: {response.status_code}')
            return None
        category_url = {'高股息ETF': [], '市值型/指數型ETF': [], '槓桿型ETF': [], '債券ETF': []}
        page = BeautifulSoup(response.text, 'html.parser')

        def get_href(search_title):
            nonlocal page
            return page.find('a', title=search_title)['href']

        category_url['高股息ETF'].append(self.root_query_url + get_href('高股息ETF'))
        category_url['槓桿型ETF'].append(self.root_query_url + get_href('正2反1 槓桿型ETF'))
        for t in ['台灣ETF']:
            category_url['市值型/指數型ETF'].append(self.root_query_url + get_href(t))

        # for t in ['AI相關ETF', '半導體ETF', '電動車產業ETF']:
        #     category_url['產業型ETF'].append(self.root_query_url + get_href(t))

        for t in ['美國政府長期公債ETF', '投資級公司債ETF', '非投資等級公司債ETF', '新興市場債ETF']:
            category_url['債券ETF'].append(self.root_query_url + get_href(t))

        return category_url

    def etf_cate(self):
        r = {'高股息ETF': set(), '市值型/指數型ETF': set(), '槓桿型ETF': set(), '債券ETF': set()}
        for cate, urls in self.etf_category_url.items():
            for u in urls:
                time.sleep(0.3)
                response = requests.get(u, verify=False)
                if response.status_code != 200:
                    print(f'Failed to get ETF info from {u}, status code: {response.status_code}')
                    return None
                page = BeautifulSoup(response.text, 'html.parser')
                tables_in_page = page.find_all('table', id='matrix')
                for t in tables_in_page:
                    products = t.find_all('tr')
                    for p in products:
                        etf_tag = p.find('td')
                        if etf_tag.find('font'):
                            continue
                        etf_num = etf_tag.contents[0]
                        # print(cate, etf_num)
                        r[cate].add(etf_num)

        else:
            r['市值型/指數型ETF'] = r['市值型/指數型ETF'] - r['高股息ETF'] - r['槓桿型ETF'] - r['債券ETF']
            return r

    def num_to_name(self, num: str):
        for cate, etfs in self.etf_category.items():
            if num in etfs:
                return cate
        return "個股"


if __name__ == '__main__':
    etf = ETFCategory()
    # print(etf.etf_category_url)
    # print(etf.etf_category)
    # print(etf.num_to_name('00919'))
    print(etf.get_taiex())