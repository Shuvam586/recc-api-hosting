from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import random
from difflib import SequenceMatcher
import os
import glob
import json
from helper import genreGetter

app = Flask(__name__)
CORS(app)

# Load genre to sub-chunk mapping from JSON file
with open('genre_to_subchunk.json') as f:
    genre_to_subchunk = json.load(f)

# Load IMDb to chunk mapping from JSON file
with open('imdb_to_chunk.json') as f:
    imdb_to_chunk = json.load(f)

# Helper function to get a movie by ID
def get_movie_by_id(movie_id, chunk_folder):
    # chunk_folder = imdb_to_chunk.get(str(movie_id))
    if chunk_folder:
        subchunk_files = [file for file in glob.glob(os.path.join(chunk_folder, 'subchunk_*.csv'))]
        for file in subchunk_files:
            df = pd.read_csv(file)
            if movie_id in df['id'].values:
                return df.loc[df['id'] == movie_id].to_dict('records')[0]
    return None


# Helper function to get movies by genre
def get_movies_by_genre(genre, chunk_folder):
    subchunk_file = os.path.join(chunk_folder, f'subchunk_{genre.replace(" ", "_")}.csv')
    if os.path.exists(subchunk_file):
        df = pd.read_csv(subchunk_file)
        return df.to_dict('records')
    return []

# /reccwatched - Fetches recommendations based on movies already watched and similar plots
@app.route('/reccwatched', methods=['GET'])
def recc_watched():
    param = request.args.get('param')
    if not param:
        return jsonify({'error': 'No movie IDs provided'}), 400
    
    # this is list of imdb ids 
    movie_ids = [mid for mid in param.split(',')]
    filesToBeSearched = []
    for m in movie_ids:
        for g in genreGetter(m):
            filesToBeSearched.append(f'chunks/chunk{str(imdb_to_chunk[m])}/subchunk_{g}.csv')

    # print(filesToBeSearched)



    
    # watched_movies = []
    # for chunk_folder in glob.glob('chunk*'):
    #     for movie_id in movie_ids:
    #         movie = get_movie_by_id(movie_id, chunk_folder)
    #         if movie:
    #             watched_movies.append(movie)

    def calculate_similarity(plot1, plot2):
        return SequenceMatcher(None, plot1, plot2).ratio()

    # def find_most_similar_movie(imdb_id):
    # Get the plot of the given movie
    inwhy = 0
    lOfFiles = []
    for ftbs in filesToBeSearched:
        try:
            lOfFiles.append(pd.read_csv(ftbs))
        except:
            pass
    # while True:
    #     try:
    #         df = pd.read_csv(filesToBeSearched[inwhy])
    #         break
    #     except:
    #         inwhy+=1

    df = pd.concat(lOfFiles)

    
    given_plot = df[df['imdb_id'] == (movie_ids[0])]['overview'].values[0]
    
    # Initialize variables to store the maximum similarity ratio and the corresponding movie ID
    max_similarity = 0
    max_similarity_movie_id = None
    
    # Iterate over the entire dataframe
    for index, row in df.iterrows():
        # Skip the row if it's the same as the given movie
        if row['imdb_id'] == movie_ids[0]:
            continue
        
        # Extract the plot of the current movie
        plot = row['overview']
        
        # print(plot, index, sep='\n')

        # if len(plot)>0:
        #     # Calculate the similarity ratio between the given plot and the current plot
        similarity = calculate_similarity(str(given_plot), str(plot))
        # else: similarity = 0
        # Update the maximum similarity ratio and the corresponding movie ID if necessary
        if similarity > max_similarity:
            max_similarity = similarity
            max_similarity_movie_id = row['imdb_id']
    
    
    # if recommendations:
    return jsonify({'recommended': max_similarity_movie_id})
    # else:
    #     return jsonify({'error': 'No similar movies found'}), 404

# /reccgenre - Fetches recommendations based on genre
@app.route('/reccgenre', methods=['GET'])
def recc_genre():
    genre = request.args.get('param')
    valid_genres = list(genre_to_subchunk.keys())
    
    if genre not in valid_genres:
        return jsonify({'error': 'Invalid genre'}), 400
    
    # Get movies by genre
    movies = []
    for chunk_folder in glob.glob('chunk*'):
        movies.extend(get_movies_by_genre(genre, chunk_folder))
    
    if movies:
        return jsonify({'recommended': random.choice(movies)})
    else:
        return jsonify({'error': f'No movies found in genre: {genre}'}), 404

# /reccrandom - Randomly recommends a movie or TV show that hasn't been watched
@app.route('/reccrandom', methods=['GET'])
def recc_random():
    media_type = request.args.get('type')
    valid_types = ['tvshow', 'movie']
    
    if media_type not in valid_types:
        return jsonify({'error': 'Invalid type, choose "tvshow" or "movie"'}), 400
    
    watched_param = request.args.get('watched', '')
    watched_ids = [int(mid) for mid in watched_param.split(',')] if watched_param else []
    
    # Recommend a random unwatched movie
    unwatched_movies = []
    for chunk_folder in glob.glob('chunk*'):
        for file in glob.glob(os.path.join(chunk_folder, 'subchunk_*.csv')):
            df = pd.read_csv(file)
            unwatched_movies.extend(df.loc[~df['id'].isin(watched_ids)].to_dict('records'))
    
    if unwatched_movies:
        return jsonify({'recommended': random.choice(unwatched_movies)})
    else:
        return jsonify({'error': 'No unwatched movies available'}), 404

if __name__ == '__main__':
    app.run(debug=True)