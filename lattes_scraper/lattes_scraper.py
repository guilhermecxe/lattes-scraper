from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from shutil import which
import os

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def search(self, mode, text, areas=None):
        # Obtendo a página
        self.get('https://buscatextual.cnpq.br/buscatextual/busca.do')

        # Aplicando os filtros
        if mode == 'Assunto':
            self.find_element(By.XPATH, "//input[@id = 'buscaAssunto']").click()
        if areas:
            self._set_atuacao_profissional(*areas)

        # Escrevendo o texto de busca
        text_input = self.find_element(By.XPATH, "//input[@id = 'textoBusca']")
        text_input.send_keys(text)

        # Buscando
        text_input.send_keys(Keys.ENTER)

        # Obtendo os resultados
        return self._get_results()

    def _get_results(self):
        results_count = len(self.find_elements(By.XPATH, "//div[@class = 'resultado']/ol/li"))
        results_pages_source = []

        for i in range(results_count):
            results = self.find_elements(By.XPATH, "//div[@class = 'resultado']/ol/li")
            result = results[i]

            # Abre modal do resultado e clica para abrir currículo
            result.find_element(By.TAG_NAME, 'a').click()
            WebDriverWait(self, 10).until(abreCV())

            # Muda para a nova aba
            WebDriverWait(self, 50).until(tabs(more_than=1))
            self.switch_to.window(self.window_handles[1])

            # Exibe o nome do pesquisador
            reseacher_name = self.find_element(By.XPATH, "//h2[@class = 'nome']").text
            print(reseacher_name)

            results_pages_source.append(self.page_source)

            # Fecha aba e volta para os resultados
            self.close()
            WebDriverWait(self, timeout=50).until(tabs(equals=1))
            self.switch_to.window(self.window_handles[0])
            self.execute_script("""document.querySelector("a.bt-fechar").click()""")

        return results_pages_source

    def _set_atuacao_profissional(self, grande_area, area=None, subarea=None, especialidade=None):
        self.find_element(By.ID, 'filtro4').click()
        self.find_element(By.XPATH, f"//option[text()='{grande_area}']").click()
        if area: self.find_element(By.XPATH, f"//option[text()='{area}']").click()
        if subarea: self.find_element(By.XPATH, f"//option[text()='{subarea}']").click()
        if especialidade: self.find_element(By.XPATH, f"//option[text()='{especialidade}']").click()
        self.find_elements(By.ID, 'preencheCategoriaNivelBolsa')[4].click()