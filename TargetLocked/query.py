import requests
import json
import xml.etree.ElementTree as ET 
from bs4 import BeautifulSoup
from datetime import datetime
from fuzzywuzzy import fuzz
from nltk.tokenize import sent_tokenize, word_tokenize
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions

import argparse
import numpy as np

from bs4 import BeautifulSoup
from stopwords import STOPWORDS

USER_COOKIE = {'PHPSESSID': '5jl72rsofffno6adngjmnc3t83',
               'NSC_iptujoh.dg.bd.vl-iuuq-wt': 'ffffffff09f7faf345525d5f4f58455e445a4a423660',
               'path': '/',
               'domain': '.www.hgmd.cf.ac.uk',
               'Expires': 'Tue, 19 Jan 2038 03:14:07 GMT'
               }

HPO_OBOFILE = 'hp.obo'
DISEASE_LIST = 'disease_names.json'
CLEAN_DISEASE_LIST = 'clean_dis_list.json'
W2V = 'bio_nlp_vec/PubMed-shuffle-win-30.bin'

URL = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/2c29526e-5a45-4973-8308-c0a59a0a9cad'
API_KEY = 'Drp653MSdtiGIbau3GKt3KfxjUs3_bC-l9TUf4BEkfM0'

GENES = json.load(open('gene_names.json','r'))
ANIMALS = json.load(open('animal_names.json','r'))

####################################################################################################
# API Calls ########################################################################################
####################################################################################################

class Article:
    def __init__(self, article_title, article_authors, article_abstract, article_url, from_api, article_date):
        self.title = article_title
        self.authors = article_authors
        self.abstract = article_abstract
        self.url = article_url
        self.api = from_api
        self.date = article_date
        self.date_seconds = None
        self.species = []
        self.diseases = []
        self.genes = []
        self.mutation_type = []

    def to_json():            
        return json.dumps(self.__dict__)        


def Parser(response):
    with open('test.xml', 'wb') as f: 
        f.write(response.content) 
    return ET.parse('test.xml')


def BioArchive(query, filter='', pageSize=20):
    api_endPoint = "https://api.rxivist.org/v1/papers"
    parameters = {}
    parameters['q'] = query
    parameters['page_size'] = pageSize
    articles = []
    response = requests.get(api_endPoint, params=parameters)
    # Validate response
    if(response.status_code != 200):
        raise CustomError("Failed to query BioArchive")
    else:
        response = response.json()
        response = response['results']
    # Parse response
    for result in response:
        title = result['title']
        abstract = result['abstract']
        api = "BioArchive"
        url = result['biorxiv_url']
        date = result['first_posted']
        authors = []
        authorsList = result['authors']
        for author in authorsList:
            authors.append(author['name'].encode().decode('utf-8','ignore'))
        articles.append(Article(title, authors, abstract, url, api, date))

    return articles  


def MedArchive(query):
    api_endPoint = "https://www.medrxiv.org/search/"
    api_endPoint += query
    articles = []
    response = requests.get(api_endPoint)    
    # Validate response
    if(response.status_code != 200):
        raise CustomError("Failed to query BioArchive")
    soup = BeautifulSoup(response.content, 'html.parser')
    spans = soup.find_all('span', attrs={'class':'highwire-cite-title'})
    titles = []
    index = 0
    for span in spans:
        if index == 0:
            #titles.append(span.text)
            articles.append(Article(span.text.decode('utf-8'), "", "", "", "MedArchive", ""))
            index = 2
        index -= 1
    #print (titles)
    spans = soup.find_all('div', attrs={'class':'highwire-cite-authors'})
    authors = []
    index = 0
    for span in spans:
        authors.append(span.text.split(','))
        articles[index].authors = span.text.decode('utf-8').split(',')
        # print(span.text.split(','))
        index += 1
    # print (authors)
    spans = soup.find_all('span', attrs={'class':'highwire-cite-metadata-doi highwire-cite-metadata'})
    urls = []
    index = 0
    for span in spans:
        urls.append(span.text.replace('doi: ',""))
        articles[index].url = span.text.replace('doi: ',"")
        index += 1
    #print (urls)
    abstracts = []
    index = 0
    for url in urls:
        response = requests.get(url)
        #print(response)
        articleContent = BeautifulSoup(response.content, 'html.parser')
        spans = articleContent.find('div', attrs={'class':'section abstract'}, id="abstract-1")
        for span in spans:
            #abstracts.append(span.text.replace("Abstract",""))
            #print(span.text.replace("Abstract",""))
            articles[index].abstract = span.text.decode('utf-8').replace("Abstract","").replace("\n","")
            #title
            pubTag = articleContent.find('meta', attrs={'name':'article:published_time'})
            #print(pubTag['content'])
            articles[index].date = pubTag['content']
        index += 1

    return articles


# TODO: rate limited
def PubMed(query):
    #Pudmed IDs
    api_endPoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    parameters = {}
    parameters['db'] = "pubmed"
    parameters['term'] = query
    parameters['usehistory'] = 'y'
    articles = []

    response = requests.get(api_endPoint, params=parameters)

    # Parse
    tree = Parser(response)
    # Webenv
    webenv = tree.find('WebEnv').text
    querykey = tree.find('QueryKey').text
    
    # Summary
    api_endPoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    parameters = {}
    parameters['db'] = "pubmed"
    parameters['query_key'] = querykey
    parameters['WebEnv'] = webenv

    response = requests.get(api_endPoint, params=parameters)
    tree = Parser(response)
    
    docs = []
    docSums = tree.findall('./DocSum')
    
#     print(docSums)
    #DocSum
    for doc in docSums:
        subdoc = doc.findall('Item')
        article = Article("","","","","PubMed","")
        article.authors = []
        for doc in subdoc:
            if(doc.get('Name') == "Title"):
                article.title = doc.text
            if(doc.get('Name') == "AuthorList"):
                for author in doc.findall('Item'):
                    article.authors.append(author.text)
            if(doc.get('Name') == "PubDate"):
#                 print("cool")
                pass
        articles.append(article)
    
    
    # Abstract
    api_endPoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    parameters = {}
    parameters['db'] = "pubmed"
    parameters['query_key'] = querykey
    parameters['WebEnv'] = webenv
    parameters['rettype'] = 'abstract'
    parameters['retmode'] = 'text'

    response = requests.get(api_endPoint, params=parameters)

    response = response.content.decode().split('\n\n')
    filtered_names = [x for x in response if x]
    length = len(filtered_names)/6
    index = 0
    for i in range(int(length)):
        index = 4*(i+1) + 2*i
        articles[i].abstract = filtered_names[index].replace("\n","")
    
#     articles_json = []
#     for article in articles:
#         articles_json.append(json.dumps(article.__dict__))
    

    return articles #json.dumps({"articles": articles_json})


# TODO: this works if you can figure out proxy switching
def google_scholar(search_term, num_documents=10):
    all_query_results = scholarly.search_pubs_query(search_term)

    query_results = []
    for i in range(num_documents):
        print(i)
        try:
            pub = next(all_query_results)
        except StopIteration:
            break

        metadata = {}
        metadata['abstract'] = pub.bib.get('abstract', None)
        metadata['title'] = pub.bib.get('title', None)
        metadata['author'] = pub.bib.get('author', None)
        metadata['year'] = pub.bib.get('year', None)
        metadata['journal'] = pub.bib.get('journal', None)
        metadata['publisher'] = pub.bib.get('publisher', None)
        metadata['ID'] = pub.bib.get('ID', None)
        metadata['url'] = pub.bib.get('url', None)
        metadata['eprint'] = pub.bib.get('eprint', None)
        metadata['num_citations'] = pub.citedby
        metadata['document_type'] = pub.bib.get('ENTRYTYPE', None)

        query_results.append(metadata)

    print(f'{len(query_results)} returned')

    return query_results


####################################################################################################
# Tagging ##########################################################################################
####################################################################################################

def gene_tagger(abstract):

    found_genes = [gene for gene in GENES if gene in abstract]    
    
    non_duplicates = []
    for gene in found_genes:
        if sum([1 for result in found_genes if gene in result]) == 1:
            non_duplicates.append(gene)
            
    return non_duplicates


def disease_tagger(text):
    authenticator = IAMAuthenticator(API_KEY)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2019-07-12',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(URL)

    response = natural_language_understanding.analyze(
        text=text,
        features=Features(categories=CategoriesOptions(limit=10))).get_result()

    diseases = []
    for category in response['categories']:

        if category['label'].startswith('/health and fitness/disease/'):
            disease = category['label'].split('/')[-1]
            diseases.append({'score':category['score'],
                             'disease':disease})

    return diseases


def animal_tagger(abstract):
    abstract_tokens = word_tokenize(abstract)
    
    found_animals = [animal for animal in ANIMALS if 90 <max([fuzz.ratio(word.lower(),animal.lower()) for word in abstract_tokens])]
    
    non_duplicates = []
    for animal in found_animals:
        if sum([1 for result in found_animals if animal in result]) == 1:
            non_duplicates.append(animal)
            
    return non_duplicates


def convert_date(date_str):
    """converts arbitrary dates to seconds since epoch"""

    input_date = datetime.strptime(date_str,'%Y-%m-%d')

    seconds_since_epoch = (input_date-datetime(1970,1,1)).total_seconds()

    return seconds_since_epoch


def string_matcher(search_string, abstract, fuzzy=False):
    """looks for the search string inside the abstract
    if fuzzy, uses partial matching"""
    
    if fuzzy:
        found = 90 < fuzz.partial_ratio(search_string.lower(), abstract.lower())
    else:
        found = search_string.lower() in abstract.lower()

    return found

####################################################################################################
# Pipeline #########################################################################################
####################################################################################################

def call_apis(query_string):
    bio_archive = BioArchive(query_string, '', 10)
    med_archive = MedArchive(query_string)

    results = med_archive + bio_archive

    return results

def tag_articles(articles):



    for article in articles:
        abstract = article.abstract.lower()
        article.genes = gene_tagger(article.abstract)
        article.diseases = disease_tagger(abstract)
        article.species = animal_tagger(abstract)   
        article.date_seconds = convert_date(article.date) 

    article_dict = [article.__dict__ for article in articles]

    return article_dict

####################################################################################################
# Sort Articles ####################################################################################
####################################################################################################




def get_diseases_for_gene(gene_name):
    """get disease for gene name from HGMD database
    Args:
        gene_name (TYPE): name of gene
    Returns:
        TYPE: list of diseases
    """
    GENE_URL = f'http://www.hgmd.cf.ac.uk/ac/gene.php?gene={gene_name}'
    resp = requests.get(GENE_URL, cookies=USER_COOKIE)
    parsed_resp = BeautifulSoup(resp.text, 'lxml')

    try:
        parsed_resp = parsed_resp.find_all('table')[2].find_all('td')[0::3]
        return [BeautifulSoup.get_text(disease) for disease in parsed_resp]
    except IndexError:
        return []



def read_disease_list():
    return json.load(open(DISEASE_LIST, 'r'))

def read_clean_disease_list():
    return json.load(open(CLEAN_DISEASE_LIST, 'r'))


def clean_dis_list():
    dis_list = read_disease_list()
    cleaned_dis_list = list()
    for item in dis_list:
        cleaned_item = list()
        for elem in item.split(' '):
            elem = elem.replace(',', '')
            elem = elem.lower()
            if elem not in STOPWORDS:
                cleaned_item.append(elem)
        cleaned_dis_list.append(cleaned_item)
    with open("clean_dis_list.json", "w") as write_file:
        json.dump(cleaned_dis_list, write_file)


def get_onehot_vector(target_list, key):

    """get loosely related one hot vector of list based on key
    Args:
        list (TYPE): Description
        key (TYPE): Description
    """
    onehot = np.zeros(len(key), dtype='float')
    for idx, sublist in enumerate(key):
        for item in target_list:
            for elem in item.split(' '):
                elem = elem.lower()
                elem = elem.replace(',', '')
                if elem in sublist:
                    onehot[idx] = 1.0
    return onehot


def get_onehot_vector_scored(target_list, key):

    """get loosely related one hot vector of list based on key
    Args:
        list (TYPE): Description
        key (TYPE): Description
    """
    onehot = np.zeros(len(key), dtype='float')
    for idx, sublist in enumerate(key):
        for item, score in target_list:
            for elem in item.split(' '):
                elem = elem.lower()
                elem = elem.replace(',', '')
                if elem in sublist:
                    onehot[idx] = score
    return onehot


def accuracy_score_onehot(target_list, given_list):
    """compare
    Args:
        target_list (TYPE): Description
        given_list (TYPE): Description
        disease_list (TYPE): Description
    """
    disease_list = read_clean_disease_list()
    target_vector = get_onehot_vector(target_list, disease_list)
    given_vector = get_onehot_vector_scored(given_list, disease_list)
    return 1 - (np.linalg.norm(target_vector - given_vector) / len(disease_list))


def accuracy_score_direct(target_list, given_list):
    score = 0
    disease_list = []
    for disease in target_list:
        disease_list += [text.lower() for text in disease.replace(',', '').split(' ') if text not in STOPWORDS]
    dl_set = set(disease_list)
    given_disease_list = []
    for item in given_list:
        given_disease_list += [text.lower() for text in item.replace(',', '').split(' ') if text not in STOPWORDS]
    gdl_set = set(given_list)
    return float(len(dl_set & gdl_set)) * float(len(dl_set & gdl_set)) / float(len(dl_set) + len(gdl_set - dl_set))


def hgmd_doc_score(gene, dis_score_list):
    """calculate score from json
    Args:
        doc_json (TYPE): Description
    """
    gene_disease_list = get_diseases_for_gene(gene)
    return accuracy_score_direct(gene_disease_list, dis_score_list)


def main():

    parser = argparse.ArgumentParser(description='A tutorial of argparse!')
    parser.add_argument("--query")
    args = parser.parse_args()
    query = args.query
    articles = call_apis(query)

    tagged_articles = tag_articles(articles)

    # score the articles
    gene = query
    for article in tagged_articles:
        disease_list = [disease['disease'] for disease in article['diseases']]
        
        if disease_list:
            score = hgmd_doc_score(gene, disease_list)
        else:
            score = 0
        
        article['score'] = score

    sorted_articles = sorted(tagged_articles, key=lambda article: article['score'], reverse=True)

    print(sorted_articles)


if __name__ == "__main__":
    main()
