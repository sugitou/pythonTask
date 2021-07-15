from logging import debug, error, log
import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import datetime
import pandas as pd
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager


# 現在時刻取得
now = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
log_path = f'log/log_{now}.log'
csv_path = f'csv/output_{now}.csv'

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
        # return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
        return Chrome(ChromeDriverManager().install(),options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)


def find_table_target_word(th_elms, td_elms, target:str):
    # tableのthからtargetの文字列を探し一致する行のtdを返す
    for th_elm,td_elm in zip(th_elms,td_elms):
        if th_elm.text == target:
            return td_elm.text


def logfile(log_text):
    with open(log_path, 'a', encoding='utf-8') as f:
        # 件数ごとに出力時間を記載する
        log_now = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        log = f'[{log_now}] {log_text}'
        f.write(log + '\n')


# main処理
def main():
    search_keyword = input("検索ワードを入力してください。 >>> ")
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
        # Chromeドライバーがバージョンアップの際に自動で更新される
        # driver = webdriver.Chrome(ChromeDriverManager().install())
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass


    # 検索窓を使わずに検索
    result_page = driver.find_elements_by_class_name("topSearch__wrapper")
    search_page_link = result_page[0].get_attribute("action")
    kw = 'list/kw' + search_keyword
    result_page_link = search_page_link.replace('search/list', kw)
    driver.get(result_page_link)

    # 空のDataFrame作成
    df = pd.DataFrame()

    # 件数カウンター作成
    job_num = 0
    
    while True:
        try:  
            # ページ終了まで繰り返し取得
            # 検索結果の会社名,求人タイトル,初年度年収,掲載終了日を取得
            name_list = driver.find_elements_by_class_name("cassetteRecruit__name")
            copy_list = driver.find_elements_by_class_name("cassetteRecruit__copy")
            table_list = driver.find_elements_by_css_selector(".cassetteRecruit .tableCondition") # 初年度年収
            end_date_list = driver.find_elements_by_class_name("cassetteRecruit__endDate")

            # 1ページ分繰り返し
            for name, copy, table, end in zip(name_list, copy_list, table_list, end_date_list):
                first_year_fee = find_table_target_word(table.find_elements_by_tag_name("th"),
                                                        table.find_elements_by_tag_name("td"),
                                                        "初年度年収")
                # 件数をカウント
                job_num += 1
                out_num = f'{job_num}件目'
                logfile(out_num)

                # DataFrameに対して辞書形式でデータを追加する
                df = df.append(
                    {"会社名": name.text, 
                    "タイトル": copy.text,
                    "初年度年収": first_year_fee,
                    "掲載終了予定日": end.text}, 
                    ignore_index=True)
                    
            # 次のページ情報を取得
            next_page = driver.find_elements_by_class_name("iconFont--arrowLeft")
            if len(next_page) > 0:
                page_link = next_page[0].get_attribute("href")
                driver.get(page_link)
            else:
                print('これ以上ページがありません。')
                print('スクレイピングを終了します。')
                break
        except Exception as e:
            er = f'{job_num}件目でエラーが発生しました。'
            logfile(er)
            print(e)
            continue
        
    # csvファイルに取得データを出力
    df.to_csv(csv_path)


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()