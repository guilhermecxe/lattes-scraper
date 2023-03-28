# Lattes Scraper

A package to scrape data from Plataforma Lattes.

## Requirements:

- `Python==3.9` or `Python==3.10`
- `selenium==4.8.3`

## Install

Clone:
```bash
$ git clone https://github.com/guilhermecxe/lattes-scraper.git
$ cd lattes-scraper
```

Run:
```bash
$ pip install -e .
```

## Example

Run:
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