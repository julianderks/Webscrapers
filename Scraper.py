from Bijenkorf import bijenkorfScraper, export

# Call bijenkorf scraper and which saves the resulting table as a pickle file
bijenkorfScraper.scrape()
# Upload the pickle file to the Datawarehouse
export.to_DWH()
