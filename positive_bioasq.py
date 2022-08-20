#!/usr/bin/env python
# coding: utf-8
'''import pip
pip.main(['install','rank_bm25'])'''


import os
filename='p10.json'
pubmed_path='/project/msi290_s22cs685/DPR_Shashank_Ankan_Elli/Pubmed_Articles/JSON'
os.chdir(pubmed_path)
pubmed_files=os.listdir()
parti=int(len(pubmed_files)/10)
pubmed_files=pubmed_files[parti*9:]
os.chdir('/project/msi290_s22cs685/DPR_Shashank_Ankan_Elli/TEST/hard_negatives')
qa_path='added_hard'
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
    for file in pubmed_files:
        curr_data=readJSON(pubmed_path+'/'+file)
        for el in curr_data:
            abstract=el['articleAbstract']
            corpus.append(abstract)
    return corpus


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

def get_all_pubmed_files():
    data=[]
    for file in pubmed_files:
        curr_data=readJSON(pubmed_path+'/'+file)
        data=data+curr_data
    return data


from tqdm import tqdm
data=get_all_pubmed_files()
all_query,all_context,query_context_dic=get_all_query_and_context()
query_positive={}
for query in tqdm(all_query):
    con=query_context_dic[query]
    for context in con:
        for i in data:
            if context in i['articleAbstract']:
                query_positive[query]=i
                break


for file in qa_files:
    with open('/project/msi290_s22cs685/DPR_Shashank_Ankan_Elli/TEST/hard_negatives/'+'query_posi'+'/'+filename, 'w') as outfile:
        json.dump(query_positive, outfile)

# In[ ]:




