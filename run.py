from lattes_scraper import LattesDriver

configurations = {
    # 'last_update': 12,
    'foreigners': False,
    'productivity_scholarship': ['1A'],
    # 'professional_activity_area': {
    #     'grande_area': 'Ciências Exatas e da Terra',
    #     'area': 'Ciência da Computação',
    #     'subarea': 'Metodologia e Técnicas da Computação',
    #     'especialidade': 'Engenharia de Software',
    # },
    'txt_saving': {
        'folder': 'C:/Estudos/Github/lattes-scraper/cvs'
    },
}

with LattesDriver(configurations, teardown=True, headless=False) as scraper:
    scraper.search()