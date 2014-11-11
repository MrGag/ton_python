# *-* coding:utf-8 *-*
# Обработка нового файла с запросом

import json
import xml.etree.cElementTree as et
import requests
import sys
import time
from src.sql_model.sql_req import TonDocuments, TonObj, TonRequest, TonSentences, ton_db


def process_request(request_id):  
    ton_req = TonRequest.query.get(request_id)
#     request_name = ton_req.name
    ton_name = u",".join(x.obj_text for x in ton_req.tonObjects)
    count_docs = ton_req.count_docs
    doc_percent = 100.0/float(count_docs)
    complete_percent = 0.0
    status_update_percent = 5
    
#     count_pass = ton_req.docs.count()
    count_pos, count_neg, count_net = 0, 0, 0
    
    url = "http://127.0.0.1:5000"
    for passport in ton_req.docs:
        try:
            passport_file_name = passport.url_doc
            r_pass = requests.request("GET", passport_file_name.strip())
            r_pass.encoding = "utf-8"
            xml_root = et.fromstring(r_pass.text.encode("utf-8"))
            pass_text = xml_root.find("resultData/text").text.strip()
            data_json = {"text":pass_text, "ton_name":ton_name, "doc_id":passport.id}
            r = requests.post(url, data=json.dumps(data_json), headers={'content-type': 'text/plain'})
            req_from_ton_server = json.loads(r.text)
            r_res = req_from_ton_server["res"]
            passport.pos_prec = req_from_ton_server["pos"]
            passport.neg_prec = req_from_ton_server["neg"]
            ton_db.session.add(passport)
            ton_db.session.commit()
            if r_res == "pos":
                count_pos += 1
            elif r_res == "neg":
                count_neg += 1
            elif r_res == "net":
                count_net += 1
            complete_percent += doc_percent
            
            # Обновляем % прогресса обработки
            if int(complete_percent) % status_update_percent == 0:
                ton_req.complete_percent = int(complete_percent)
                ton_db.session.add(ton_req)
                ton_db.session.commit()
        except KeyboardInterrupt:
            exit()
        except:
            print("Error in file: {0}".format(passport_file_name.strip()))
    
    # Сохраняем результат
    count_ton_docs = ton_req.docs.filter(TonDocuments.have_ton_obj == True).count()
    ton_req.pos_percent = float(count_pos)/float(count_ton_docs)*100
    ton_req.neg_percent = float(count_neg)/float(count_ton_docs)*100
    ton_req.net_percent = float(count_net)/float(count_ton_docs)*100
    ton_req.complete_status = True
    ton_req.complete_percent = 100
    ton_db.session.add(ton_req)
    ton_db.session.commit()
    return ton_req.uuid

if __name__=="__main__":
    request_id = int(sys.argv[1])
    process_request(request_id)