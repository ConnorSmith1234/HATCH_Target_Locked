import requests
import obonet
import numpy as np
import json

from bs4 import BeautifulSoup
from stopwords import STOPWORDS

USER_COOKIE = {'PHPSESSID': '6lm3i3jevbhqhbu1o3fsnm3u64',
               'NSC_iptujoh.dg.bd.vl-iuuq-wt': 'ffffffff09f7fa6f45525d5f4f58455e445a4a423660',
               'path': '/',
               'domain': '.www.hgmd.cf.ac.uk',
               'Expires': 'Tue, 19 Jan 2038 03:14:07 GMT'
               }

HPO_OBOFILE = 'hp.obo'
DISEASE_LIST = 'disease_names.json'
CLEAN_DISEASE_LIST = 'clean_dis_list.json'
W2V = 'bio_nlp_vec/PubMed-shuffle-win-30.bin'


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


def get_hpo_names():
    graph = obonet.read_obo(HPO_OBOFILE)
    return {id_: data.get('name') for id_, data in graph.nodes(data=True)}


def get_hpo_embeddings(w2v):
    id_name_list = get_hpo_names()
    id_embed_list = id_name_list.copy()
    for hpo in id_name_list:
        text = id_name_list[hpo]
        text_list = text.split(' ')
        embedding = np.zeros(w2v.vector_size)
        for text in text_list:
            if text in w2v.vocab:
                embedding += w2v[text]
        id_embed_list[hpo] = embedding
    return id_name_list, id_embed_list


def _find_closest_hpo(embed_list, disease, w2v):
    disease_list = disease.split(' ')
    dis_embed = np.zeros(w2v.vector_size)
    for text in disease_list:
        if text in w2v.vocab:
            dis_embed += w2v[text]
    if np.linalg.norm(dis_embed) == 0:
        return None
    arg = np.argmin(np.linalg.norm(np.subtract(dis_embed,list(embed_list.values())),axis=1))
    return list(embed_list)[arg]


def find_closest_hpo(disease, w2v):
    name_list, embed_list = get_hpo_embeddings(w2v)
    hpo = _find_closest_hpo(embed_list, disease, w2v)
    if hpo:
        return name_list[hpo]
    return None


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

