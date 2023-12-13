# REMOVING STOPWORDS FROM COLUMN OF STRINGS
from collections import Counter

stop_words = set(stopwords.words('english'))

# Function to remove stopwords from a single string
def remove_stopwords(text):
    stopwords_dict = Counter(stop_words)
    text = ' '.join([word for word in text.split() if word not in stopwords_dict])
    return text

# Function to remove stopwords from column of string values
def remove_stopwords_column(df, col):
    return df[col].apply(lambda x: remove_stopwords(x))
