from lattes_scraper import LattesScraper

with LattesScraper(teardown=True, headless=False) as scraper:
    mode = 'Assunto'
    text = 'visao computacional'
    areas = ('Ciências da Saúde', 'Odontologia', 'Ortodontia')
    results = scraper.search(mode, text, areas)

for r in results:
    pass