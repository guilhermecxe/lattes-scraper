from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from shutil import which
import os
import time

from .expected_conditions import abreCV, tabs

class LattesScraper(webdriver.Firefox):
    def __init__(self, teardown=True, headless=True):
        # Se o navegador deve ser fechado após a execução
        self.teardown = teardown

        # Se o navegador deve ser exibido
        options = Options()
        options.headless = headless

        # Obtendo a localização do geckodriver pelo PATH
        geckodriver_path = which('geckodriver')
        if not geckodriver_path:
            geckodriver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'geckodriver.exe')
        service = Service(geckodriver_path)

        # Iniciando o driver
        super().__init__(options=options, service=service)

        # Setando 10 segundos de espera padrão
        self.implicitly_wait(10)

        self.results_pages_source = {}

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def search(self, mode, text, areas=None, foreigner=False, professional_activity_uf=None, max_results=10):
        # Obtendo a página
        self.get('https://buscatextual.cnpq.br/buscatextual/busca.do')

        # Aplicando os filtros
        text_input = self.find_element(By.XPATH, "//input[@id = 'textoBusca']")
        if mode == 'Assunto':
            self.find_element(By.XPATH, "//input[@id = 'buscaAssunto']").click()
        if not foreigner:
            self.find_element(By.ID, 'buscarEstrangeiros').click()
        if areas:
            self._set_atuacao_profissional(*areas)
        if professional_activity_uf:
            self.find_element(By.ID, 'filtro8').click()
            self.find_elements(By.XPATH, f"//option[contains(text(), '{professional_activity_uf}')]")[-1].click()
            self.find_elements(By.ID, 'preencheCategoriaNivelBolsa')[8].click()
        if text:
            text_input.send_keys(text)

        # Buscando
        text_input.send_keys(Keys.ENTER)

        # Obtendo os resultados
        try:
            return self._get_results(max_results=max_results)
        except:
            print(f'An error occurred while getting the results. {len(self.results_pages_source)} results obtained.')
            print('Use .save_results method to save them.')
            raise

    def _get_results(self, max_results=10):
        self.results_pages_source = {}
        next_page = True
        missing_results = max_results

        while next_page and len(self.results_pages_source.keys()) < max_results:
            results_count = len(self.find_elements(By.XPATH, "//div[@class = 'resultado']/ol/li"))
            missing_results = max_results - len(self.results_pages_source.keys())
            for i in range(min(results_count, missing_results)):
                results = self.find_elements(By.XPATH, "//div[@class = 'resultado']/ol/li")
                result = results[i]

                # Abre modal do resultado e clica para abrir currículo
                result.find_element(By.TAG_NAME, 'a').click()
                WebDriverWait(self, 10).until(abreCV())

                # Muda para a nova aba
                WebDriverWait(self, 50).until(tabs(more_than=1))
                self.switch_to.window(self.window_handles[1])

                # Exibe o nome do pesquisador
                time.sleep(2)
                reseacher_name = self.find_element(By.XPATH, "//h2[@class = 'nome']").text
                lattes_url = self.find_element(By.XPATH, "//ul[@class='informacoes-autor']/li").text.split('CV: ')[-1]
                lattes_id = lattes_url.split('/')[-1]

                self.results_pages_source[lattes_id] = self.page_source

                # Fecha aba e volta para os resultados
                self.close()
                WebDriverWait(self, timeout=50).until(tabs(equals=1))
                self.switch_to.window(self.window_handles[0])
                self.execute_script("""document.querySelector("a.bt-fechar").click()""")

            try:
                next_page_button = self.find_element(By.XPATH, "//font[@color='#ff0000']/parent::*/following-sibling::a")
                next_page_button.click()
                next_page = True
            except NoSuchElementException:
                next_page = False
            
        return self.results_pages_source

    def _set_atuacao_profissional(self, grande_area, area=None, subarea=None, especialidade=None):
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
        results = results if results else self.results_pages_source
        for k, v in results.items():
            with open(os.path.join(folder_path, f'{k}.html'), 'w', encoding='utf-8') as f:
                f.write(v)