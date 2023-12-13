## Executive Virtual Assistant - EVA

EVA is a bot that combines the LLM ability to understand natural language and Looker semantic layer to answer user analytical query from their data warehouse. This approach helps to reduce the hallucination because the data definition has been defined in the LookML files.

### How to run it in your local environment
1. Ensure that you have a working python environment
2. Ensure that you have gcloud sdk installed and authenticated
3. Ensure you have `looker.ini` file with Looker user secret
4. Install all the necessary dependencies `pip install -r requirements.txt`
5. Changed the looker model_name, user_id, and folder_id into your own looker project in the `app.py` file
6. Execute `streamlit run app.py`

### How to get looker user secret for step number 3
1. Go to your looker instance
2. Click the Admin menu at the top and pick Users
3. Go to your user page, and click Edit Keys
4. Create a new API Key, and then copy both the client ID and client Secret into the looker.ini
