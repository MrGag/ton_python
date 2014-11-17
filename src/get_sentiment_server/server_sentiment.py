# *-* coding:utf-8 *-*
# Сервер определения тоанльности

import json, os, re
import nltk
from nltk.tokenize import TreebankWordTokenizer, PunktSentenceTokenizer
from sklearn.externals import joblib
from flask import Flask, request, render_template
from src.sql_model.sql_req import TonDocuments, TonObj, TonRequest, TonSentences, ton_db

app = Flask(__name__)

# Начальные устоновки
pos_dict = set()
neg_dict = set()
tokenizer = TreebankWordTokenizer()
punkt_sent_token = PunktSentenceTokenizer()
stemer = nltk.SnowballStemmer("russian")

#load models and vector
vectorizer = joblib.load("models/vector.pkl")
clf=joblib.load("models/model_RussianTweet.pkl")

# Заполняем словари
def load_ext_dics(dir): # load 37 types of emotions
    dics={}
    for files in os.listdir(dir):
        with open(dir+"/"+files,"r") as f1:
            ls=[]
            for raw in f1:
                s=raw.strip()
                ls.append(s.decode("UTF-8"))
            dics[files]=ls
            ls=0
    return dics
dics=load_ext_dics("dicts/emodic")

def define_obj(sent):
    #sent="@ghjlksjd Привет сегодня будем пить играть и веселиться:)"
    
    tokens=tokenizer.tokenize(sent)
    punktua=[u".",u",",u"!",u"&",u"?",u"$",u"|",u"`",u"(",u")",u"^",u"%",u"-"]
    pos_emo=[u":)",u":-)", u")))",u"!!!"] #emoticons
    neg_emo=[u":(",u":-(", u"(((",u"!!!"] #emoticons
    res_sent=u""        
    for i in range(len(tokens)):
        str=tokens[i].strip().decode("utf-8")
        if str in pos_emo:
            res_sent+=u"[pos_emo]"+u" "
        elif str in neg_emo:
            res_sent+=u"[neg_emo]"+u" "
        elif str in punktua:
            res_sent+=u"[punkt]"+u" "
        elif re.match(u"[А-я]+", str):
            wrd=stemer.stem(str)
            for k,v in dics.iteritems():
                if wrd in v:
                    res_sent+="["+k+"]"+u" "
            else:
                res_sent+=wrd+u" "
        elif str.startswith("@"):
                res_sent+=u"[name]"+u" "
               # i=i+2                
    return res_sent

def get_sentiment(inp_str, dics, tokenizer, punkt_sent_token, stemer):
    # Определение тональности на основе словарей
    res = {"res":"",
           "pos_words":0, "list_pos_words":[],
           "neg_words":0, "list_neg_words":[],
           "list_words":[],
           "inp_str":""
           }
    sent_obj=define_obj(inp_str)
    vect_sent_obj=vectorizer.transform([sent_obj])
    pred = clf.predict_proba(vect_sent_obj)
    # Если разница между позитивной оценкой и негативной меньше 5% то предложение нейтрально
    if abs(pred[0][0] - pred[0][1])<0.05:
        pred[0] = [0.5, 0.5]
    return pred

def find_object(name_obj,  inp_str, inp_doc_id):
    otvet=[]
    res={}
    flag=False
    name_obj = name_obj.split(",")
    ton_doc = TonDocuments.query.get(inp_doc_id)
    ton_sents_list = []
    for obj in name_obj:
        for sent in punkt_sent_token.tokenize(inp_str):
            tokens=tokenizer.tokenize(sent.lower())
            if obj.lower().strip().encode("utf-8") in tokens:
                sentiment_val = get_sentiment(sent, dics, tokenizer, punkt_sent_token, stemer)
                otvet.append(sentiment_val)
                ton_sents_list.append(TonSentences(sent.decode("utf-8"), sentiment_val[0][1], sentiment_val[0][0]))
                flag=True
            else:
                stem_tokens=[]
                for t in tokens:
                    stem_tokens.append(stemer.stem(t.decode("utf-8")))
                stem_obj=stemer.stem(obj.strip())
                if stem_obj in stem_tokens:
                    sentiment_val = get_sentiment(sent, dics, tokenizer, punkt_sent_token, stemer)
                    otvet.append(sentiment_val)
                    ton_sents_list.append(TonSentences(sent.decode("utf-8"), sentiment_val[0][1], sentiment_val[0][0]))
                    flag=True
    if flag==False:
        res["neg"]=0.
        res["pos"]=0.
        ton_doc.have_ton_obj = False
    else:
        pos=0.
        neg=0.
        for var in otvet:
            pos+=var[0][1]
            neg+=var[0][0]
        res["neg"]=neg/len(otvet)
        res["pos"]=pos/len(otvet)
        ton_doc.have_ton_obj = True
        if pos>neg:
            ton_doc.ton = "pos"
        elif pos<neg:
            ton_doc.ton = "neg"
        else:
            ton_doc.ton = "net"

    ton_doc.tonSents = ton_sents_list
    ton_db.session.add(ton_doc)
    ton_db.session.commit()      
    return res

@app.route("/", methods=["GET"])
def sentiment_get():
    return render_template("sentiment_html_form.html")

@app.route("/", methods=["POST"])
def sentiment_post():
    inp_json = json.loads(request.data)
    inp_text = inp_json["text"].encode("utf-8", "replace")
    inp_doc_id = int(inp_json["doc_id"])
    #
    # *** Новый папраметр "Объект тональности" ***
    #
    f_names=inp_json["ton_name"]
    #
    # ********************************************
    #
    res_obj = find_object(f_names, inp_text, inp_doc_id)
    if res_obj["pos"]>res_obj["neg"]:
        res_txt = "pos"
    elif res_obj["pos"]<res_obj["neg"]:
        res_txt = "neg"
    elif res_obj["pos"] == res_obj["neg"] and res_obj["pos"]>0 and res_obj["neg"]>0:
        res_txt = "net"
    else:
        res_txt = "no_ton_obj"
    res = {"res":res_txt, "pos":res_obj["pos"], "neg":res_obj["neg"]}
    return json.dumps(res)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)