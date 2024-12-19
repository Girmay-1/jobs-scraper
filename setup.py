from setuptools import setup, find_packages

setup(
    name="job_scraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests>=2.26.0',
        'beautifulsoup4>=4.9.3',
        'selenium>=4.1.0',
        'python-dotenv>=0.19.0',
        'sqlalchemy>=1.4.23',
        'flask>=2.0.1',
        'webdriver-manager>=3.5.2'
    ]
)