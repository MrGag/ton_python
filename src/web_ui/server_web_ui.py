# *-* coding:utf-8 *-*
# Сервер для работы Вебинтерфейса

import json
from flask import Flask, request, render_template, redirect
import datetime
from os import listdir
import uuid
import subprocess
from sql_model.sql_req import TonDocuments, TonObj, TonRequest, TonSentences, ton_db

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def list_requests_form():
    if request.method == "POST":
        """ Запускает на обработку новый запрос, возвращает уникальный идентификатор нового запроса """
        request_uuid = str(uuid.uuid4()).decode("utf-8")
        list_requests = request.files["request_file"].readlines()
        request_name = list_requests[0]
        files_list = list_requests[1:]
        ton_req = TonRequest(request_name.decode("utf-8"), len(files_list), request_uuid)
        ton_doc_list = []
        for doc in files_list:
            ton_doc_list.append(TonDocuments(url_doc=doc.decode("utf-8")))
        ton_req.docs = ton_doc_list
        ton_obj_list = []
        for text_tonobj in request.form["ton_name"].split(","):
            ton_obj_list.append(TonObj(text_tonobj.encode("utf-8").strip().decode("utf-8")))
        ton_req.tonObjects = ton_obj_list
        ton_db.session.add(ton_req)
        ton_db.session.commit()
        subprocess.Popen(["python", "../requests_processing/process_new_request.py", str(ton_req.id)])
        return redirect("/")
    else:
        """Отображает список всех поисковых запросов"""
        def get_ton(pos, neg, net):
            ton = ""
            if pos>neg and pos>net:
                ton = "pos"
            elif neg>pos and neg>net:
                ton = "neg"
            else:
                ton = "net"
            
            return ton
        
        list_requests = []
        for i, ton_req in enumerate(TonRequest.query.order_by(TonRequest.date_add.desc()).all(), 1):
            if ton_req.complete_status:
                status = u"complete"
            else:
                status = u"process"
            list_requests.append({"status": status,
                                  "name": ton_req.name,
                                  "ton_name": u", ".join(x.obj_text for x in ton_req.tonObjects),
                                  "neg": "{:.0f}".format(ton_req.neg_percent),
                                  "pos": "{:.0f}".format(ton_req.pos_percent),
                                  "net": "{:.0f}".format(ton_req.net_percent),
                                  "date": ton_req.date_add.strftime("%d.%m.%Y %H:%M"),
                                  "uuid": ton_req.uuid,
                                  "ton": get_ton(ton_req.pos_percent, ton_req.neg_percent, ton_req.net_percent),
                                  "complete_percent": ton_req.complete_percent,
                                  "id_req": ton_req.id,
                                  "i": int(i)
                                  })
        return render_template("list_requests.html", requests=list_requests )


@app.route("/upload/", methods=["GET", "POST"])
def upload_new_request():
    """ Запускает на обработку новый запрос, возвращает уникальный идентификатор нового запроса """
    if request.method == "POST":
        request_uuid = str(uuid.uuid4()).decode("utf-8")
        list_requests = request.files["request_file"].readlines()
        request_name = list_requests[0]
        files_list = list_requests[1:]
        ton_req = TonRequest(request_name.decode("utf-8"), len(files_list), request_uuid)
        ton_doc_list = []
        for doc in files_list:
            ton_doc_list.append(TonDocuments(url_doc=doc.decode("utf-8")))
        ton_req.docs = ton_doc_list
        ton_obj_list = []
        for text_tonobj in request.form["ton_name"].split(","):
            ton_obj_list.append(TonObj(text_tonobj.encode("utf-8").strip().decode("utf-8")))
        ton_req.tonObjects = ton_obj_list
        ton_db.session.add(ton_req)
        ton_db.session.commit()
        subprocess.Popen(["python", "../requests_processing/process_new_request.py", str(ton_req.id)])
        return render_template("upload_form.html", upload_req=True, req_uuid=request_uuid)
    elif request.method == "GET":
        return render_template("upload_form.html", upload_req=False)


@app.route("/details", methods=["GET", "POST"])
def details_request():
    def get_ton(pos, neg):
        ton = ""
        if pos>neg:
            ton = "pos"
        elif pos<neg:
            ton = "neg"
        elif pos==neg:
            ton = "net"
        return ton
    
    ton_req = TonRequest.query.get(int(request.args.get("id_req")))
    id_req = request.args.get("id_req")
    type_ton_docs = request.args.get("docs_ton_type") # all, pos, neg, net, all_with_ton_obj, all_without_ton_obj
    if type_ton_docs is None:
        # type_ton_docs = u"None"
        type_ton_docs = u"all"
    
    count_pos_docs = ton_req.docs.filter(TonDocuments.ton == "pos" and TonDocuments.have_ton_obj == True).count()
    count_neg_docs = ton_req.docs.filter(TonDocuments.ton == "neg" and TonDocuments.have_ton_obj == True).count()
    count_net_docs = ton_req.docs.filter(TonDocuments.ton == "net" and TonDocuments.have_ton_obj == True).count()
    
    # Общие данные о запросе
    ton_req_data = {"name": ton_req.name,
                    "tonObjects": u", ".join(x.obj_text for x in ton_req.tonObjects),
                    "neg": ton_req.neg_percent,
                    "pos": ton_req.pos_percent,
                    "net": ton_req.net_percent,
                    "count_pos": count_pos_docs,
                    "count_neg": count_neg_docs,
                    "count_net": count_net_docs,
                    "date": ton_req.date_add.strftime("%d.%m.%Y %H:%M"),
                    "count_docs": ton_req.count_docs,
                    "docs_with_ton_obj": ton_req.docs.filter(TonDocuments.have_ton_obj == True).count(),
                    "docs_without_ton_obj": ton_req.docs.filter(TonDocuments.have_ton_obj != True).count(),
                    }
    
    
    res_docs = []
    if type_ton_docs == "all":
        # Все документы
        res_docs = ton_req.docs.all()
    elif type_ton_docs == "pos":
        # Позитивные документы
        res_docs = ton_req.docs.filter(TonDocuments.ton == "pos" and TonDocuments.have_ton_obj == True).all()
    elif type_ton_docs == "neg":
        # Негативные документы
        res_docs = ton_req.docs.filter(TonDocuments.ton == "neg" and TonDocuments.have_ton_obj == True).all()
    elif type_ton_docs == "net":
        # Нейтральные документы
        res_docs = ton_req.docs.filter(TonDocuments.ton == "net" and TonDocuments.have_ton_obj == True).all()
    elif type_ton_docs == "all_with_ton_obj":
        # Все документы с объектом тональности
        res_docs = ton_req.docs.filter(TonDocuments.have_ton_obj == True).all()
    elif type_ton_docs == "all_without_ton_obj":
        # Документы без объекта тональности
        res_docs = ton_req.docs.filter(TonDocuments.have_ton_obj == False).all()            
    
    list_res_docs = []
    for i, doc in enumerate(res_docs, 1):
        list_res_docs.append({"url":doc.url_doc,
                              "name": doc.url_doc.split("/")[-1],
                              "ton": get_ton(doc.pos_prec, doc.neg_prec),
                              "i": int(i),
                              "ton_sents":({"text":x.sent_text,
                                            "pos":int(x.pos_prob*100),
                                            "neg":int(x.neg_prob*100),
                                            "sent_ton": get_ton(x.pos_prob, x.neg_prob)
                                            } for x in doc.tonSents)})

    list_res_source = []
    for i, doc in enumerate(res_docs, 1):
        list_res_source.append({"url": doc.url_doc,
                                "name": u"Источник " + str(i),
                                "pos_docs": 10,
                                "neg_docs": 5,
                                "net_docs": 1,
                                "i": int(i),
                                "gos": True,
                                "popularity": 5,
                                "in_database": True,
                                })
        
    pyLegendTemplate = "<ul class=\\\"<%=name.toLowerCase()%>-legend\\\"><% for (var i=0; i<segments.length; i++){%><li><span class=\\\"badge\\\" style=\\\"background-color:<%=segments[i].fillColor%>\\\"><%if(segments[i].label){%><%=segments[i].label%><%}%></span></li><%}%></ul>"
    return render_template("request_details.html",
                           ton_request=ton_req_data,
                           list_docs=list_res_docs,
                           list_source=list_res_source,
                           type_ton_docs=type_ton_docs,
                           id_req=id_req,
                           pyLegendTemplate=pyLegendTemplate)


@app.route("/save_source", methods=["POST"])
def save_source():
    if request.method == "POST":
        print "save post"
        print request.form['source']
        print request.form['gos']
        print request.form['popularity']
        return json.dumps({'success': True}), 200, {'ContentType':'application/json'} 
    # else:
    #     return False


@app.route("/add_source", methods=["POST"])
def add_source():
    if request.method == "POST":
        print "add post"
        print request.form['source']
        print request.form['gos']
        print request.form['popularity']
        return json.dumps({'success': True}), 200, {'ContentType':'application/json'} 
    # else:
    #     return False


@app.route("/delete_request", methods=["GET"])
def delete_request():
    id_req = int(request.args.get("id_req"))
    ton_req = TonRequest.query.get(id_req)
    ton_db.session.delete(ton_req)
    ton_db.session.commit()
    return True


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)