import streamlit as st
import google.generativeai as genai
from google.ai import generativelanguage as glm
import helpers
import json

# --- 1. API and Model Configuration ---
try:
    genai.configure(api_key=st.secrets["gemini_api_key"]) # type: ignore
except Exception as e:
    st.error(f"Error configuring the Gemini API: {e}", icon="🚨")
    st.stop()

# --- 2. Tool Definition ---
tools = [
    helpers.search_movie,
    helpers.get_recommendations_by_genre,
]

# --- 3. Model and Chat Initialization ---
safety_settings = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
}

model = genai.GenerativeModel( # type: ignore
    model_name="models/gemini-2.5-flash-preview-05-20",
    safety_settings=safety_settings
)
chat = model.start_chat()

# --- 4. App Setup and State Initialization ---
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎬 Gemini Movie Recommender")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I'm your movie-buff assistant. Ask me to find a movie by title or recommend something by genre!"}
    ]

# --- 5. UI Display ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "results" in message:
            results = message["results"]
            if results:
                if isinstance(results, dict):
                    results = [results]
                
                cols = st.columns(len(results))
                for i, movie in enumerate(results):
                    with cols[i]:
                        if movie and movie.get("poster_path"): # type: ignore
                            st.image(f"https://image.tmdb.org/t/p/w200{movie.get('poster_path')}", caption=movie.get('title')) # type: ignore
                        if movie:
                            st.markdown(f"**{movie.get('title', 'N/A')}**") # type: ignore
                            if st.button("Show Details", key=f"details_{movie.get('id')}_{i}"): # type: ignore
                                    st.session_state.selected_movie = movie # type: ignore
                                    st.rerun()

if 'selected_movie' in st.session_state and st.session_state.selected_movie:
    movie = st.session_state.selected_movie
    with st.container():
        st.subheader(f"Details for: {movie.get('title')}") # type: ignore
        col1, col2 = st.columns([1, 2])
        with col1:
             if movie.get('poster_path'): # type: ignore
                st.image(f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}", use_container_width=True) # type: ignore
        with col2:
            st.write(f"**Synopsis:** {movie.get('overview', 'No synopsis available.')}") # type: ignore
            st.write(f"**Cast:** {', '.join(movie.get('cast', ['N/A']))}") # type: ignore
            st.write(f"**Director:** {movie.get('director', 'N/A')}") # type: ignore
            if st.button("Back to Recommendations"):
                del st.session_state.selected_movie
                st.rerun()

# --- 6. User Input and Chat Logic ---
if prompt := st.chat_input("Ask me for a movie, genre, or something similar..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = chat.send_message(prompt, tools=tools)

    try:
        response_part = response.candidates[0].content.parts[0]
        if hasattr(response_part, 'function_call') and response_part.function_call:
            with st.spinner("Calling my movie database tool... 🎬"):
                function_call = response_part.function_call
                tool_function = next((f for f in tools if f.__name__ == function_call.name), None)

                if tool_function:
                    tool_response = tool_function(**dict(function_call.args))
                    
                    if tool_response:
                        response_for_ai = tool_response
                        if isinstance(tool_response, dict):
                            response_for_ai = [tool_response]
                        
                        movie_titles = [m.get('title', 'Unknown Title') for m in response_for_ai] # type: ignore
                        tool_response_json = json.dumps(movie_titles)
                    else:
                        tool_response_json = json.dumps("I couldn't find any movies matching that.")

                    final_response = chat.send_message(
                        glm.Part(function_response=glm.FunctionResponse(
                            name=function_call.name,
                            response={"content": tool_response_json}
                        ))
                    )
                    
                    response_text = final_response.text
                    assistant_message = {"role": "assistant", "content": response_text}
                    
                    if tool_response:
                         assistant_message["results"] = tool_response #type: ignore
                    
                    st.session_state.chat_history.append(assistant_message)
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Error: Could not find the tool '{function_call.name}'."})
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})

    except (IndexError, AttributeError, genai.types.StopCandidateException): # type: ignore
        try:
            error_text = response.text
            st.session_state.chat_history.append({"role": "assistant", "content": error_text})
        except (ValueError, AttributeError):
            st.session_state.chat_history.append({"role": "assistant", "content": "I'm sorry, my response was blocked. Please try asking in a different way."})

    st.rerun()

