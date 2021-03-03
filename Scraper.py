
from Bijenkorf import bijenkorfScraper
from Wehkamp import wehkampScraper
import export

# Call bijenkorf scraper and which saves the resulting table as a pickle file
bijenkorfScraper.scrape_website()
export.to_DWH(table = 'bijenkorf_articles')
# Call wehkamp scraper and which saves the resulting table as a pickle file
wehkampScraper.scrape_website()
export.to_DWH(table = 'wehkamp_articles')
