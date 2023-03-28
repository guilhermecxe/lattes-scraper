# Lattes Scraper

A package to scrape data from Plataforma Lattes.

Example:

```py
>>> from lattes_scraper import LattesScraper
>>> with LattesScraper(teardown=True, headless=False) as scraper:
        mode = 'Assunto'
        text = 'visao computacional'
        areas = ('Ciências da Saúde', 'Odontologia', 'Ortodontia')
        scraper.search(mode, text, areas)
        
Fernando César Torres
Thyciana Rodrigues Ribeiro
Viviane Veroni Degan
Alexandre Protásio Vianna
Giovana Cherubini Venezian
```