import pickle
import pandas as pd
import streamlit as st
from recommender import hybrid_recommend

st.set_page_config(page_title="Music Recommendation System")

songs_dict = pickle.load(open('pickles/data.pkl', 'rb'))
songs = pd.DataFrame(songs_dict)

# Sidebar

option1 = 'Chart-Toppers (Popular)'
option2 = 'Undiscovered Gems (Less Popular)'
mode = st.sidebar.selectbox('Your mode of recommendations', (option1, option2))
if mode == option1:
    prioritisePopular = True
else:
    prioritisePopular = False

# Slider

num_songs = st.sidebar.slider("Number of Songs to Recommend", 1, 10, 5)

# Lyrics
def format_lyrics(lyrics):
    # Add line breaks at appropriate places in the lyrics
    formatted_lyrics = lyrics.replace('\n', '<br/>')
    return formatted_lyrics

# Mood Based Recommendation
st.sidebar.markdown("---")
st.sidebar.subheader("Mood-based Recommendation")
enable_mood_filtering = st.sidebar.checkbox("Enable Mood Filtering")
if enable_mood_filtering:
    if 'current_recommendations' not in st.session_state:
        st.session_state.current_recommendations = None

    song_moods = songs['predicted_mood_rf'].unique()
    song_moods = [mood.title() for mood in song_moods]
    selected_mood = st.sidebar.selectbox('Moods', song_moods)

    change_recommendations = st.button("Change Recommendations", key="change_recommendations")
    if change_recommendations:
        st.session_state.current_recommendations = songs[
            songs['predicted_mood_rf'].str.title() == selected_mood].sample(n=num_songs)

    if st.session_state.current_recommendations is None:
        st.session_state.current_recommendations = songs[
            songs['predicted_mood_rf'].str.title() == selected_mood].sample(n=num_songs)

    # Display recommended songs with adjacent "Show Lyrics" buttons and Spotify links
    st.title('Recommended Songs:')
    st.subheader(f"Selected Mood - {selected_mood}")

    for i in range(num_songs):
        song_info = st.session_state.current_recommendations.iloc[i]
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            st.write(f"**{i + 1}**")
        with col2:
            track_id = song_info['track_id']
            spotify_track_url = f"https://open.spotify.com/track/{track_id}"
            st.markdown(f"Track: [{song_info['track_name']}]({spotify_track_url})", unsafe_allow_html=True)
            st.write(f"**Artist:** {song_info['track_artist']}")
        with col3:
            # Button to show lyrics
            show_lyrics = st.button(f"Lyrics - {i + 1}")

        if show_lyrics:
            formatted_lyrics = format_lyrics(song_info['lyrics'])
            st.markdown(f"**Lyrics:**<br/>{formatted_lyrics}", unsafe_allow_html=True)

#Content Based Recommendation

else:
    # Search bar for artist/track
    st.sidebar.markdown("---")
    st.sidebar.subheader("Content-based Recommendation")
    search_query = st.text_input("Search for a track")
    if search_query:
        search_results = songs[songs['track_name'].str.contains(search_query, case=False)]
        if not search_results.empty:
            st.session_state.current_song_index = search_results.index[0]
        else:
            st.warning("No matching song found.")

    #Getting and displaying the recommendations
    if 'current_song_index' in st.session_state:
        recommendations = hybrid_recommend(st.session_state.current_song_index, num_songs,
                                           prioritisePopular=prioritisePopular)
        for recommendation_type, recommended_songs in recommendations.items():
            if not st.sidebar.checkbox(recommendation_type, value=True):
                continue
            if len(recommended_songs) == 0:
                continue
            st.write(f'#### {recommendation_type.title()}')
            for song in recommended_songs:
                track_name = song["track_name"]
                track_artist = song["track_artist"]
                # Fetch track ID from the song dictionary
                track_id = songs.loc[song['index'], 'track_id']
                # Generate Spotify track URL
                spotify_track_url = f"https://open.spotify.com/track/{track_id}"
                # Make the track name a clickable link
                st.markdown(f'Track: [{track_name}](https://open.spotify.com/track/{track_id})')
                st.write(f'Artist: {track_artist}')
