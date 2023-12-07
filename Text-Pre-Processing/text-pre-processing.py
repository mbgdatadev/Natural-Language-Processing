# !pip install nltk
# !pip install textblob
# !pip install wordcloud


from warnings import filterwarnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GridSearchCV, cross_validate
from sklearn.preprocessing import LabelEncoder
from textblob import Word, TextBlob
from wordcloud import WordCloud

filterwarnings('ignore')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

##################################################
# 1. Text Preprocessing
##################################################

df = pd.read_csv("datasets/amazon_reviews.csv", sep=",")
df.head()

###############################
# Normalizing Case Folding
###############################

df['reviewText'] = df['reviewText'].str.lower()

###############################
# Punctuations
###############################

df['reviewText'] = df['reviewText'].str.replace('[^\w\s]', '')

# regular expression

###############################
# Numbers
###############################

df['reviewText'] = df['reviewText'].str.replace('\d', '')

###############################
# Stopwords
###############################
import nltk
# nltk.download('stopwords')

sw = stopwords.words('english')

df['reviewText'] = df['reviewText'].apply(lambda x: " ".join(x for x in str(x).split() if x not in sw))


###############################
# Rarewords
###############################

temp_df = pd.Series(' '.join(df['reviewText']).split()).value_counts()

drops = temp_df[temp_df <= 1]

df['reviewText'] = df['reviewText'].apply(lambda x: " ".join(x for x in x.split() if x not in drops))


###############################
# Tokenization
###############################

# nltk.download("punkt")

df["reviewText"].apply(lambda x: TextBlob(x).words).head()


###############################
# Lemmatization
###############################

# nltk.download('wordnet')
#  nltk.download('omw-1.4')
df['reviewText'] = df['reviewText'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))

