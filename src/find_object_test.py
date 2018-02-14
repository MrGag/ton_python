#! *-* coding: utf-8 *-*

import json, os, re
import nltk
from nltk.tokenize import TreebankWordTokenizer, PunktSentenceTokenizer
from sklearn.externals import joblib
#from flask import Flask, request, render_template
#from sql_model.sql_req import TonDocuments, TonObj, TonRequest, TonSentences, ton_db

#app = Flask(__name__)

# Начальные устоновки
pos_dict = set()
neg_dict = set()
tokenizer = TreebankWordTokenizer()
punkt_sent_token = PunktSentenceTokenizer()
stemer = nltk.SnowballStemmer("russian")

inp_str = u"сегодня правительством ирана было объявлено о подавлении митингов благодаря напалму"
name_obj=u'правительство ирана'

#def find_object(name_obj,  inp_str, inp_doc_id):
otvet=[]
res={}
flag=False
name_obj = name_obj.split(",")
#ton_doc = TonDocuments.query.get(inp_doc_id)
ton_sents_list = []

for obj in name_obj:
    for sent in punkt_sent_token.tokenize(inp_str):
        tokens=tokenizer.tokenize(sent.lower())
        if obj in sent.lower():
            flag=True
        #if obj.lower().strip().encode("utf-8") in tokens:  #for sistem
        # if obj.lower().strip() in tokens:
        #     #sentiment_val = get_sentiment(sent, dics, tokenizer, punkt_sent_token, stemer)
        #     #otvet.append(sentiment_val)
        #     #ton_sents_list.append(TonSentences(sent.decode("utf-8"), sentiment_val[0][1], sentiment_val[0][0]))
        #     flag=True
        else:
            stem_tokens=[]
            for t in tokens:
                # stem_tokens.append(stemer.stem(t.decode("utf-8"))) #for sistem
                stem_tokens.append(stemer.stem(t))
            stem_obj=stemer.stem(obj.strip())
            if stem_obj in ' '.join(stem_tokens):
                flag=True
            # if stem_obj in stem_tokens:
            #     #sentiment_val = get_sentiment(sent, dics, tokenizer, punkt_sent_token, stemer)
            #     #otvet.append(sentiment_val)
            #     #ton_sents_list.append(TonSentences(sent.decode("utf-8"), sentiment_val[0][1], sentiment_val[0][0]))
            #     flag=True
if flag==False:
    res["neg"]=0.
    res["pos"]=0.
    #ton_doc.have_ton_obj = False
else:
    pos=0.
    neg=0.
    for var in otvet:
        pos+=var[0][1]
        neg+=var[0][0]
    res["neg"]=neg/len(otvet)
    res["pos"]=pos/len(otvet)
    # ton_doc.have_ton_obj = True
    # if pos>neg:
    #     ton_doc.ton = "pos"
    # elif pos<neg:
    #     ton_doc.ton = "neg"
    # else:
    #     ton_doc.ton = "net"

    # ton_doc.tonSents = ton_sents_list
    # ton_db.session.add(ton_doc)
    # ton_db.session.commit()
    # return res