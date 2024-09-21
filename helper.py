import requests

def genreGetter(id):
    url = f"http://www.omdbapi.com/?i={id}&apikey=a0567a93"
    data = requests.get(url)
    data = data.json()
    return data['Genre'].split(', ')
