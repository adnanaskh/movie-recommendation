# Movie Recommendation System

> A content-based movie recommender that finds films with similar descriptions and genres, then presents enriched results in a Streamlit interface.

**Designed and developed by Adnan Ahmad**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

## Overview

This project recommends movies by comparing the text content of movies in a catalog. The system does not require user ratings or a user profile. Instead, it uses the selected movie's genre and plot overview to locate titles with similar language and themes.

The project has two parts:

1. **Model preparation:** `main.ipynb` reads the dataset, selects relevant fields, combines genre and overview text into tags, vectorizes those tags, calculates pairwise cosine similarity, and serializes the processed movie table.
2. **Interactive application:** `app.py` loads the processed movie table and similarity matrix, lets a user select a title, ranks the closest movies, and fetches poster, genre, year, and plot details from the OMDb API.

## Features

- Content-based recommendations from a movie's genre and overview.
- A searchable Streamlit dropdown containing the available movie titles.
- Five recommendations per selected movie.
- Poster, year, genre, and plot information for each recommendation.
- Cached similarity-matrix loading to avoid downloading the matrix on every rerun.
- Notebook workflow for inspecting the data and rebuilding the model artifacts.

## How The System Works

### 1. Input data

`moviesDataset.csv` contains 10,000 movies and the following fields:

| Column | Purpose |
| --- | --- |
| `id` | Movie identifier |
| `title` | Movie title shown to the user |
| `genre` | Comma-separated genre labels |
| `original_language` | Original language code |
| `overview` | Plot description used for similarity |
| `popularity` | Dataset popularity value |
| `release_date` | Original release date |
| `vote_average` | Average user rating |
| `vote_count` | Number of votes |

The training workflow keeps `id`, `title`, `genre`, and `overview`. It then creates a `tags` field:

```text
tags = overview + genre
```

The current dataset contains 3 missing `genre` values and 13 missing `overview` values. The notebook does not explicitly impute these values, so preprocessing behavior should be reviewed before rebuilding the artifacts with a different dataset.

### 2. Text vectorization

The tags are converted into a numerical bag-of-words representation with:

```python
CountVectorizer(max_features=10000, stop_words="english")
```

This produces one vector per movie. Each vector represents the words found in that movie's combined overview and genre text. English stop words are removed, and the vocabulary is limited to the 10,000 most useful features selected by the vectorizer.

### 3. Similarity mathematics

For every movie, let its vector be:

$$
\mathbf{x}_i = (x_{i1}, x_{i2}, \ldots, x_{id})
$$

where each component records a word count and $d$ is the vectorizer vocabulary size. The similarity between movies $i$ and $j$ is cosine similarity:

$$
\operatorname{sim}(i,j) =
\frac{\mathbf{x}_i \cdot \mathbf{x}_j}
{\lVert\mathbf{x}_i\rVert_2\lVert\mathbf{x}_j\rVert_2}
$$

Interpretation:

- A value near `1` means the movies have very similar text features.
- A value near `0` means they share little or no represented vocabulary.
- Because this is a content-based method, recommendations reflect textual similarity, not personal taste or collaborative user behavior.

The notebook calculates the complete similarity matrix:

```python
similarity = cosine_similarity(vector)
```

For a selected movie, the app finds its row in the matrix, pairs each score with a movie index, sorts by score in descending order, and returns the next five titles after the selected movie itself.

## Runtime Flow

```text
User selects a movie
        |
        v
Find selected title index in movies_list.pkl
        |
        v
Read that movie's similarity scores
        |
        v
Sort scores from highest to lowest
        |
        v
Choose the top five other movies
        |
        v
Request details from OMDb for each title
        |
        v
Render posters, titles, years, genres, and plots in Streamlit
```

## Project Structure

```text
movie-recommendation/
|
|-- app.py                  # Streamlit user interface and recommendation logic
|-- main.ipynb              # Data exploration and model-building workflow
|-- main.py                 # Basic CSV loading and dataset inspection script
|-- moviesDataset.csv       # Source catalog: 10,000 movie records
|-- movies_list.pkl         # Serialized processed movie table with id, title, tags
|-- requirements.txt        # Python dependencies
|-- README.md               # Project documentation
```

### Generated or external artifact

The notebook includes a step that writes `similarity.pkl` locally. The current `app.py` does not read a local `similarity.pkl`; instead, it downloads the similarity matrix from Google Drive the first time the app runs and caches the result as `similarity.pkl`.

## Requirements

- Python 3.9 or newer recommended.
- Internet access on the first app run so the similarity matrix can be downloaded.
- Internet access while showing recommendations so OMDb metadata and posters can be requested.
- A working OMDb API key. The current app contains a key directly in `app.py`; use an environment variable before deploying publicly.

The declared dependencies are:

```text
streamlit >= 1.33.0
gdown >= 5.1.0
requests >= 2.31.0
pandas >= 2.2.2
```

The notebook also uses `scikit-learn`, specifically `CountVectorizer` and `cosine_similarity`. Install it if it is not already available in the environment:

```powershell
python -m pip install scikit-learn
```

## Installation

Open PowerShell in the project directory:

```powershell
cd D:\movie-recommendation
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation for the current user, run PowerShell as permitted by your local policy or activate the environment through another supported shell.

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install scikit-learn
```

## Run The Application

Start Streamlit from the project root:

```powershell
streamlit run app.py
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

Then:

1. Open the local URL in a browser.
2. Choose a movie from the dropdown.
3. Select **Show Recommendation**.
4. Review the five recommended movies and their OMDb details.

On the first launch, `app.py` downloads the similarity artifact from Google Drive and saves it as `similarity.pkl`. Later launches reuse that local file.

## Rebuild The Model Artifacts

Use this workflow when the CSV changes or the model configuration needs to be regenerated:

1. Open `main.ipynb` in VS Code or Jupyter.
2. Select the virtual environment containing `pandas` and `scikit-learn`.
3. Run the cells in order.
4. Confirm that `moviesDataset.csv` loads successfully.
5. Confirm that the vectorizer and cosine-similarity cells complete.
6. Run the serialization cells to create:

   - `movies_list.pkl`: processed movie data with `id`, `title`, and `tags`.
   - `similarity.pkl`: the pairwise similarity matrix.

The notebook currently creates a local similarity file, while the deployed app points to a Google Drive copy identified in `app.py`. If the dataset or row ordering changes, the hosted similarity matrix must be regenerated and replaced as well; the movie table and matrix must have matching row order and dimensions.

## Data And Artifact Contract

The app assumes:

- `movies_list.pkl` is a pandas DataFrame.
- The DataFrame has a `title` column.
- Movie row positions match the rows and columns of the similarity matrix.
- Every selected title has at least one matching row.
- The similarity matrix can be loaded with Python `pickle`.

The current serialized movie table has shape `(10000, 3)` and columns:

```text
id, title, tags
```

## Important Implementation Notes

- Recommendations are based on text similarity only. Ratings, popularity, language, release date, and vote count are not used by the current recommender.
- The app returns five results by using the sorted similarity list after skipping the selected movie.
- OMDb requests use the movie title as the query. Ambiguous or uncommon titles may produce incomplete metadata.
- When OMDb cannot return a record, the app falls back to `N/A` values and a placeholder poster.
- The similarity matrix is loaded through Streamlit's `@st.cache_data`, so the download/load operation is reused during the app session.
- `pickle` files should only be loaded from trusted sources because unpickling can execute arbitrary code.
- The current OMDb key is present in source code. For production use, move it to a secret or environment variable and avoid committing credentials.

## Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and reinstall dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install scikit-learn
```

### Similarity download fails

Check internet access and confirm that the Google Drive file referenced by `file_id` in `app.py` is still available. A local `similarity.pkl` can be generated from the notebook, but the current app only uses it after the download logic has been adapted to prefer local artifacts.

### OMDb details are missing

Check internet access, the API key, the OMDb response limit, and the selected title. The app intentionally displays fallback values when OMDb returns an unsuccessful response.

### The app and artifacts disagree

Regenerate both `movies_list.pkl` and `similarity.pkl` from the same dataset in the same row order. A movie table from one dataset cannot safely be paired with a similarity matrix generated from another.

## Future Improvements

- Load the OMDb API key from `st.secrets` or an environment variable.
- Add request timeouts and clearer API error messages.
- Handle missing text values explicitly before concatenating tags.
- Use TF-IDF vectors to reduce the influence of very common words.
- Add genre, language, rating, and popularity filters.
- Add recommendation evaluation with a defined offline metric.
- Prefer a versioned local or hosted artifact pipeline instead of a hard-coded download URL.
- Add automated tests for artifact compatibility and recommendation ordering.

## Author

**Adnan Ahmad**

This project was designed and developed by Adnan Ahmad as a practical demonstration of text feature extraction, cosine-similarity recommendation, serialized model artifacts, API integration, and Streamlit application development.

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2026 Adnan Ahmad.