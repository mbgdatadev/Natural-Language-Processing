
##################################################
# Sentiment Analysis and Sentiment Modeling for Amazon Reviews
##################################################

# 1. Text Preprocessing
# 2. Text Visualization
# 3. Sentiment Analysis
# 4. Feature Engineering
# 5. Sentiment Modeling

# !pip install nltk
# !pip install textblob
# !pip install wordcloud

import numpy as np
import pandas as pd
import nltk
import matplotlib
from sklearn.metrics import classification_report

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from warnings import filterwarnings
from PIL import Image
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GridSearchCV, cross_validate, train_test_split
from sklearn.preprocessing import LabelEncoder
from textblob import Word, TextBlob
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer



filterwarnings('ignore')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

##################################################
# 1. Text Preprocessing
##################################################

df = pd.read_excel("datasets/amazon.xlsx")
df.head()
df2=df.copy()
###############################
# Normalizing Case Folding
###############################

df['Review'] = df['Review'].str.lower()
df['Review'].head()

###############################
# Punctuations
###############################

df['Review'] = df['Review'].str.replace(r'[^\w\s]|<br\s?\/?>', '', regex=True)

df['Review'].head()

###############################
# Numbers
###############################

df['Review'] = df['Review'].str.replace('\d', '')
df['Review'].head()

###############################
# Stopwords
###############################

# nltk.download('stopwords')

sw = stopwords.words('english')

df['Review'] = df['Review'].apply(lambda x: " ".join(x for x in str(x).split() if x not in sw))
df['Review'].head()

###############################
# Rarewords
###############################



#temp_df = pd.Series(' '.join(df['Review']).split()).value_counts()
#drops = temp_df[temp_df < 1000]
#df['Review'] = df['Review'].apply(lambda x: " ".join(x for x in x.split() if x  in drops))
#df['Review'].count()


 drops = pd.Series(' '.join(df['Review']).split()).value_counts()[-1000:]
 df['Review'] = df['Review'].apply(lambda x: " ".join(x for x in x.split() if x not in drops))

###############################
# Lemmatization
###############################

# nltk.download('wordnet')
#  nltk.download('omw-1.4')
df['Review'] = df['Review'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
df['Review'].head()


##################################################
# 2. Text Visualization
##################################################


###############################
# Terim Frekanslarının Hesaplanması
###############################

tf = df["Review"].apply(lambda x: pd.value_counts(x.split(" "))).sum(axis=0).reset_index()

tf.columns = ["words", "tf"]

tf.sort_values("tf", ascending=False)

###############################
# Barplot
###############################

tf[tf["tf"] > 500].plot.bar(x="words", y="tf")
plt.show()

###############################
# Wordcloud
###############################

text = " ".join(i for i in df.Review)

wordcloud = WordCloud().generate(text)
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()


wordcloud = WordCloud(max_font_size=50,
                      max_words=100,
                      background_color="white").generate(text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

wordcloud.to_file("wordcloud.png")
###############################
# Şablonlara Göre Wordcloud
###############################

tr_mask = np.array(Image.open("tr.png"))

wc = WordCloud(background_color="white",
               max_words=1000,
               mask=tr_mask,
               contour_width=3,
               contour_color="firebrick")

wc.generate(text)
plt.figure(figsize=[10, 10])
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()


##################################################
# 3. Sentiment Analysis
##################################################

df["Review"].head()

# nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

df["Review"][0:10].apply(lambda x: sia.polarity_scores(x))

df["Review"][0:10].apply(lambda x: sia.polarity_scores(x)["compound"])

df["polarity_score"] = df["Review"].apply(lambda x: sia.polarity_scores(x)["compound"])

df[["Star","polarity_score"]].head()

###############################
# 4. Feature Engineering
###############################
df.head()

df["Review"][0:10].apply(lambda x: "pos" if sia.polarity_scores(x)["compound"] > 0 else "neg")

df["sentiment_label"] = df["Review"].apply(lambda x: "pos" if sia.polarity_scores(x)["compound"] > 0 else "neg")

df["sentiment_label"].value_counts()

df.groupby("sentiment_label")["Star"].mean()

df["sentiment_label"] = LabelEncoder().fit_transform(df["sentiment_label"])


###############################
# 5. Sentiment Modeling
###############################
train_x, test_x, train_y, test_y = train_test_split(df["Review"],
                                                    df["sentiment_label"],
                                                    random_state=42)


# TF-IDF Word Level
tf_idf_word_vectorizer = TfidfVectorizer().fit(train_x)
x_train_tf_idf_word = tf_idf_word_vectorizer.transform(train_x)
x_test_tf_idf_word = tf_idf_word_vectorizer.transform(test_x)


# Lojistik Regresyon

log_model = LogisticRegression().fit(x_train_tf_idf_word, train_y)

y_pred = log_model.predict(x_test_tf_idf_word)

print(classification_report(y_pred, test_y))

cross_val_score(log_model, x_test_tf_idf_word, test_y, cv=5).mean()

# Veride bulunan yorumlardan ratgele seçerek modele sorulması.

random_review = pd.Series(df["Review"].sample(1).values)
new_review = CountVectorizer().fit(train_x).transform(random_review)
pred = log_model.predict(new_review)
print(f'Review:  {random_review[0]} \n Prediction: {pred}')

# Random Forest Classifier
rf_model = RandomForestClassifier().fit(x_train_tf_idf_word, train_y)

y_pred = rf_model.predict(x_test_tf_idf_word)

print(classification_report(y_pred, test_y))

cross_val_score(rf_model, x_test_tf_idf_word, test_y, cv=5, n_jobs=-1).mean()

# Naive Bayes (MultinomialNB)
from sklearn.naive_bayes import MultinomialNB

# Model oluşturma ve eğitme
nb_model = MultinomialNB().fit(x_train_tf_idf_word, train_y)

# Tahmin yapma
nb_predictions = nb_model.predict(x_test_tf_idf_word)

# Performans ölçümü (örneğin, sınıflandırma raporu)
from sklearn.metrics import classification_report
print(classification_report(test_y, nb_predictions))
cross_val_score(nb_model, x_test_tf_idf_word, test_y, cv=5, n_jobs=-1).mean()

# Destek Vektör Makineleri (SVM)
from sklearn.svm import SVC

# Model oluşturma ve eğitme
svm_model = SVC().fit(x_train_tf_idf_word, train_y)

# Tahmin yapma
svm_predictions = svm_model.predict(x_test_tf_idf_word)

# Performans ölçümü (örneğin, sınıflandırma raporu)
from sklearn.metrics import classification_report
print(classification_report(test_y, svm_predictions))

cross_val_score(svm_model, x_test_tf_idf_word, test_y, cv=5, n_jobs=-1).mean()


