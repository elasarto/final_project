import spacy
import pandas as pd
import nltk
from nltk.tokenize.toktok import ToktokTokenizer

import unicodedata
#from contractions import CONTRACTION_MAP
import re

# removing accents from text
def remove_accent(txt):
    txt = unicodedata.normalize('NFKD', txt).encode('ascii','ignore').decode('utf-8','ignore')
    return txt

# 57650 songs
df = pd.read_csv('songdata.csv')

df['text']
count = 0
for i in range(0,len(df['text'])):
    text = df['text'][count]
    text = text.replace('  \n','. ')
    text = text.replace('\n\n',' ')
    text = text.replace(' . ','')
    text = remove_accent(text)
    # print(text)
    df['text'][count] = text
    count+=1

df1 = df['text'][:15000]
df2 = df['text'][15001:30000]
df3 = df['text'][30001:45000]
df4 = df['text'][45001:]

print(len(df1))

df1.to_csv('lyrics1.txt', sep=' ', index=False)
df2.to_csv('lyrics2.txt', sep=' ', index=False)
df3.to_csv('lyrics3.txt', sep=' ', index=False)
df4.to_csv('lyrics4.txt', sep=' ', index=False)