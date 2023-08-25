import streamlit as st

import looker_sdk
from shortuuid import uuid

from IPython.display import IFrame

import json
import vertexai
from vertexai.language_models import TextGenerationModel

import pandas as pd

st.title('Executive Virtual Assistant - EVA')

sdk = looker_sdk.init40('looker.ini')

model_name = st.selectbox(
    'Select Looker Model',
    ['mitochondrion_looker', 'thelook']
)

# model_name = 'mitochondrion_looker'
# question = 'for each zip code, what is their total conversion'

# question = 'what is the zip code with the highest total number of conversion?'
question = st.text_input('question', 'what is the zip code with the highest total number of conversion?')

# st.write(question)

lookml_model = sdk.lookml_model(model_name)

explores = [exp.name for exp in lookml_model.explores]

views = []

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
        
    views += [abc]

template = """
{context}

You are an expert data analyst. Follow these instructions.
Given the above LookML model file definition, construct a valid JSON. 
The JSON should contains the correct view and only the necessary fields to answer the questions.

Input: what is the total conversion for each channel?
Output:
{{
"view": "marketing",
"fields": [
            "marketing.channel",
            "marketing.total_conversion"
        ]
}}

Input: {question}
Output:
"""

llm = TextGenerationModel.from_pretrained('text-bison@001')
prompt = template.format(question=question, context=str(views))
response = llm.predict(prompt, temperature=0)


chart_options = ['looker_column' ,'looker_bar','looker_line','looker_scatter','looker_area','looker_pie','single_value','looker_grid','looker_google_map']

chart_template = """
['looker_column', 'looker_line', 'looker_scatter', 'looker_area', 'looker_pie', 'single_value', 'looker_grid', 'looker_google_map']

You are an expert data analyst.
Pick the most appropriate looker visualization option based on the list above and sample of data from pandas dataframe.
For example, if the first column is categorical, the second column is numerical, and there is only less than 5 rows, output looker_pie. If the number of rows is more than 5 output looker_bar

Input: 
user_group, num_transaction
group_1, 90
group_2, 10
Output:
looker_pie

Input: 
customer_id, num_transaction
Alex, 123
Jon, 345
Dave, 123
Max, 345
Zia, 333
Tommy, 876
Output:
looker_column

Input:
10988
Output:
single_value

Input:
date, value
2023-08-01, 10
2023-08-02, 22
2023-08-03, 31
Output:
looker_line

Input:
{dataframe_string}
Output:
"""

json_query = json.loads(str(response))
json_query['model'] = model_name

output = sdk.run_inline_query('json', json_query)
df = pd.DataFrame(json.loads(output))
df.head()

chart_prompt = chart_template.format(dataframe_string=str(df))

chart_type = llm.predict(chart_prompt, temperature=0)
json_query['vis_config'] = {
        'type': f'{chart_type}'
    }

query_result = sdk.create_query(json_query)

look_query = {
  "title": f'Visualization using Vertex Palm API_{uuid()[:8]}',
  "user_id": "8",
  "description": "test",
  "public": True,
  "query_id": f"{query_result['id']}",
  "folder": {},
  "folder_id": "6"
}

look_result = sdk.create_look(look_query)


prompt = f"""
{str(df)}

You are an expert data analyst. Based on the data above, answer this question.

{question}
"""

import streamlit.components.v1 as components

components.iframe(look_result['embed_url'])

# IFrame(look_result['embed_url'], width=700, height=300)

answer = llm.predict(prompt, temperature=0)

st.write(str(answer.text))