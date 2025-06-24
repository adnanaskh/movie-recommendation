import streamlit as st
import pickle
import requests
import os
import gdown



@st.cache_data
def load_similarity_from_drive():
    file_id = "1uCBowBVrB2wuXGCWBdCaj_b7-wE3Rb8G"
    url = f"https://drive.google.com/uc?id={file_id}&confirm=t"
    output = "similarity.pkl"

    # Only download if not already downloaded
    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)

    # Now safely open the pickle file
    with open(output, "rb") as f:
        return pickle.load(f)
        
# Load data
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = load_similarity_from_drive()
movies_list = movies['title'].values



# Streamlit header
st.header("🎬 Movie Recommender System")

# Dropdown to select a movie
select_value = st.selectbox("Select a movie from the dropdown", movies_list)

# OMDb API Key
OMDB_API_KEY = "22489474"

# Function to fetch full movie details
def fetch_movie_details(movie_title):
    response = requests.get(f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}")
    data = response.json()
    if data.get('Response') == 'True':
        return {
            'poster': data.get('Poster', 'https://via.placeholder.com/150?text=No+Poster'),
            'genre': data.get('Genre', 'N/A'),
            'plot': data.get('Plot', 'N/A'),
            'year': data.get('Year', 'N/A')
        }
    else:
        return {
            'poster': 'https://via.placeholder.com/150?text=No+Poster',
            'genre': 'N/A',
            'plot': 'N/A',
            'year': 'N/A'
        }

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommended_data = []
    for i in distances[1:6]:
        title = movies.iloc[i[0]].title
        details = fetch_movie_details(title)
        details['title'] = title
        recommended_data.append(details)
    return recommended_data

# Show recommendations
if st.button("Show Recommendation"):
    recommendations = recommend(select_value)
    for data in recommendations:
        st.image(data['poster'], width=150)
        st.markdown(f"### {data['title']} ({data['year']})")
        st.markdown(f"**Genre:** {data['genre']}")
        st.markdown(f"**Plot:** {data['plot']}")
        st.markdown("---")

# Credits
st.markdown("---")
st.subheader("Designed and developed by Adnan Ahmad")

# Contact Info
st.markdown("### 📬 Contact Me")
st.markdown("""
- 📧 [Email Me](mailto:your_email@example.com)
- 💼 [Connect on LinkedIn](https://www.linkedin.com/in/adnanask/)
""")



