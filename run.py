from lattes_scraper import LattesScraper

with LattesScraper(teardown=True, headless=False) as scraper:
    mode = 'Nome'
    text = ''
    areas = ('Ciências Agrárias', 'Zootecnia', 'Genética e Melhoramento dos Animais Domésticos')
    UF = 'Goiás'
    results = scraper.search(mode, text, areas, professional_activity_uf=UF, max_results=15)