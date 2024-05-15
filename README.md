# Lattes Scraper

Este é um pacote que realiza buscas na plataforma Currículo Lattes e extrai arquivos HTMLs referentes ao currículos encontrados.

## Requisitos:

- `Python==3.9` or `Python==3.10`
- `selenium==4.8.3`

## Instalação

Clone:
```bash
$ git clone https://github.com/guilhermecxe/lattes-scraper.git
$ cd lattes-scraper
```

Execute:
```bash
$ pip install -e .
```

## Exemplo

Execute o código abaixo para salvar, na pasta `cvs`, os currículos encontrados pela busca:
```py
from lattes_scraper import LattesDriver

configurations = {
    'last_update': 12,
    'foreigners': False,
    'productivity_scholarship': ['1A'],
    'professional_activity_area': {
        'grande_area': 'Ciências Exatas e da Terra',
        'area': 'Ciência da Computação',
        'subarea': 'Metodologia e Técnicas da Computação',
        'especialidade': 'Engenharia de Software',
    },
    'txt_saving': {
        'folder': 'cvs/'
    },
}

with LattesDriver(configurations, headless=False) as scraper:
    scraper.search()