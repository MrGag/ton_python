# *-* coding:utf-8 *-*
import json
import nltk
from sklearn import svm
from nltk.tokenize import TreebankWordTokenizer, PunktSentenceTokenizer
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer 
import re
import os

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
# f_pos = open("dicts/pos/pos.dict", "r")
# for w in f_pos:
#     pos_dict.add(w.strip("\n").decode("utf-8"))
# f_pos.close()
# f_neg = open("dicts/neg/neg.dict", "r")
# for w in f_neg:
#     neg_dict.add(w.strip("\n").decode("utf-8"))
# f_neg.close()

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


def read_file(filename):
    sentences=[]
    with open(filename,"rU") as f:
        for raw in f:
            stroka=punkt_sent_token.sentences_from_text(raw)
            for st in stroka:
                sentences.append(st)
    return sentences

def define_obj(sent):
    #sent="@ghjlksjd Привет сегодня будем пить играть и веселиться:)"
    #tokens=[]
    
    tokens=tokenizer.tokenize(sent)
    punktua=[u".",u",",u"!",u"&",u"?",u"$",u"|",u"`",u"(",u")",u"^",u"%",u"-"]
    pos_emo=[u":)",u":-)", u")))",u"!!!"] #emoticons
    neg_emo=[u":(",u":-(", u"(((",u"!!!"] #emoticons
    res_sent=""        
    for i in range(len(tokens)):
        str=tokens[i].strip()
        if str in pos_emo:
            res_sent+=u"[pos_emo]"+u" "
        elif str in neg_emo:
            res_sent+=u"[neg_emo]"+u" "
        elif str in punktua:
            res_sent+=u"[punkt]"+u" "
        elif re.match(u"[А-я]+", str):
            wrd=stemer.stem(str)
            #wrd=wrd.decode("UTF-8")
            for k,v in dics.iteritems():
                if wrd in v:
                    res_sent+="["+k+"]"+u" "
#             if wrd in pos_dict:
#                 #positiv.append(wrd)
#                 res_sent+=u"[pos]"+u" "
#             elif wrd in neg_dict:
#                 #negativ.append(wrd)
#                 res_sent+=u"[neg]"+u" "
            else:
                res_sent+=wrd+u" "
        elif str.startswith("@"):
                res_sent+=u"[name]"+u" "
               # i=i+2                
    return res_sent

def learn_sentiment_model(file="RussianT.txt", save_f=False):
    learn_list_data=[]
    learn_list_out=[]
    neutral=[]
    with open(file,"r") as f:
        for raw in f:
            str=raw.split("\t")
            if str[0].isdigit()==True and str[1].isdigit()==True: 
                sent_in_str=punkt_sent_token.sentences_from_text(str[2])
                for sent in sent_in_str:
                    if int(str[0])==int(str[1]):
                        neutral.append(sent)
                    elif int(str[0])<int(str[1]):
                        stroka=define_obj(sent)
                        learn_list_data.append(stroka)
                        learn_list_out.append(0) #neg
                    elif int(str[0])>int(str[1]):
                        stroka=define_obj(sent)
                        learn_list_data.append(stroka)
                        learn_list_out.append(1) #pos
    print "Neutral: ", len(neutral)
    print "pos neg data for learn: ", len(learn_list_data)
    
    from sklearn.metrics import classification_report  
    
    clf=svm.SVC(kernel="linear", probability=True)
    vectorizer=CountVectorizer(ngram_range=[1,3])
    
    X_train=vectorizer.fit_transform(learn_list_data)
    y_train=learn_list_out
    clf.fit(X_train, y_train)
    
    if save_f==True:
        joblib.dump(vectorizer, "models/vector.pkl")
        joblib.dump(clf,"models/model_RussianTweet.pkl")
    
    pred=clf.predict(X_train)
    print "SVM: \n", classification_report(y_train,pred) 
    clf=0
        
#     from sklearn.naive_bayes import GaussianNB
#     gnb = GaussianNB()
#     y_pred = gnb.fit(X_train.toarray(), y_train)
#     pred_b=gnb.predict(X_train.toarray())
#     print "Gausian\n", classification_report(y_train,pred_b) 
#     gnb=0        
#learn_sentiment_model(file="RussianT.txt", save_f=True)
                                    
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
    #pred1=clf.predict_proba(vect_sent_obj)
    #print pred1
#     if pred[0]==0:
#         res["res"]="neg"
#     elif pred[0]==1:
#         res["res"]="pos"
        
        #for every sentences
#    for sent in punkt_sent_token.tokenize(inp_str.decode("utf-8", "replace")):
#         sent_obj=define_obj(sent)
#         vect_sent_obj=vectorizer.transform(sent_obj)
#         pred=clf.predict(vect_sent_obj)
#         if pred==0:
#             res["res"]="neg"
#         elif pred==1:
#             res["res"]="pos"
        
#         for token in tokenizer.tokenize(sent_obj):    
#             sent_word = token #stemer.stem(token).lower().strip()
#             if sent_word in pos_dict:
#                 res["pos_words"] += 1
#                 res["list_pos_words"].append(sent_word)
#             if sent_word in neg_dict:
#                 res["neg_words"] += 1
#                 res["list_neg_words"].append(sent_word)
#             res["list_words"].append(sent_word)
#     if res["pos_words"] - res["neg_words"]>0:
#         res["res"] = "pos"
#     elif res["pos_words"] - res["neg_words"]<0:
#         res["res"] = "neg"
#     else:
#         res["res"] = "net"
   # res["inp_str"] = inp_str
    #res["sent_obj"] = sent_obj
    return pred

def find_object(name_obj,  inp_str):
    otvet=[]
    res={}
    name_obj = name_obj.split(",")
    flag=False
    for obj in name_obj:
        for sent in punkt_sent_token.tokenize(inp_str.decode("utf-8", "replace")):
            tokens=tokenizer.tokenize(sent.lower())
            if obj.lower() in tokens:
                otvet.append(get_sentiment(sent, dics, tokenizer, punkt_sent_token, stemer))
                flag=True
            else:
                stem_tokens=[]
                for t in tokens:
                    stem_tokens.append(stemer.stem(t))
                stem_obj=stemer.stem(obj)
                if stem_obj in stem_tokens:
                    otvet.append(get_sentiment(sent, dics, tokenizer, punkt_sent_token, stemer))
                    flag=True
    if flag==False:
        res["neg"]=0
        res["pos"]=0
    else:
        pos=0
        neg=0
        for var in otvet:
            pos+=var[0][1]
            neg+=var[0][0]
        res["neg"]=neg/len(otvet)
        res["pos"]=pos/len(otvet)
      
    return res

r=find_object(u"Винни-Пух", "Хорошо живет на свете Винни-Пух счастливый мишка косолапый")

print "Хорошо живет на свете Винни-Пух счастливый мишка косолапый"
print "positive =",r["pos"]
print "negative =",r["neg"]
r=find_object(u"козел", "Пошел козел в ужасную компанию с убийцами и насильниками, идиот он был. Однажды ему повезло и, будучи счастливчиком, на козла упал кирпич")
print "Пошел козел в ужасную компанию с убийцами и насильниками, идиот он был"
print "positive =",r["pos"]
print "negative =",r["neg"]
#vvod=get_sentiment("Мама мыла раму", pos_dict, neg_dict, tokenizer, punkt_sent_token, stemer)


