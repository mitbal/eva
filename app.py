import json
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import looker_sdk
from shortuuid import uuid
from vertexai.language_models import TextEmbeddingModel
from vertexai.preview.language_models import TextGenerationModel

st.set_page_config(
    page_title='EVA - Executive Virtual Assistant',
    page_icon='random'
)

st.title('Executive Virtual Assistant - EVA')

model_name = st.sidebar.selectbox(
    'Select Looker Model',
    ['mini_look', 'mitochondrion_looker', 'thelook', 'retail_block_model']
)
sdk = looker_sdk.init40('looker.ini')

vertex_model_name = st.sidebar.selectbox(
    'Select Vertex Model',
    ['text-bison-32k', 'text-bison@001']
)

llm = TextGenerationModel.from_pretrained(vertex_model_name)
gecko = TextEmbeddingModel.from_pretrained('textembedding-gecko@001')

## Looker setup and initialization
@st.cache_data
def init_looker(looker_model_name):

    lookml_model = sdk.lookml_model(model_name)

    explores = [exp.name for exp in lookml_model.explores]

    views = {}
    total_fields = 0
    for exp in explores:
        
        explore = sdk.lookml_model_explore(
            lookml_model_name=model_name,
            explore_name=exp
        )
        
        abc = {}
        abc['view'] = exp
        abc['fields'] = []
        
        for dim in explore.fields.dimensions:
            abc['fields'] += [dim.name]
            
        for dim in explore.fields.measures:
            abc['fields'] += [dim.name]
            
        views[exp] = abc
        total_fields += len(abc['fields'])

    for view_name, view_content in views.items():
        view_embeddings = gecko.get_embeddings([str(view_content)])
        views[view_name]['embedding'] = view_embeddings[0].values

    st.write(f'Processed {len(views)} explores with {total_fields} of fields total')
    return views

views = init_looker(model_name)

with st.expander('Complete Explores'):
    st.write([{key:views[i][key] for key in ['view', 'fields']} for i in views.keys()])

## Translate natural language query to looker query based on lookml definition above
question = st.text_input('question', 'which product has the highest revenue?')

q_embedding = gecko.get_embeddings([question])
q_vector = q_embedding[0].values

max_score = -1000000
relevant_view = None
for view_name, view_content in views.items():
    view_vector = view_content['embedding']

    score = np.dot(view_vector, q_vector)
    # st.write(view_name, score)

    if score > max_score:
        max_score = score
        relevant_view = view_name

winning_view = {key:views[relevant_view][key] for key in ['view', 'fields']}
st.write(f'Most relevant view with score {max_score}', relevant_view)

if max_score < 0.5:
    st.write('No relevant information is available in the data. Please try a different questions')
    st.stop()

with open('looker_query.template', 'r') as f:
    looker_query_template = f.read()

prompt = looker_query_template.format(question=question, 
                                      context=str(winning_view),
                                      date=datetime.today().strftime('%Y-%m-%d'))
response = llm.predict(prompt, temperature=0)

# generate visualization using looker with the json payload above
with open('looker_viz.template', 'r') as f:
    chart_template = f.read()

json_query = json.loads(str(response.text))
json_query['model'] = model_name

output = sdk.run_inline_query('json', json_query)
df = pd.DataFrame(json.loads(output))
df.head()

chart_prompt = chart_template.format(dataframe_string=str(df))

chart_type = llm.predict(chart_prompt, temperature=0)
json_query['vis_config'] = {
        'type': f'{chart_type.text.strip()}'
    }

query_result = sdk.create_query(json_query)

st.write(json_query)

look_query = {
  "title": f'Chart ID_{uuid()[:8]}',
  "user_id": "8",
  "description": "test",
  "public": True,
  "query_id": f"{query_result['id']}",
  "folder": {},
  "folder_id": "6"
}

look_result = sdk.create_look(look_query)
components.iframe(look_result['embed_url'], height=400, scrolling=True)

# Answer the questions given above based on the dataframe returned from looker
prompt = f"""
You are an expert data analyst who are truthful.
Based on the data above, answer the following question succinctly.
If the answer is not obvious, do not make up stuff or print python code.

Context:
   year company  market_cap\n0  2022    BBRI         500\n1  2022    UNVR         600\n2  2022    ASII         400\n3  2023    BBRI         709\n4  2023    UNVR         165\n5  2023    ASII         242\n
Question:
What is the average market cap of the company with lowest market cap in 2022 all throughout the years?
Answer:
The company with the lowest market cap in 2022 is UNVR. The average market cap of UNVR all throughout the years is 381.5

Context:
{str(df)}
Question:
{question}
Answer:
"""

if chart_type.text.strip() != 'looker_grid':
    st.dataframe(df.head(10))

answer = llm.predict(prompt, temperature=0)
st.text_area('answer', str(answer.text), disabled=True)
