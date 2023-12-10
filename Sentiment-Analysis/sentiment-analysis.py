
##################################################
# 3. Sentiment Analysis
##################################################

df["reviewText"].head()

# nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()
sia.polarity_scores("The film was awesome")


sia.polarity_scores("I liked this music but it is not good as the other one")


df["reviewText"][0:10].apply(lambda x: sia.polarity_scores(x))

df["reviewText"][0:10].apply(lambda x: sia.polarity_scores(x)["compound"])

df["polarity_score"] = df["reviewText"].apply(lambda x: sia.polarity_scores(x)["compound"])





