# 🎬 Conversational Movie Recommender

This is a sophisticated, AI-powered movie database assistant built with Python, Streamlit, and Google's Gemini Pro model. It goes beyond simple recommendations, allowing users to explore a vast movie database through natural, conversational language.
<img width="1042" height="785" alt="image" src="https://github.com/user-attachments/assets/ffa9b46f-5ce0-47cc-86d2-466352c94609" />
 
## ✨ Features

This application leverages the Gemini AI's "Tool Use" capability to provide a wide range of features. The AI intelligently understands the user's request and chooses the correct tool to get the job done.

Here's what it can do:

### 🎭 Get Recommendations by Genre

Prompt: "I'm in the mood for some comedy movies" or "action and thriller"
Action: Fetches the most popular movies that match the requested genre(s).

<img width="999" height="767" alt="image" src="https://github.com/user-attachments/assets/2093a552-abee-4544-bfcc-0d95d4215a98" />

### 🔍 Search for a Specific Movie

Prompt: "Find the movie Inception" or simply "Inception"
Action: Locates the specific movie and displays its details, poster, cast, and director.

<img width="948" height="767" alt="image" src="https://github.com/user-attachments/assets/8e3f0362-c4ca-4625-9335-c90fa3185320" />

<img width="986" height="595" alt="image" src="https://github.com/user-attachments/assets/f5f3a8c0-afb2-47d7-ae6b-edc77b2bffa2" />

### 👯 Find Similar Movies

Prompt: "Recommend movies similar to Interstellar"
Action: Finds the movie you mentioned and then uses the TMDb API to discover and display other movies with a similar theme and style.

<img width="993" height="620" alt="image" src="https://github.com/user-attachments/assets/b1b6f93f-8b50-48d8-8190-49260d483b72" />

### 🔥 Discover Trending Movies

Prompt: "What's trending today?" or "Show me this week's trending movies"
Action: Fetches and displays the top 5 movies that are currently trending.

<img width="1010" height="656" alt="image" src="https://github.com/user-attachments/assets/91460380-ee35-4e8d-ba93-089b5e1fb519" />


### ⭐ List Top-Rated Movies

Prompt: "What are the best movies of all time?"
Action: Retrieves and displays the highest-rated movies according to the TMDb database.

<img width="963" height="594" alt="image" src="https://github.com/user-attachments/assets/e9e05b55-b4c2-4003-b68c-eaeadf0b4326" />

### 🧑‍🎤 Find Movies by Actor

Prompt: "Show me movies with Tom Hanks"
Action: Finds the most popular movies starring the specified actor.

<img width="991" height="597" alt="image" src="https://github.com/user-attachments/assets/88072f47-0d8e-45b7-87ac-9d9d7617d38f" />

### 🎥 Find Movies by Director

Prompt: "Find movies directed by Christopher Nolan"
Action: Finds the most popular movies directed by the specified person.

<img width="1025" height="714" alt="image" src="https://github.com/user-attachments/assets/6ab2447c-c55e-4bf3-b92e-92224752f88b" />

## 💻 Technologies Used

- Frontend: Streamlit

- AI & Language Model: Google Gemini 2.5 flash

- Movie Data: The Movie Database (TMDb) API

- Core Language: Python

## 🚀 How It Works: The AI Tool-Use Architecture

The core of this application is its modern AI architecture. Instead of relying on rigid if/else logic, we give the Gemini AI a "tool belt" of functions.

- User Prompt: The user types a natural language request (e.g., "What are some good sci-fi movies like Blade Runner?").

- AI Analysis: The Gemini model analyzes the prompt to understand the user's intent.

- Tool Selection: The AI determines that the user wants movies "similar to" another movie and selects the get_similar_movies tool. It also extracts "Blade Runner" as the required argument.

- Function Execution: The Python application executes the chosen helpers.py function with the arguments provided by the AI.

- API Call: The function calls The Movie Database (TMDb) API to fetch the relevant movie data.

- Display Results: The results are returned to the Streamlit app, which then displays the movie posters and details in a clean, user-friendly interface.

This architecture makes the application incredibly flexible and easy to extend. To add a new feature, we simply have to write a new tool function and add it to the AI's tool belt.

## 🎬Want to test the app? Here's the link!:
https://recommender-of-movies-uqgvkygpqrbw9x2kf75npn.streamlit.app/

Hope you like it, feel free to comment!

Stay tuned for more imporvements!

   -5und4r





