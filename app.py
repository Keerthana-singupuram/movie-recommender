import streamlit as st
import pickle
import pandas as pd
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cinema Recommender", layout="wide")


# --- 2. THEATER BACKGROUND ---
def add_bg_from_url():
    st.markdown(
        f"""
         <style>
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop");
             background-attachment: fixed;
             background-size: cover;
         }}
         .stApp, .stMarkdown, .stText, h1, h2, h3, p {{ color: white !important; }}
         .stSelectbox > div > div {{ background-color: rgba(255, 255, 255, 0.9); color: black !important; }}
         .stButton>button {{ background-color: #e50914; color: white; border-radius: 5px; }}
         </style>
         """,
        unsafe_allow_html=True
    )


add_bg_from_url()


# --- 3. FETCH POSTER FUNCTION ---
def fetch_poster(movie_id):
    # -------------------------------------------------------
    # 1. PASTE YOUR KEY HERE
    api_key = "7372a53eef01bde87546d6e56d0ff564"
    # -------------------------------------------------------

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        # We disable SSL verification just in case your office network blocks it
        # (Note: verify=False is for testing only)
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            data = response.json()
            if 'poster_path' in data and data['poster_path']:
                return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
            else:
                return "https://via.placeholder.com/500x750?text=No+Image+On+TMDB"
        elif response.status_code == 401:
            # If you see this image, your API KEY IS WRONG
            return "https://via.placeholder.com/500x750?text=Invalid+API+Key"
        else:
            return f"https://via.placeholder.com/500x750?text=Error+{response.status_code}"

    except Exception as e:
        # If you see this, your OFFICE NETWORK is blocking Python
        print(e)
        return "https://via.placeholder.com/500x750?text=Network+Blocked"

# --- 4. RECOMMENDATION LOGIC ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters


# --- 5. MAIN APP ---
st.title('🎬 Cinema Recommender')

# Load Data
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Error: Pickle files missing. Run your VS Code script first!")
    st.stop()

# Dropdown
selected_movie_name = st.selectbox(
    'Search for a movie:',
    movies['title'].values
)

# Button
if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)


    # Function to show movie neatly
    def show(col, name, poster):
        with col:
            st.image(poster, use_container_width=True)
            st.caption(name)


    show(col1, names[0], posters[0])
    show(col2, names[1], posters[1])
    show(col3, names[2], posters[2])
    show(col4, names[3], posters[3])
    show(col5, names[4], posters[4])
