from setuptools import setup, find_packages

setup(
    author="Guilherme Alves",
    description="A package to scrape data from Plataforma Lattes.",
    name="lattes_parser",
    version="0.1.0",
    packages=find_packages(include=["lattes_scraper"]),
    install_requires=[
        'selenium==4.8.3',
    ],
    python_requires='>=3.9',
)