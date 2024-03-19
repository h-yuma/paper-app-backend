import asyncio
import httpx
import json
import sys
import logging
sys.path.append('../')
from set_log import setup_logger
import xml.etree.ElementTree as ET
import time


logger = setup_logger(__name__)

ESEARCH_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EFETCH_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def measure_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 処理の開始時間
        result = func(*args, **kwargs)
        end_time = time.time()  # 処理の終了時間
        elapsed_time = end_time - start_time  # 実行時間の計算      
        print(f"elapsed_time: {elapsed_time:.3f} sec")  
        return result
    return wrapper

async def get_paper_info(pmid):
    # Get paper info from pubmed using PMID
    params = {
        "db": "pubmed",
        "id": str(pmid),
        "retmode": "json"
    }
    try:
        async with httpx.AsyncClient() as client:
            # send request to pubmed
            json_response = await client.get(ESUMMARY_BASE_URL, params=params)
            # change json_response to python object
            response = json.loads(json_response.content)
            logger.info(f'Successfully retrieved paper info for PMID: {pmid}')
    except Exception as e:
        logger.error(f'Error retrieving paper info for PMID: {pmid}')
        logger.error(e)
        return None
    
    result = response['result']
    paper_info = result[str(pmid)]
    title = paper_info['title']
    last_author = paper_info['lastauthor']
    publication_date = paper_info['pubdate']
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"

    return {
        "pmid": pmid,
        "title": title,
        "last_author": last_author,
        "publication_date": publication_date,
        "url": url
    }


def get_paper_abstract(pmid):
    # Get paper abstract from pubmed using PMID
    params = {
        "db": "pubmed",
        "id": str(pmid),
        "retmode": "XML",
    }
    try:
        # send request to pubmed
        xml_response = httpx.get(EFETCH_BASE_URL, params=params)
        logger.info(f'Successfully retrieved paper abstract for PMID: {pmid}')
    except Exception as e:
        logger.error(f'Error retrieving paper abstract for PMID: {pmid}')
        logger.error(e)
        return None

    # parse XML response
    try:
        root = ET.fromstring(xml_response.content)
        abstract = root.find('.//AbstractText').text
    except Exception as e:
        logger.error(f'Error parsing XML response for PMID: {pmid}')
        logger.error(e)
        return None
    
    return abstract

async def get_pmids_from_words(words, retmax=5, minyear=None, maxyear=None):
    # validate mindate and maxdate
    if minyear and maxyear:
        if minyear > maxyear:
            logger.error("minyear should be less than maxyear")
            return None
    
    # join words list to string
    search_phrase = ",".join(words)

    # Get pmids from pubmed using search words
    params = {
        "db": "pubmed",
        "term": search_phrase,
        "datatype": "pdat",
        "retmode": "json",
        "retmax": retmax,
        "mindate": minyear,
        "maxdate": maxyear
    }
    try:
        async with httpx.AsyncClient() as client:
            # send request to pubmed
            json_response = await client.get(ESEARCH_BASE_URL, params=params)
            # change json_response to python object
            response = json.loads(json_response.content)
            logger.info(f'Successfully retrieved paper info for words: {words}')
    except Exception as e:
        logger.error(f'Error retrieving paper info for words: {words}')
        logger.error(e)
        return None
    
    result = response['esearchresult']
    pmid_list = result['idlist']

    return pmid_list

async def get_paper_abstracts_from_words(words, retmax=5, minyear=None, maxyear=None):
    pmid_list = await get_pmids_from_words(words, retmax, minyear, maxyear)
    if pmid_list:
        # abstract_list = await asyncio.gather(
        #     *[get_paper_abstract(pmid) for pmid in pmid_list]
        # )
        # return abstract_list
        abstract_list = []
        for pmid in pmid_list:
            abstract = get_paper_abstract(pmid)
            if abstract:
                abstract_list.append(abstract)
            else:
                pass
        return abstract_list
    else:
        return None


    

@measure_performance
def main():
    result = asyncio.run(get_paper_abstracts_from_words(["bacteria"], \
                                              retmax=5, minyear=2020, maxyear=2021))
    print(result)
    # abst = get_paper_abstract(32293474)
    # print(abst)

if __name__ == "__main__":
    # pmid = 32293474
    # print(get_pmids_from_words(["chemotaxis", "bacteria"], retmax=5, minyear=2020, maxyear=2021))
    main()

