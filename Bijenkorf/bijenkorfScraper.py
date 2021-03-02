import requests
import pandas as pd
from .utils import headers, queries
import datetime

def query_article(productCode, productVariantCode, productReferer):
  headers['referer'] = productReferer

  params = (
    ('productCode', productCode),
    ('productVariantCode', productVariantCode),
    ('cached', 'false'),
    ('locale', 'nl_NL'),
    ('api-version', '2.36'),
  )

  response = requests.get('https://ceres-catalog.debijenkorf.nl/catalog/product/show', headers=headers, params=params)
  return response.json()

def scrape():
    startindex = 0
    df = pd.DataFrame()
    skipped = []

    for targetgroup in ['Men', 'Women', 'Boys', 'Girls']:
        index, artnr = 0, 0

        # Keep quering next productlists until you receive an empty list.
        while(True):
            # Replace the indexvariable in the query string
            query = queries[targetgroup].replace('**INDEXPLACEHOLDER**', f'fh_start_index={index}')

            # Pass the query to the server
            response = requests.post('https://www.debijenkorf.nl/api/graphql', headers=headers, data=query)

            # Transform response in json and get variables of interest
            data = response.json()
            productList = data['data']['productListing']['navigation']['products']
            totalItemCount = data['data']['productListing']['navigation']['pagination']['totalItemCount']
            # Let the server think you are accesing the article from the 'current' page
            referer = 'https://www.debijenkorf.nl/' + \
                    data['data']['productListing']['navigation']['pagination']['currentPage']['relativeUrl']

            # Check if the productlist has products, else break the while loop
            print(f'Current query index: {index}')
            if len(productList) == 0:
                break

            # Create dictionary that will hold all the variables of interest for each article SKU
            articleSKU = {}

            # Iterate over general article info in queried productlist
            for data in productList:
                artnr += 1

                articleSKU['Brand'] = data['brand']['name']
                articleSKU['Code'] = data['code']
                articleSKU['Name'] = data['name']
                print(f'Article {artnr}/{totalItemCount}: {data["name"]}')

                # Query detailed data for current article
                articleQuery = query_article(articleSKU['Code'], data['currentVariantProduct']['code'], referer)

                articleSKU['Category01'] = targetgroup

                # Category 2 untill 4 may sometimes be unpresent
                for i in range(2, 5):
                    try:
                        articleSKU[f'Category0{i}'] = articleQuery['data']['product']['categoryPath'][i]['name']
                    except (IndexError, TypeError):
                        articleSKU[f'Category0{i}'] = None

                # Obtain data on a SKU level
                try:
                    for data in articleQuery['data']['product']['variantProducts']:
                        articleSKU['OSP'] = data['sellingPrice']['value']

                        try:
                            articleSKU['ASP'] = data['overriddenPrices'][0]['value']
                        except IndexError:
                            articleSKU['ASP'] = articleSKU['OSP']

                        # Default = low quality, web_detail = high_quality
                        articleSKU['Image URL'] = 'https:' + data['selectionImage']['url'].replace('default', 'web_detail')

                        articleSKU['Size'] = data['size']
                        articleSKU['Color'] = data['color']
                        articleSKU['Stock'] = data['availability']['stock']

                        # Append the SKU article to the final Dataframe
                        df = df.append(articleSKU, ignore_index=True)

                except Exception:
                    print(f"TypeError on article {articleSKU['name']}, code:{articleSKU['code']} & variantCode: {data['currentVariantProduct']['code']}. Skipping...")
                    skipped.append(articleSKU['Name']) 
                
            # Get next 240 articles (max stepsize)
            index += 240

    df['Date'] = datetime.date.today()
    # save problematic articles for manual investigation to further improve the scraper
    with open("bijenkorf_skipped.txt", mode='w') as file:
        print(skipped, file=file)

    df.to_pickle(f"bijenkorf_articles.pkl")



 