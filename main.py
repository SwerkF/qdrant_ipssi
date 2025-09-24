import streamlit as st
import pandas as pd
from datetime import datetime

# Import functions directly from app.py
from app import (
    qdrant_client,
    add_movie,
    get_movie_by_id,
    search_movies_by_title,
    get_all_movies,
    update_movie,
    delete_movie
)

# Page configuration
st.set_page_config(
    page_title="Netflix Movies Database",
    page_icon="🎬",
    layout="wide"
)

st.title("Netflix Movies Database")

# Sidebar navigation
page = st.sidebar.selectbox("Select Operation", [
    "View All Movies", 
    "Add Movie", 
    "Search Movies", 
    "Edit Movie", 
    "Delete Movie"
])

if page == "View All Movies":
    st.header("All Movies")
    
    if st.button("Load All Movies"):
        with st.spinner("Loading all movies..."):
            try:
                movies = get_all_movies(qdrant_client)
                
                if movies:
                    st.success(f"Found {len(movies)} movies")
                    
                    for movie in movies:
                        with st.expander(f"{movie.get('title', 'Unknown')} ({movie.get('release_year', 'Unknown')})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Director:** {movie.get('director', 'Unknown')}")
                                st.write(f"**Country:** {movie.get('country', 'Unknown')}")
                                st.write(f"**Rating:** {movie.get('rating', 'Unknown')}")
                                st.write(f"**Duration:** {movie.get('duration', 'Unknown')}")
                            
                            with col2:
                                st.write(f"**Cast:** {', '.join(movie.get('cast', [])) if movie.get('cast') else 'Unknown'}")
                                st.write(f"**Genres:** {movie.get('listed_in', 'Unknown')}")
                                st.write(f"**ID:** {movie.get('id', 'Unknown')}")
                            
                            st.write(f"**Description:** {movie.get('description', 'No description available')}")
                else:
                    st.info("No movies found")
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "Add Movie":
    st.header("➕ Add New Movie")
    
    with st.form("add_movie_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title*")
            director = st.text_input("Director")
            country = st.text_input("Country")
            rating = st.selectbox("Rating", ["G", "PG", "PG-13", "R", "TV-PG", "TV-14", "TV-MA"])
        
        with col2:
            release_year = st.number_input("Release Year", min_value=1900, max_value=2030, value=2024)
            duration = st.text_input("Duration (e.g., '120 min')")
            listed_in = st.text_input("Genres")
            date_added = st.text_input("Date Added")
        
        cast = st.text_area("Cast (comma-separated)")
        description = st.text_area("Description")
        
        submitted = st.form_submit_button("Add Movie")
        
        if submitted and title:
            movie_data = {
                "title": title,
                "director": director,
                "cast": [c.strip() for c in cast.split(',') if c.strip()] if cast else [],
                "country": country,
                "date_added": date_added,
                "release_year": release_year,
                "rating": rating,
                "duration": duration,
                "listed_in": listed_in,
                "description": description
            }
            
            try:
                movie_id = add_movie(qdrant_client, movie_data)
                if movie_id:
                    st.success(f"Movie '{title}' added successfully with ID: {movie_id}")
                    st.balloons()
                else:
                    st.error("Failed to add movie")
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "Search Movies":
    st.header("🔍 Search Movies")
    
    search_term = st.text_input("Search by title")
    
    if search_term and st.button("Search"):
        try:
            movies = search_movies_by_title(qdrant_client, search_term)
            
            if movies:
                st.success(f"Found {len(movies)} movie(s)")
                
                for movie in movies:
                    with st.expander(f"{movie.get('title', 'Unknown')} ({movie.get('release_year', 'Unknown')})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Director:** {movie.get('director', 'Unknown')}")
                            st.write(f"**Country:** {movie.get('country', 'Unknown')}")
                            st.write(f"**Rating:** {movie.get('rating', 'Unknown')}")
                        
                        with col2:
                            st.write(f"**Cast:** {', '.join(movie.get('cast', [])) if movie.get('cast') else 'Unknown'}")
                            st.write(f"**Duration:** {movie.get('duration', 'Unknown')}")
                            st.write(f"**Genres:** {movie.get('listed_in', 'Unknown')}")
                        
                        st.write(f"**Description:** {movie.get('description', 'No description available')}")
            else:
                st.info("No movies found")
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif page == "Edit Movie":
    st.header("✏️ Edit Movie")
    
    movie_id = st.text_input("Enter Movie ID to edit")
    
    if movie_id:
        try:
            movie = get_movie_by_id(qdrant_client, movie_id)
            
            if movie:
                st.success("Movie found!")
                st.json(movie)
                
                with st.form("edit_movie_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        title = st.text_input("Title", value=movie.get('title', ''))
                        director = st.text_input("Director", value=movie.get('director', ''))
                        country = st.text_input("Country", value=movie.get('country', ''))
                        rating = st.selectbox("Rating", ["G", "PG", "PG-13", "R", "TV-PG", "TV-14", "TV-MA"], 
                                            index=0)
                    
                    with col2:
                        release_year = st.number_input("Release Year", min_value=1900, max_value=2030, 
                                                     value=int(movie.get('release_year', 2024)))
                        duration = st.text_input("Duration", value=movie.get('duration', ''))
                        listed_in = st.text_input("Genres", value=movie.get('listed_in', ''))
                        date_added = st.text_input("Date Added", value=movie.get('date_added', ''))
                    
                    cast = st.text_area("Cast (comma-separated)", 
                                      value=', '.join(movie.get('cast', [])) if movie.get('cast') else '')
                    description = st.text_area("Description", value=movie.get('description', ''))
                    
                    submitted = st.form_submit_button("Update Movie")
                    
                    if submitted:
                        updated_data = {
                            "title": title,
                            "director": director,
                            "cast": [c.strip() for c in cast.split(',') if c.strip()] if cast else [],
                            "country": country,
                            "date_added": date_added,
                            "release_year": release_year,
                            "rating": rating,
                            "duration": duration,
                            "listed_in": listed_in,
                            "description": description
                        }
                        
                        try:
                            success = update_movie(qdrant_client, movie_id, updated_data)
                            if success:
                                st.success("Movie updated successfully!")
                            else:
                                st.error("Failed to update movie")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.error("Movie not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif page == "Delete Movie":
    st.header("🗑️ Delete Movie")
    
    movie_id = st.text_input("Enter Movie ID to delete")
    
    if movie_id:
        try:
            movie = get_movie_by_id(qdrant_client, movie_id)
            
            if movie:
                st.warning(f"Movie found: **{movie.get('title', 'Unknown')}**")
                st.json(movie)
                
                if st.button("Delete This Movie", type="primary"):
                    try:
                        success = delete_movie(qdrant_client, movie_id)
                        if success:
                            st.success("Movie deleted successfully!")
                        else:
                            st.error("Failed to delete movie")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Movie not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")
