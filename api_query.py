import scholarly

def PubMed(search_term):
    return 'what they return'

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


def BioArchive():
    pass

def MedArchive():
    pass

