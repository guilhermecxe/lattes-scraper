from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from shutil import which
import os
import time

from .expected_conditions import abreCV, tabs, modal

class LattesDriver(webdriver.Firefox):
    '''
    Responsável por operar o driver que realiza a busca por currículos.
    '''
    def __init__(self, configurations, teardown=True, headless=True):
        self.configurations = configurations
        self.teardown = teardown
        self.headless = headless

        options = Options()
        options.headless = self.headless

        service = Service(self.get_geckodriver_path())

        super().__init__(options=options, service=service)

        self.implicitly_wait(30)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def get_geckodriver_path(self):
        geckodriver_path = which('geckodriver')
        if not geckodriver_path:
            geckodriver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'geckodriver.exe')
        return geckodriver_path

    def search(self):
        s = Search(self, self.configurations)
        s.execute()

class Search:
    '''
    Responsável por coordenador a pesquisa. Isto inclui delegar a aplicação de filtros e preferências
    e obter os resultados da busca.
    '''
    def __init__(self, driver, configurations):
        self.driver = driver
        self.configurations = configurations

    def execute(self):
        filters = Filters(self.driver, self.configurations)
        preferences = Preferences(self.driver, self.configurations)
        results = Results(self.driver, self.configurations)

        self.get_search_page()
        filters.apply()
        preferences.apply()
        self.search()
        results.get_results()

        time.sleep(5)

    def get_search_page(self):
        self.driver.get('https://buscatextual.cnpq.br/buscatextual/busca.do')

    def search(self):
        self.driver.find_element(By.ID, 'botaoBuscaFiltros').click()

class Filters:
    '''
    Responsável por aplicar os filtros escolhidos pelo usuário.

    Filtros disponíveis:
        mode: "Nome" ou "Assunto"
        foreigners: True ou False
        productivity_scholarship: ["1A", "1B", "1C", "1D", "2"]
        professional_activity_areas: {"grande_area": ..., "area": ..., "subarea": ..., "especialidade": ...}
        professional_activity_uf: Todas, Acre, Alagoas, ..., Sergipe ou Tocantins
        text: <str>
    '''
    def __init__(self, driver, configurations):
        self.driver = driver
        self.configurations = configurations

    def apply(self):
        self.set_mode()
        self.set_foreigners()
        self.set_productivity_scholarship()
        self.set_professional_activity_areas()
        self.set_professional_activity_uf()
        self.set_text()

    def set_mode(self):
        if self.configurations.get('mode') == 'Assunto':
            self.driver.find_element(By.XPATH, "//input[@id = 'buscaAssunto']").click()

    def set_text(self):
        text = self.configurations.get('text')
        if text:
            text_input = self.driver.find_element(By.XPATH, "//input[@id = 'textoBusca']")
            text_input.send_keys(text)

    def set_foreigners(self):
        if not self.configurations.get('foreigners'):
            self.driver.find_element(By.ID, 'buscarEstrangeiros').click()

    def set_productivity_scholarship(self):
        self.driver.find_element(By.ID, 'filtro0').click()
        for scholarship in self.configurations.get('productivity_scholarship', []):
            self.driver.find_element(By.XPATH, f"//input[@id = 'checkbox{scholarship}']").click()
        self.driver.find_elements(By.ID, 'preencheCategoriaNivelBolsa')[0].click()

    def set_professional_activity_areas(self):
        grande_area = self.configurations.get('professional_activity_area', {}).get('grande_area')
        area = self.configurations.get('professional_activity_area', {}).get('area')
        subarea = self.configurations.get('professional_activity_area', {}).get('subarea')
        especialidade = self.configurations.get('professional_activity_area', {}).get('especialidade')

        if grande_area:
            self.driver.find_element(By.ID, 'filtro4').click()
            self.driver.find_element(By.XPATH, f"//option[text()='{grande_area}']").click()

            if area:
                self.driver.find_element(By.XPATH, f"//option[text()='{area}']").click()
                if subarea:
                    self.driver.find_element(By.XPATH, f"//option[text()='{subarea}']").click()
                    if especialidade:
                        self.driver.find_element(By.XPATH, f"//option[text()='{especialidade}']").click()

            self.driver.find_elements(By.ID, 'preencheCategoriaNivelBolsa')[4].click()

    def set_professional_activity_uf(self):
        professional_activity_uf = self.configurations.get('professional_activity_uf')
        if professional_activity_uf:
            self.driver.find_element(By.ID, 'filtro8').click()
            self.driver.find_elements(By.XPATH, f"//option[contains(text(), '{professional_activity_uf}')]")[-1].click()
            self.driver.find_elements(By.ID, 'preencheCategoriaNivelBolsa')[8].click()

class Preferences:
    '''
    Responsável por aplicar as preferências escolhidas pelo usuário.

    Preferências disponíveis:
        last_update: <int>
    '''
    def __init__(self, driver, configurations):
        self.driver = driver
        self.configurations = configurations

    def apply(self):
        self.driver.find_element(By.XPATH, "//a[text()=' Preferências ']").click()

        self.set_last_update()

    def set_last_update(self):
        last_update = self.configurations.get('last_update')
        if last_update:
            self.driver.find_element(By.ID, 'somenteAtualizados').clear()
            self.driver.find_element(By.ID, 'somenteAtualizados').send_keys(last_update)

class Results:
    """
    Responsável por acessar e salvar os currículos retornados na busca feita pela classe `Search`.
    """
    def __init__(self, driver, configurations):
        self.driver = driver
        self.configurations = configurations
        
        self.bd = TxtSaving(self.configurations.get('txt_saving', {}).get('folder'))

    def get_results(self):
        there_is_next_page = True
        current_page = 1
        while there_is_next_page:
            page_results = self.get_page_results()

            for result in page_results:
                id = self.get_result_id(result)
                if not self.bd.saved(id):
                    self.open_cv(result)
                    self.save_cv(id)
                    self.close_cv()
            there_is_next_page = self.next_page()
            if there_is_next_page:
                current_page = self.wait_load_next_page(previous_page=current_page)

    def get_result_id(self, result):
        href = result.find_element(By.TAG_NAME, 'a').get_attribute('href')
        return href.strip("javascript:abreDetalhe('").split("'")[0]

    def get_page_results(self):
        return self.driver.find_elements(By.XPATH, "//div[@class = 'resultado']/ol/li")

    def open_cv(self, result):
        WebDriverWait(self.driver, 10).until(modal(result))
        WebDriverWait(self.driver, 10).until(abreCV())
        WebDriverWait(self.driver, 50).until(tabs(more_than=1))
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.wait_load_cv()

    def save_cv(self, id):
        self.bd.save(id, self.driver.page_source)

    def close_cv(self):
        self.driver.close()
        WebDriverWait(self.driver, timeout=50).until(tabs(equals=1))
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.execute_script("""document.querySelector("a.bt-fechar").click()""")

    def wait_load_cv(self):
        try:
            self.driver.find_element(By.XPATH, "//div[@class='rodape-cv']")
        except NoSuchElementException:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.find_element(By.XPATH, "//div[@class='rodape-cv']")
    
    def next_page(self):
        try:
            next_page_button = self.driver.find_element(By.XPATH, "//font[@color='#ff0000']/parent::*/following-sibling::a")
            next_page_button.click()
            return True
        except NoSuchElementException:
            return False
    
    def wait_load_next_page(self, previous_page:int):
        for _ in range(3):
            try:
                current_page = int(self.driver.find_element(By.XPATH, "//font[@color='#ff0000']/parent::*").text)
            except NoSuchElementException:
                raise RuntimeError('Apesar do site indicar a existência de uma próxima página, ele não exibe os resultados desta.')
            
            if current_page == previous_page:
                time.sleep(self.configurations.get('sleep', 5))
            else:
                return current_page
        raise TimeoutError
    
class TxtSaving:
    def __init__(self, folder):
        self.folder = folder
        if self.folder:
            file_names = filter(lambda file_name: file_name.endswith('.txt'), os.listdir(folder))
            ids = map(lambda file_name: file_name.strip('.txt'), file_names)
            self.ids = list(ids)
        else:
            self.ids = []

    def saved(self, id):
        if id in self.ids:
            return True
        return False
    
    def save(self, id, soup):
        if self.folder:
            with open(os.path.join(self.folder, id + '.txt'), 'w', encoding='utf-8') as f:
                f.write(str(soup))