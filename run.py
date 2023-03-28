from lattes_scraper import LattesScraper

with LattesScraper(teardown=False, headless=False) as scraper:
    mode = 'Assunto'
    text = 'visao computacional'
    areas = ('Ciências da Saúde', 'Odontologia', 'Ortodontia')
    scraper.search(mode, text, areas)