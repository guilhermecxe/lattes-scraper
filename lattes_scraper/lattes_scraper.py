from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from shutil import which
from tqdm import tqdm
import os
import time

from .expected_conditions import abreCV, tabs, modal
from .backup import Backup, save_backup, read_backup
from .utils import fill_list, hash

class LattesScraper(webdriver.Firefox):
    def __init__(self, teardown=True, headless=True, show_progress=False, backup_id=None, backup_name=None,
                 sleep=0):
        self.teardown = teardown
        self.show_progress = show_progress
        self.current_result = None
        self.previous_page_number = 0
        self.sleep = sleep
        self.backup = read_backup(backup_id) if backup_id else Backup({}, backup_name)
        self.progress_bar = None

        options = Options()
        service = Service(self.__get_geckodriver_path())
        options.headless = headless

        super().__init__(options=options, service=service)

        self.implicitly_wait(15)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def __get_geckodriver_path(self):
        geckodriver_path = which('geckodriver')
        if not geckodriver_path:
            geckodriver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'geckodriver.exe')
        return geckodriver_path
    
    def _set_progress_bar(self, total):
        if self.show_progress:
            self._progress_bar = tqdm(total=total)

    def _update_progress_bar(self, by=1):
        if self.show_progress:
            self._progress_bar.update(by)
            self._progress_bar.refresh()

    def __get_search_page(self):
        for i in range(3):
            try:
                self.get('https://buscatextual.cnpq.br/buscatextual/busca.do')
            except WebDriverException:
                if i == 2:
                    print('Error trying to access website. Check if it is working.')
                    raise
                time.sleep(5)

    def __click_search(self):
        self.find_element(By.ID, 'botaoBuscaFiltros').click()

    def __click_back_to_search(self):
        self.find_element(By.CSS_SELECTOR, "#tit2_simples .button").click()

    def multiple_searches(self, max_results=10, filters=[], preferences=[]):
        searches = max(len(filters), len(preferences))
        fill_list(filters, {}, searches)
        fill_list(preferences, {}, searches)

        self.__get_search_page()
        for i in range(searches):
            self.__apply_filters(filters[i])
            self.__apply_preferences(preferences[i])
            self.__click_search()
            self.__handle_get_results(max_results)
            self.__click_back_to_search()

    def search(self, max_results=10, filters={}, preferences={}):
        self.__get_search_page()
        self.__apply_filters(filters)
        self.__apply_preferences(preferences)
        self.__click_search()
        self.__handle_get_results(max_results)

    def __handle_get_results(self, max_results):
        try:
            self._get_search_results(max_results=max_results)
            return self.backup.item
        except:
            current_result_text = self.current_result.text.strip()
            if current_result_text == 'Stale file handle':
                print('Error. The plataform is not working well. Try again after some time.')
            else:
                print(f'An error occurred while getting the results. {len(self.backup.item)} results obtained.')
                print('Use .save_results method to save them.')
                if current_result_text:
                    print('Error while on result defined as:\n---')
                    print(current_result_text)
                    print('---')
            raise
        finally:
            if self.backup.id:
                id = save_backup(self.backup)
                print(f'A backup with id {id} was updated.')
            elif self.backup.item:
                id = save_backup(self.backup)
                print(f'A backup was created with id {id}.')

    def __wait_load_curriculum(self):
        try:
            self.find_element(By.XPATH, "//div[@class='rodape-cv']")
        except NoSuchElementException:
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.find_element(By.XPATH, "//div[@class='rodape-cv']")

    def _open_next_page(self):
        try:
            next_page_button = self.find_element(By.XPATH, "//font[@color='#ff0000']/parent::*/following-sibling::a")
            next_page_button.click()
            return True
        except NoSuchElementException:
            return False

    def _open_curriculum(self):
        WebDriverWait(self, 10).until(modal(self.current_result))
        WebDriverWait(self, 10).until(abreCV())
        WebDriverWait(self, 50).until(tabs(more_than=1))
        self.switch_to.window(self.window_handles[1])

        self.__wait_load_curriculum()

    def _wait_page_change(self, previous_page_number):
        for _ in range(3):
            current_page = self.find_element(By.XPATH, "//font[@color='#ff0000']/parent::*/following-sibling::a").text
            if current_page == 'próximo': # o próxima página, quando estamos na página 20, é nomeada "próximo"
                return previous_page_number + 1
            else:
                current_page_number = int(current_page)
                if current_page_number == previous_page_number:
                    time.sleep(self.sleep)
                else:
                    return current_page_number
        raise TimeoutError

    def _save_curriculum(self, curriculum_result_hash_code):
        self.backup.item[curriculum_result_hash_code] = self.page_source

    def _close_curriculum(self):
        self.close()
        WebDriverWait(self, timeout=50).until(tabs(equals=1))
        self.switch_to.window(self.window_handles[0])
        self.execute_script("""document.querySelector("a.bt-fechar").click()""")

    def _get_search_results(self, max_results=10):
        results_found = int(self.find_element(By.XPATH, "//div[@class='tit_form']/b").text)
        self._set_progress_bar(total=min(max_results, results_found))

        stored_results = lambda: len(self.backup.item)
        get_page_results = lambda: self.find_elements(By.XPATH, "//div[@class = 'resultado']/ol/li")

        there_is_next_page = True
        current_page_number = 0
        while there_is_next_page and stored_results() < max_results:
            missing_results = max_results - stored_results()
            page_results = get_page_results()
            results_to_get_on_page = min(len(page_results), missing_results)

            for i in range(results_to_get_on_page):
                self.current_result = page_results[i]
                result_text = self.current_result.text.strip()
                result_hash_code = hash(result_text)

                if not self.backup.item.get(result_hash_code):
                    self._open_curriculum()
                    self._save_curriculum(result_hash_code)
                    self._close_curriculum()
                    time.sleep(self.sleep)
                self._update_progress_bar(by=1)
                self.current_result = None
            
            there_is_next_page = self._open_next_page()
            if there_is_next_page:
                current_page_number = self._wait_page_change(previous_page_number=current_page_number)

    def __set_professional_activity_areas(self, grande_area, area=None, subarea=None, especialidade=None):
        self.find_element(By.ID, 'filtro4').click()
        for i in range(3):
            try:
                self.find_element(By.XPATH, f"//option[text()='{grande_area}']").click()
                if area: self.find_element(By.XPATH, f"//option[text()='{area}']").click()
                if subarea: self.find_element(By.XPATH, f"//option[text()='{subarea}']").click()
                if especialidade: self.find_element(By.XPATH, f"//option[text()='{especialidade}']").click()
                break
            except NoSuchElementException:
                time.sleep(2)
        self.find_elements(By.ID, 'preencheCategoriaNivelBolsa')[4].click()

    def save_results(self, folder_path, results=None):
        results = results if results else self.backup.item
        for k, v in results.items():
            with open(os.path.join(folder_path, f'{k}.html'), 'w', encoding='utf-8') as f:
                f.write(v)

    def __apply_preferences(self, preferences):
        last_update = preferences.get('last_update', 48)
        self.find_element(By.XPATH, "//a[text()=' Preferências ']").click()

        if last_update != 48:
            self.find_element(By.ID, 'somenteAtualizados').clear()
            self.find_element(By.ID, 'somenteAtualizados').send_keys(last_update)

    def __apply_filters(self, filters):
        areas = filters.get('areas')
        professional_activity_uf = filters.get('professional_activity_uf')
        text = filters.get('text')
        text_input = self.find_element(By.XPATH, "//input[@id = 'textoBusca']")

        if filters.get('mode') == 'Assunto':
            self.find_element(By.XPATH, "//input[@id = 'buscaAssunto']").click()
        if not filters.get('foreigner'):
            self.find_element(By.ID, 'buscarEstrangeiros').click()
        if areas:
            self.__set_professional_activity_areas(*areas)
        if professional_activity_uf:
            self.find_element(By.ID, 'filtro8').click()
            self.find_elements(By.XPATH, f"//option[contains(text(), '{professional_activity_uf}')]")[-1].click()
            self.find_elements(By.ID, 'preencheCategoriaNivelBolsa')[8].click()
        if text:
            text_input.send_keys(text)
