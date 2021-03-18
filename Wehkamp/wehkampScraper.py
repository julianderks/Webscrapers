import requests
import pandas as pd
import datetime
from lxml import html
import json


base_url = 'https://www.wehkamp.nl/'

headers = {
'accept': '*/*',
'Referer': 'https://www.wehkamp.nl/kleding/',
'User-Agent': 'XXXXXXX',
'content-type': 'application/json',}

# get
def read_page(pagenumber):
    base_url = 'https://www.wehkamp.nl/kleding/'
    response = requests.get(base_url + '?pagina=' + str(pagenumber), headers=headers)
    print(response.url)
    
    # This indicates we went over the final page
    if (response.url == base_url) & (pagenumber != 1):
        return None, False

    tree = html.fromstring(response.content)
    return tree.xpath('//article//@href'), True

# Get more detailed info (like stock per SKU)
def query_article(url):
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)

    # # Name of the Wehkamp script that contains product data
    try:
        script = tree.xpath('//script[contains(., "__REDUX_STATE__")]/text()')[0]
    except:
        script = tree.xpath('//script[contains(., "__REDUX_STATE__")]/text()')
        
    text = json.loads(script.strip('window.__REDUX_STATE__=').replace('undefined', '999'))
    return text

def extract_article_data(response, article_url, df):
    ArticleDict = {}
    ArticleDict['Article url'] = article_url

    try:
        x = response['product']['activeProduct']['taxonomy']['breadcrumbs']
    except:
        print('ERROR: Breadcrumbs not loaded properly..')
    
    try:
        ArticleDict['Category'] = x[-1]['name']
    except:
        print('Error: Category Not found...')

    try:
        ArticleDict['Targetgroup'] = x[-3]['name']
    except:
        print('Error: Targetgroup Not found...')
    
    try:
        x = response['product']['activeProduct']['productInformation']
    except:
        print('Error: productinformation Not found...')
    
    try:
        ArticleDict['Description'] = x['description']
    except:
        print('Error: Description Not found...')
        
    try:
        ArticleDict['Geslacht'] = x['geslacht']
    except:
        print('Error: Geslacht Not found...')
            
    try:
        ArticleDict['EAN'] = x['ean']
    except:
        print('Error: EAN Not found...')
    
    for prop in x['properties']:
        if prop['label'] in ['Kleur','Materiaal', 'Voering']:
            ArticleDict[prop['label']] = prop['value']
            
    x = response['product']['activeProduct']['buyingArea']
        
    try:
        ArticleDict['Brand'] = x['brand']
    except:
        print('Error: Brand Not found...')
    
    try:
        ArticleDict['Name'] = x['originalTitle']
    except:
        print('Error: Name Not found...')
    
    try:
        ArticleDict['Code'] = x['productNumber']
    except:
        print('Error: Code Not found...')
        
    try:
        ArticleDict['Number of Reviews'] = x['reviewSummary']['numberOfReviews']
    except:
        print('Error: #Review Not found...')
    
    try:
        ArticleDict['Avg. Review rating'] = x['reviewSummary']['rating']
    except:
        print('Error: Review rating Not found...')
    
    try:
        ArticleDict['ASP'] = x['pricing']['price']/100
    except:
        print('Error: ASP can\'t be found')
    
    try:
        ArticleDict['OSP'] = x['pricing']['scratchPrice']/100
    except:
        print('Error: OSP can\'t be found')
    
    try:
        ArticleDict['Discount'] = x['pricing']['discount']/100
    except:
        print('Error: Discount can\'t be found')
        
    try:
        ArticleDict['Image url'] = x['images'][0]['url']
    except:
        print('Error: Image can\'t be found')
        
    try:
        SKUs = x['rollups'][1]
    except:
        SKUs = x['rollups'][0]
    
    if SKUs['code'] == 'SizeCode':
        for SKU in SKUs['items']:
            ArticleDict['Size'] = SKU['label']
            ArticleDict['Stock'] = SKU['itemsInStock']
            df = df.append(ArticleDict, ignore_index=True)
    return df

def scrape_website():
    pagenumber, articlenumber = 1, 1
    df = pd.DataFrame()

    article_urls, notLastPage = read_page(pagenumber)
    while notLastPage:
        print(f'Page {pagenumber}')
        
        # Iterate over articles on productpage
        for article_url in article_urls:
            try:
                response = query_article(article_url)
            except:
                print('Can\'t find article, continuing...')
                continue

            print(f'Queried product {articlenumber} {article_url}')
            df = extract_article_data(response,article_url,df)    

            articlenumber+=1 
        pagenumber+=1
        article_urls, notLastPage = read_page(pagenumber)
        notLastPage = False

    df['Description'] = df['Description'].str.replace("[<].*?[>]|[&].*?[;]", "", regex=True)
    #df = df.astype({"ASP": 'str', "Avg. Review rating": 'str', "Discount": 'str',
    #                             "Discount": 'str', "Number of Reviews": 'str', "OSP": 'str', "Stock": 'str'})

    df['Date'] = datetime.date.today()
    df.to_pickle(f"wehkamp_articles.pkl")
