import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd

# Chromeを起動する関数


def set_driver(driver_path, headless_flg):
    if "chrome" in driver_path:
          options = ChromeOptions()
    else:
      options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)

# main処理


def main():
    search_keyword = "高収入"
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

    # 検索窓を使わずに検索
    result_page = driver.find_elements_by_class_name("topSearch__wrapper")
    print('検索ボックスの数：', len(result_page))
    search_page_link = result_page[0].get_attribute("action")
    print('検索結果のURL：', search_page_link)
    kw = 'list/kw' + search_keyword
    result_page_link = search_page_link.replace('search/list', kw)
    print('キーワード検索結果のURL：', result_page_link)
    driver.get(result_page_link)

    # # 検索窓に入力
    # driver.find_element_by_class_name(
    #     "topSearch__text").send_keys(search_keyword)
    # # 検索ボタンクリック
    # driver.find_element_by_class_name("topSearch__button").click()

    # ページ終了まで繰り返し取得
    # 検索結果の一番上の会社名を取得
    name_list = driver.find_elements_by_class_name("cassetteRecruit__name")
    
    # 空のDataFrame作成
    df = pd.DataFrame()

    # 1ページ分繰り返し
    print(len(name_list))
    for name in name_list:
        print(name.text)
        # DataFrameに対して辞書形式でデータを追加する
        df = df.append(
            {"会社名": name.text, 
             "項目B": "",
             "項目C": ""}, 
            ignore_index=True)
        
        


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
