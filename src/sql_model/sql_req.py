# *-* coding:utf-8 *-*

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ton_request.db'
ton_db = SQLAlchemy(app)

class TonRequest(ton_db.Model):
    id = ton_db.Column(ton_db.Integer, primary_key=True)
    uuid = ton_db.Column(ton_db.String, index=True)
    name = ton_db.Column(ton_db.String)
    pos_percent = ton_db.Column(ton_db.Float)
    neg_percent = ton_db.Column(ton_db.Float)
    net_percent = ton_db.Column(ton_db.Float)
    count_docs = ton_db.Column(ton_db.Integer)
    date_add = ton_db.Column(ton_db.DateTime, index=True)
    complete_status = ton_db.Column(ton_db.Boolean)
    complete_percent = ton_db.Column(ton_db.Integer)
    tonObjects = ton_db.relationship("TonObj", backref="ton_request", lazy="dynamic", cascade="all, delete, delete-orphan")
    docs = ton_db.relationship("TonDocuments", backref="ton_request", lazy="dynamic", cascade="all, delete, delete-orphan") 

    def __init__(self, name, count_docs, uuid, pos_percent=0.0, neg_percent=0.0, net_percent=0.0):
        self.name = name
        self.count_docs = count_docs
        self.uuid = uuid
        self.pos_percent = pos_percent
        self.neg_percent = neg_percent
        self.net_percent = net_percent
        self.date_add = datetime.now()
        self.complete_status = False

    def __repr__(self):
        return (u"<Request {0}".formatself.name).encode("utf-8")


class TonObj(ton_db.Model):
    id = ton_db.Column(ton_db.Integer, primary_key=True)
    obj_text = ton_db.Column(ton_db.String)
    req_id = ton_db.Column(ton_db.Integer, ton_db.ForeignKey("ton_request.id"))
    
    def __init__(self, obj_text):
        self.obj_text = obj_text
    
    def __repr__(self):
        return (u"TonObj {0}".format(self.obj_text)).encode("utf-8")


class TonDocuments(ton_db.Model):
    id = ton_db.Column(ton_db.Integer, primary_key=True)
    req_id = ton_db.Column(ton_db.Integer, ton_db.ForeignKey("ton_request.id"))
    url_doc = ton_db.Column(ton_db.String)
    pos_prec = ton_db.Column(ton_db.Float)
    neg_prec = ton_db.Column(ton_db.Float)
    ton = ton_db.Column(ton_db.String, index=True) # pos, neg, net
    have_ton_obj = ton_db.Column(ton_db.Boolean, index=True)
#     net_prec = ton_db.Column(ton_db.Float)
    tonSents = ton_db.relationship("TonSentences", backref="ton_documents", lazy="dynamic", cascade="all, delete, delete-orphan")
     
    def __init__(self, url_doc, pos_prec=0., neg_prec=0., net_prec=0.):
        self.url_doc = url_doc
        self.pos_prec = pos_prec
        self.neg_prec = neg_prec
        self.net_prec = net_prec
        
    def __repr__(self):
        return (u"Documents {0}".format(self.url_doc)).encode("utf-8")
 
 
class TonSentences(ton_db.Model):
    id = ton_db.Column(ton_db.Integer, primary_key=True)
    sent_text = ton_db.Column(ton_db.String)
    pos_prob = ton_db.Column(ton_db.Float)
    neg_prob = ton_db.Column(ton_db.Float)
    id_doc = ton_db.Column(ton_db.Integer, ton_db.ForeignKey("ton_documents.id"))
     
    def __init__(self, sent_text, pos_prob, neg_prob):
        self.sent_text = sent_text
        self.pos_prob = pos_prob
        self.neg_prob = neg_prob


# Создание БД
ton_db.create_all()

# search_req = TonRequest(u"Тестовый запрос", 10, "123")
# tonObj1 = TonObj(u"Первый")
# tonObj2 = TonObj(u"Второй")
# search_req.tonObjects = [tonObj1, tonObj2]
#  
# doc1_s1 = TonSentences(u"Первое предложение документа 1", 87., 13.)
# doc1_s2 = TonSentences(u"Второе предложение документа 1", 87., 13.)
# doc2_s1 = TonSentences(u"Первое предложение документа 2", 87., 13.)
# doc2_s2 = TonSentences(u"Второе предложение документа 2", 87., 13.)
# doc1 = TonDocuments("url_doc1", 30., 20., 50.)
# doc1.tonSents = [doc1_s1, doc1_s2]
# doc2 = TonDocuments("url_doc2", 10., 10., 80.)
# doc2.tonSents = [doc2_s1, doc2_s2]
# search_req.docs = [doc1, doc2]
#  
# ton_db.session.add(search_req)
# ton_db.session.commit()
#  
# print("Выполненно")