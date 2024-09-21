from flask import Flask, request, jsonify
import json
import random
import difflib
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load JSON data from a file
with open('movies.json') as f:
    movies_data = json.load(f)['movies']

# Helper function to get a movie by ID
def get_movie_by_id(movie_id):
    return next((movie for movie in movies_data if movie['id'] == movie_id), None)

def get_genre(movie_id):
    return next((movie['genre'] for movie in movies_data if movie['id'] == movie_id), None)

# /reccwatched - Fetches recommendations based on movies already watched and similar plots
@app.route('/reccwatched', methods=['GET'])
def recc_watched():
    param = request.args.get('param')
    if not param:
        return jsonify({'error': 'No movie IDs provided'}), 400
    
    movie_ids = [int(mid) for mid in param.split(',')]
    watched_movies = [get_movie_by_id(mid) for mid in movie_ids if get_movie_by_id(mid)]
    print(watched_movies)
    if not watched_movies:
        return jsonify({'error': 'No valid movie IDs found'}), 404

    # Example: Compare plots using difflib for similarity
    watched_plots = " ".join([str(movie['plot']) for movie in watched_movies])
    
    def plot_similarity(plot1, plot2):
        return difflib.SequenceMatcher(None, plot1, plot2).ratio()

    # Recommend movie with similar plot that hasn't been watched yet
    recommendations = []
    genres = list(set([get_genre(mid) for mid in movie_ids if get_genre(mid)]))
    for movie in movies_data:
        if movie['id'] not in movie_ids and movie['genre'] in genres:
            similarity = plot_similarity(watched_plots, movie['plot'])
            if similarity > 0.1:  # Threshold for similarity
                recommendations.append(movie)
    
    

    if recommendations:
        return jsonify({'recommended': random.choice(recommendations)})
    else:
        return jsonify({'error': 'No similar movies found'}), 404

# /reccgenre - Fetches recommendations based on genre
@app.route('/reccgenre', methods=['GET'])
def recc_genre():
    genre = request.args.get('param')
    valid_genres = [
        'action', 'adventure', 'animation', 'anime', 'comedy', 'crime',
        'documentary', 'drama', 'family', 'fantasy', 'horror', 'mystery',
        'romance', 'sci-fi', 'sport', 'thriller'
    ]
    
    if genre not in valid_genres:
        return jsonify({'error': 'Invalid genre'}), 400
    
    # Filter movies based on the genre
    genre_movies = [movie for movie in movies_data if movie['genre'] == genre]
    
    if genre_movies:
        return jsonify({'recommended': random.choice(genre_movies)})
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
    unwatched_movies = [movie for movie in movies_data if movie['id'] not in watched_ids]
    
    if unwatched_movies:
        return jsonify({'recommended': random.choice(unwatched_movies)})
    else:
        return jsonify({'error': 'No unwatched movies available'}), 404

if __name__ == '__main__':
    app.run(debug=True)
