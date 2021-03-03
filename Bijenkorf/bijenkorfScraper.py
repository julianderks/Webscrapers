import requests
import pandas as pd
import datetime


headers = {
    'authority': 'www.debijenkorf.nl',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'content-type': 'application/graphql',
    'accept': '*/*',
    'origin': 'https://www.debijenkorf.nl',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.google.nl',
    'accept-language': 'en-US,en;q=0.9',
    }

baseQuery = "query { productListing(query: \"\"\"fh_location=//catalog01/nl_NL/**CATEGORYPLACEHOLDER**&fh_view_size=240&**INDEXPLACEHOLDER**&country=NL&chl=1&vt=unknown\"\"\", locale: \"nl-NL\") { \n    navigation {\n        products {\n            \n    brand {\n        \n    name\n\n    }\n    code\n    colorCount\n    currentVariantProduct {\n        \n    availability {\n        \n    available\n    availableFuture\n    stock\n\n    }\n    code\n    color\n    current\n    images {\n        \n    position\n    type\n    url\n\n    }\n    overriddenPrices {\n        \n    currencyCode\n    type\n    value\n\n    }\n    sellingPrice {\n        \n    currencyCode\n    type\n    value\n\n    }\n    signings {\n        \n    discount {\n        \n    key\n    text\n\n    }\n    merchandise {\n        \n    key\n    text\n\n    }\n\n    }\n    trackingMetadata\n    size\n    url\n\n    }\n    defaultVariantCode\n    description\n    designer\n    displayName\n    displayProperties {\n        \n    currentVariantSelected\n    detailPageVariation\n\n    }\n    gift\n    name\n    subBrand {\n        \n    name\n\n    }\n    supplierModel\n    sustainable\n    trackingMetadata\n    url\n    variantProducts (limit:4, groupBy: COLOR) {\n        \n    availability {\n        \n    available\n    availableFuture\n    stock\n\n    }\n    code\n    color\n    current\n    images {\n        \n    position\n    type\n    url\n\n    }\n    overriddenPrices {\n        \n    currencyCode\n    type\n    value\n\n    }\n    sellingPrice {\n        \n    currencyCode\n    type\n    value\n\n    }\n    signings {\n        \n    discount {\n        \n    key\n    text\n\n    }\n    merchandise {\n        \n    key\n    text\n\n    }\n\n    }\n    trackingMetadata\n    size\n    url\n\n    }\n    recommendationRanking\n\n        }\n        pagination {\n            \n    currentPage {\n        \n    pageNumber\n    query\n    relativeUrl\n\n    }\n    nextPage {\n        \n    pageNumber\n    query\n    relativeUrl\n\n    }\n    previousPage {\n        \n    pageNumber\n    query\n    relativeUrl\n\n    }\n    totalItemCount\n    viewSize\n\n        }\n    }\n } }"

# Manually found that these specific querries result in articles that can be seperated in 4 the Target group categories
groupQuery = [
                ['Men', 'Women', 'Boys', 'Girls'], 
                ['categories<{catalog01_80}/categories<{catalog01_80_890}','categories<{catalog01_60}/categories<{catalog01_60_880}',
                'categories<{catalog01_100}/baby_geslacht>{jongens}','categories<{catalog01_100}/baby_geslacht>{meisjes}']
                ]

queries = {targetGroup: baseQuery.replace('**CATEGORYPLACEHOLDER**', targetGroupQuery) for targetGroup, targetGroupQuery in zip(*groupQuery)}


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

def scrape_website():
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



 