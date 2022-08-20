#!/usr/bin/env python
# coding: utf-8
import pip
pip.main(['install','rank_bm25'])

from numba import jit, cuda
import os
pubmed_path='/project/msi290_s22cs685/DPR_Shashank_Ankan_Elli/Pubmed_Articles/Final_Pubmed_Abstracts'
os.chdir(pubmed_path)
pubmed_files=os.listdir()
os.chdir('/project/msi290_s22cs685/DPR_Shashank_Ankan_Elli/BioASQ')
qa_path='Factoids'
os.chdir(qa_path)
qa_files=os.listdir()
os.chdir(os.pardir)

# In[181]:


import json
import numpy as np

### read file

def readJSON(path):

    f = open(path)
 
    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    # list

    # Closing file
    f.close()
    return data


def load_from_json(json_file):
	with open(json_file, 'r') as fp:
		return json.load(fp)


# In[191]:


def get_all_pubmed_corpus():
    corpus=[]
    abs_data_dic={}
    for file in pubmed_files:
        curr_data=readJSON(pubmed_path+'/'+file)
        for el in curr_data:
            abstract=el['articleAbstract']
            corpus.append(abstract)
            abs_data_dic[abstract]=el
    return corpus,abs_data_dic


def get_all_query_and_context():
    all_query=[]
    all_context=[]
    query_context_dic={}
    for file in qa_files:
        curr_data=readJSON(qa_path+'/'+file)
        for el in curr_data:
            question=el['question']
            context=[i['text'] for i in el['positive_ctxs']]
            query_context_dic[question]=context
            all_query.append(question)
            all_context.append(context)
    return all_query,all_context,query_context_dic


def is_similar(qa_context, pubmed_abstract):
    qa_context=qa_context.split(' ')
    pubmed_abstract=pubmed_abstract.split(' ')
    m=0
    l=len(qa_context)
    for token in qa_context:
        if token in pubmed_abstract:
            m+=1
    ratio=m/l
    if ratio>0.95:
        return True
    else:
        return False


def save_in_json(save_dict, save_file):
	with open(save_file, 'w') as fp:
		json.dump(save_dict, fp)
		


# In[ ]:
from rank_bm25 import BM25Okapi
from tqdm import tqdm

corpus, abs_data_dic = get_all_pubmed_corpus()
tokenized_corpus = [doc.split(" ") for doc in corpus]
all_query,all_context,query_context_dic=get_all_query_and_context()
bm25 = BM25Okapi(tokenized_corpus)
query_hard_dic={}
dic={}
for query in tqdm(all_query):
    tokenized_query = query.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)
    for i in sorted(list(doc_scores),reverse=True):
        index=list(doc_scores).index(i)
        corr_abstract=corpus[index]
        contexts=query_context_dic[query]
        l=len(contexts)
        s=0
        for context in contexts:
            if not is_similar(context,corr_abstract):
                s+=1
        if s==l:
            query_hard_dic[query]=abs_data_dic[corr_abstract]
            break
            
    for file in qa_files:
        if file not in dic.keys():
            dic[file]=readJSON(qa_path+'/'+file)
        for el in dic[file]:
            if el['question']==query:
                el['hard_negative_ctxs']=query_hard_dic[query]

for file in qa_files:
    with open('/project/msi290_s22cs685/DPR_Shashank_Ankan_Elli/TEST/hard_negatives/'+'added_hard'+'/'+'added_hard_'+file, 'w') as outfile:
        json.dump(dic[file], outfile)

# In[ ]:




