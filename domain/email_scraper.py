"""
    Interface of scraper
"""

from domain.email_scraper_port import EmailScraperPort

class EmailScraper:
    def __init__(self, scraperAdapter: EmailScraperPort):
        self.adapter = scraperAdapter

    def connect(self):
        return self.adapter.connect()

    def scrape(self):
        return self.adapter.scrape()
