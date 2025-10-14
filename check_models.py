import google.generativeai as genai
import os

# --- IMPORTANT ---
# This script MUST be run from the command line using: python check_models.py
# Do NOT run it with "streamlit run".

def get_api_key_from_secrets():
    """A robust, simple function to read the API key from the secrets.toml file."""
    secrets_path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
    if not os.path.exists(secrets_path):
        print("ERROR: .streamlit/secrets.toml file not found.")
        return None
    
    with open(secrets_path, 'r') as f:
        for line in f:
            # Look for the line containing the key
            if 'gemini_api_key' in line:
                # Split the line at the '=' sign
                parts = line.split('=')
                if len(parts) == 2:
                    # Get the second part, and strip whitespace and any quotes
                    api_key = parts[1].strip().strip('"').strip("'")
                    return api_key
    
    print("ERROR: 'gemini_api_key' not found in .streamlit/secrets.toml")
    return None

try:
    api_key = get_api_key_from_secrets()
    if api_key:
        genai.configure(api_key=api_key) # type: ignore
    else:
        # Exit the script if the key couldn't be found
        exit()

    print("--- Finding available models for your API key ---")
    
    found_models = False
    # List all models that support the 'generateContent' method
    for m in genai.list_models(): # type: ignore
      if 'generateContent' in m.supported_generation_methods:
        print(f"Model found: {m.name}")
        found_models = True

    if not found_models:
        print("\nNo models supporting 'generateContent' were found for your API key.")
        print("This could be due to API key restrictions or regional availability.")

    print("\n--- Finished ---")
    print("Please use one of the model names from the list above in your app.py file.")
    print("A likely candidate is 'models/gemini-1.0-pro'.")

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure your Gemini API key in secrets.toml is correct.")

