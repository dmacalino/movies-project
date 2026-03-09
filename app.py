import streamlit as st
import pandas as pd

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎬 Movie Genre Explorer",
    page_icon="🎬",
    layout="wide",
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("movies_cleaned.csv")
    return df

df = load_data()

# ── Extract unique individual genres ─────────────────────────────────────────
all_genres = sorted(
    set(
        genre
        for genres_str in df["genres"].dropna()
        for genre in genres_str.split("|")
        if genre != "(no genres listed)"
    )
)

# ── App Header ────────────────────────────────────────────────────────────────
st.title("🎬 Movie Genre Explorer")
st.markdown(
    "Explore movies by genre. Select **one genre** from the dropdown to see all matching titles."
)
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 About this App")
    st.markdown(
        """
        **Dataset:** MovieLens movies.csv  
        **Total movies:** {:,}  
        **Genres available:** {}  
        """.format(len(df), len(all_genres))
    )
    st.divider()
    st.markdown("Built with **Streamlit** 🚀")

# ── Genre Selection ───────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 3])

with col1:
    selected_genre = st.selectbox(
        "🎭 Select a Genre",
        options=["— Select a genre —"] + all_genres,
        index=0,
    )

# ── Filter and display ────────────────────────────────────────────────────────
if selected_genre == "— Select a genre —":
    st.info("👆 Please select a genre from the dropdown to see movies.")
    
    # Show genre overview chart data
    st.subheader("📊 Genre Overview")
    genre_counts = pd.Series(
        [
            genre
            for genres_str in df["genres"].dropna()
            for genre in genres_str.split("|")
            if genre != "(no genres listed)"
        ]
    ).value_counts().reset_index()
    genre_counts.columns = ["Genre", "Number of Movies"]
    
    col_chart, col_table = st.columns(2)
    with col_chart:
        st.bar_chart(genre_counts.set_index("Genre").head(15))
    with col_table:
        st.dataframe(genre_counts, use_container_width=True, hide_index=True)

else:
    # Filter movies that contain EXACTLY this genre (not just substring match)
    mask = df["genres"].str.split("|").apply(
        lambda genres_list: selected_genre in genres_list
        if isinstance(genres_list, list)
        else False
    )
    filtered = df[mask][["movieId", "Title", "Year", "genres"]].copy()
    filtered = filtered.sort_values("Year", ascending=False, na_position="last")
    filtered["Year"] = filtered["Year"].astype("Int64")
    filtered.columns = ["Movie ID", "Title", "Year", "All Genres"]

    with col2:
        st.metric("Movies found", f"{len(filtered):,}")

    st.subheader(f"🎞️ Movies in: **{selected_genre}**")
    
    # Search within results
    search = st.text_input("🔍 Filter by title within results", placeholder="e.g. Star Wars")
    if search:
        filtered = filtered[filtered["Title"].str.contains(search, case=False, na=False)]

    st.dataframe(
        filtered.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Movie ID": st.column_config.NumberColumn(width="small"),
            "Year": st.column_config.NumberColumn(format="%d", width="small"),
            "Title": st.column_config.TextColumn(width="large"),
            "All Genres": st.column_config.TextColumn(width="medium"),
        },
    )

    st.caption(f"Showing {len(filtered):,} movie(s) tagged with the **{selected_genre}** genre.")
