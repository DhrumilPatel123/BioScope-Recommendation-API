import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv('movie_data.csv')

data['original_title'] = data['original_title'].str.lower()

data_recommend = data.drop(['movie_id', 'original_title','plot'],axis=1)

data_recommend['combine'] = data_recommend[data_recommend.columns[0:2]].apply(
        lambda x: ','.join(x.dropna().astype(str)),axis=1)

count =  CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(data_recommend['combine'])

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['plot'])

combine_sparse = sp.hstack([count_matrix, tfidf_matrix], format='csr')
transform= cosine_similarity(combine_sparse, combine_sparse)

indices = pd.Series(data.index, index = data['original_title'])

def recommend(title):
        title = title.lower()
        index = indices[title]

        if title not in data['original_title'].unique():
                return 'Movie not in Database'

        else:
                sim_scores = list(enumerate(transform[index]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                sim_scores = sim_scores[1:21]

                movie_indices = [i[0] for i in sim_scores]
                movie_id = data['movie_id'].iloc[movie_indices]
                #movie_title = data['original_title'].iloc[movie_indices]
                #movie_genres = data['genres'].iloc[movie_indices]

                recommendation_data = pd.DataFrame(columns=['Movie_Id'])

                #recommendation_data = pd.DataFrame(columns=['Name', 'genre'])

                recommendation_data['Movie_Id'] = movie_id

                #recommendation_data['Name'] = movie_title
                #recommendation_data['genre'] = movie_genres

                return recommendation_data.to_dict('records')

from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
        
@app.route('/movie', methods=['GET'])
def recommend_movies():
        res = recommend(request.args.get('title'))
        return jsonify(res)

if __name__=='__main__':
        app.run(port = 5000, debug = True)

#print(recommend('Batman v Superman: Dawn of Justice'))
