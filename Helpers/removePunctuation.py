# REMOVING PUNCTIATION FROM COLUMN OF STRINGS
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def remove_ punc(df, col):
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    return df[col].apply(lambda x: tokenizer.tokenize(x))


