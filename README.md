# Biomedical_Q-A_BERT_Model

Question answering (QA) is a task that answers factoid
(what, when, where etc.) questions using a large collection
of documents. It aims to provide precise answers in response
to the user’s questions in natural language.

On the web, there is no single article that could provide all
the possible answers available on the internet to the question
of the problem asked by the user. Most search engines provide
top results for an open-domain question but may also provide
some biased articles which may or may not be directly relevant
to the question asked by the user. These biased articles may be
based on various criteria like advertised articles, paid articles
to come on top results, the number of times a particular site
is visited, and many more.


TRAINING
It is essentially a metric learning issue to train the encoders
such that the dot-product similarity becomes a decent ranking
function for retrieval. By learning a greater embedding function,
the purpose is to develop a vector space wherein relevant
pairings of questions and passages have a shorter distance (i.e.,
higher similarity) versus irrelevant ones.

Hard Negative
During inference, the retriever needs to identify positive (or
relevant) passages for each question from a large collection
containing millions of candidates. However, during training,
the model is learned to estimate the probabilities of positive
passages in a small candidate set for each question, due to the
limited memory of a single GPU (or other device). To reduce
such a discrepancy, we tried to design specific mechanisms
for selecting a few hard negatives from the top-k retrieved
candidates. To find the hard negatives, we sub sampled the
210K Pubmed articles randomly and ran the BM25 model to
find the hard negatives on them. BM25 gives the score how
relevant a passage is given a query. Top passage which do not
contain the answer was taken as hard negative for the given
query. 

compared different types of pre-trained language models that are able to encode questions and
contexts to high-dimensional vectors. Due to time limit, we
only indexed 4421 Pubmed abstracts. We performed MIPS to
retrieve the top 10 passages and measured the accuracy of
those 10 retrieved passages. We observed the top 10 accuracy
is 0.69 based on our test dataset.
