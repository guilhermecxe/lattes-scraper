# Lattes Scraper

Este é um pacote que realiza buscas na plataforma Currículo Lattes e extrai arquivos html referentes ao currículos encontrados.

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
from lattes_scraper import LattesScraper

filters = {
    'mode': 'Nome',
    'text': '',
    'foreigner': False,
    'areas': ('Ciências Humanas', 'Ciência Política'),
    'professional_activity_uf': 'Goiás',
}

preferences = {
    'last_update': 12,
}

max_results = 15
backup_name = 'Example'
backup_id = None
sleep = 2

# Um backup é criado sempre que um erro ocorre ou a busca termina
with LattesScraper(teardown=True, headless=True, show_progress=False,
                   backup_name=backup_name, backup_id=backup_id) as scraper:
    scraper.implicitly_wait(30)
    scraper.search(max_results, filters, preferences)

# Para obter o id do backup criado ou atualizado:
print(scraper.backup.id)

# Para obter um dicionário dos arquivos html salvos:
print(scraper.backup.item)

# Para salvar os arquivos html em uma pasta: 
scraper.save_results('data/')


```