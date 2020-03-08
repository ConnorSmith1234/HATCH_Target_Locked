import requests

from bs4 import BeautifulSoup


USER_COOKIE = {'PHPSESSID': '6lm3i3jevbhqhbu1o3fsnm3u64',
               'NSC_iptujoh.dg.bd.vl-iuuq-wt': 'ffffffff09f7fa6f45525d5f4f58455e445a4a423660',
               'path': '/',
               'domain': '.www.hgmd.cf.ac.uk',
               'Expires': 'Tue, 19 Jan 2038 03:14:07 GMT'
               }


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
