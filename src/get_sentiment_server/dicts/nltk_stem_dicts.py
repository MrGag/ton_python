
import nltk
from nltk.tokenize import TreebankWordTokenizer, PunktSentenceTokenizer
from os import listdir

inp_dir = "pos/"
res_dir = "pos_stem/"
inp_dir = "neg/"
res_dir = "neg_stem/"
inp_dir = "net/"
res_dir = "net_stem/"

tokenizer = TreebankWordTokenizer()
punkt_sent_token = PunktSentenceTokenizer()
stemer = nltk.SnowballStemmer("russian")

for file_name in listdir(inp_dir):
    f = open(inp_dir + file_name, "r")
    f_str = f.read().decode("utf-8", "replace")
    f.close()
    tokeniz = tokenizer.tokenize(f_str)
    res_file = open(res_dir + file_name, "w")
    for w in tokeniz:
        res_file.write(stemer.stem(w.lower())+"\n")
    