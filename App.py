import streamlit as st
import pandas as pd
import pickle
import requests

# Function to fetch movie poster and details from TMDb API
def fetch_movie_details(id):
    """Fetch the poster URL and details for a given movie ID from TMDb."""
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "poster": f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}",
            "overview": data.get("overview", "No overview available."),
            "release_date": data.get("release_date", "N/A"),
            "rating": data.get("vote_average", "N/A"),
            "genres": ', '.join([genre['name'] for genre in data.get("genres", [])])
        }
    return {"poster": "", "overview": "", "release_date": "", "rating": "", "genres": ""}

# Recommendation function
def recommend(movie):
    if movie not in movies['title'].values:
        return f"Movie '{movie}' not found in the dataset.", []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = []
    recommended_details = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]]['id']
        movie_info = fetch_movie_details(movie_id)
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_details.append(movie_info)

    return recommended_movies, recommended_details

# Load movie data and similarity matrix
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit page configuration
st.set_page_config(page_title="Movie Recommender System", layout="wide")

# Custom CSS for enhanced UI
st.markdown(
    """
    <style>
    body {
        background-color: #121212;
        font-family: 'Arial', sans-serif;
        color: white;
    }
    .stButton > button {
        background: linear-gradient(135deg, #ff8a00, #e52e71);
        color: white;
        border-radius: 8px;
        padding: 12px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #e52e71, #ff8a00);
    }
    .movie-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .movie-card:hover {
        transform: translateY(-5px);
    }
    img {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app title
st.title('🎬 Movie Recommender System')

# Search bar for movie selection
selected_movie_name = st.selectbox(
    'Search for a Movie:',
    movies['title'].values
)

# Recommendation button and results display
if st.button('Recommend'):
    recommendations, movie_details = recommend(selected_movie_name)
    if isinstance(recommendations, str):
        st.write(recommendations)
    else:
        st.subheader(f"If you liked *{selected_movie_name}*, you might enjoy:")
        cols = st.columns(5)

        for col, title, details in zip(cols, recommendations, movie_details):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if details['poster']:
                    st.image(details['poster'], use_container_width=True)
                else:
                    st.write("No poster available")
                st.write(f"{title}")
                st.write(f"⭐ {details['rating']} | 📅 {details['release_date']}")
                st.write(f"🎭 {details['genres']}")
                st.write(f"📝 {details['overview'][:100]}...")  # Show short overview
                st.markdown('</div>', unsafe_allow_html=True)

# Display popular movies section
def fetch_popular_movies():
    url = "https://api.themoviedb.org/3/movie/popular?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])[:5]
    return []

st.subheader("🔥 Trending Now")
popular_movies = fetch_popular_movies()
cols = st.columns(5)
for col, movie in zip(cols, popular_movies):
    col.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", use_container_width=True)
    col.write(f"{movie['title']}")

# Theme switch
theme = st.selectbox("Choose Theme", ["Dark", "Light"])
if theme == "Dark":
    st.markdown('<style>body{background-color:#121212;color:white;}</style>', unsafe_allow_html=True)
else:
    st.markdown('<style>body{background-color:#ffffff;color:black;}</style>', unsafe_allow_html=True)

# Feedback system
feedback = st.radio("Did you find the recommendations useful?", ('Yes', 'No', 'Somewhat'))
if feedback:
    st.write("Thanks for your feedback!")