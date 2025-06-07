import streamlit as st
import pickle
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ---------- Page Config ----------
st.set_page_config(page_title="🎵 Song Recommender", layout="wide")

# ---------- Spotify API Setup ----------
CLIENT_ID = "a4a490f3021d42539d61ddecef4c86e2"
CLIENT_SECRET = "611c34671a4e49798457e92b303830c2"


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# ---------- Hugging Face URLs ----------
df_url = "https://huggingface.co/shivi2k/Songs_recommendation/resolve/main/df1.pkl?download=true"
similarity_url = "https://huggingface.co/shivi2k/Songs_recommendation/resolve/main/similarity.pkl?download=true"

@st.cache_data(show_spinner="🎶 Loading song data...")
def load_pickle_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return pickle.loads(response.content)

# ---------- Load Data ----------
df = load_pickle_from_url(df_url)
similarity = load_pickle_from_url(similarity_url)

# ---------- Recommendation Logic ----------
def get_album_and_uri(song_name):
    try:
        result = sp.search(q=song_name, type="track", limit=1)
        if result["tracks"]["items"]:
            item = result["tracks"]["items"][0]
            image = item["album"]["images"][0]["url"]
            uri = item["uri"].split(":")[-1]  # Spotify ID
            return image, uri
    except:
        pass
    return "https://i.postimg.cc/0QNxYz4V/social.png", None

def recommend(song_name):
    index = df[df['song'] == song_name].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommendations = []
    for i in distances[1:21]:
        rec_song = df.iloc[i[0]].song
        image, uri = get_album_and_uri(rec_song)
        recommendations.append({"song": rec_song, "image": image, "uri": uri})
    return recommendations

# ---------- UI ----------
st.title("🎧 Song Recommender")
st.markdown("### 💡 Get 20 amazing song recommendations based on your favorite track!")

selected_song = st.selectbox("🎵 Choose a song", df['song'].values)

if st.button("🔍 Recommend"):
    with st.spinner("✨ Finding your perfect musical matches..."):
        recs = recommend(selected_song)

    st.subheader("🎼 Recommended Songs")
    cols = st.columns(4)  # 4 per row

    for i, rec in enumerate(recs):
        with cols[i % 4]:
            st.image(rec["image"], use_container_width=True)
            st.markdown(f"**{rec['song']}**", unsafe_allow_html=True)
            if rec["uri"]:
                embed_url = f"https://open.spotify.com/embed/track/{rec['uri']}"
                st.markdown(
                    f"""
                    <iframe src="{embed_url}" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                    """,
                    unsafe_allow_html=True
                )

st.markdown("---")
st.markdown("Made with ❤️ by Shivam Bhardwaj (SRB)", unsafe_allow_html=True)
