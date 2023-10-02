from fastapi import FastAPI, File, UploadFile
from fastapi.utils import generate_unique_id
import requests,json
import logging
import pandas as pd
import io
import uvicorn
def get_access_token():
    #Provides an access token received from api
    main_url = "https://api.baubuddy.de/index.php/login"
    payload = {
        "username": "365",
        "password": "1"
    }
    headers = {
        "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
        "Content-Type": "application/json"
    }
    response = requests.request("POST", main_url, json=payload, headers=headers)
    response = response.json()
    access_token = response['oauth']['access_token']
    return access_token 


app=FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/")
async def upload_csv(file: UploadFile = File(...)):
    #Creates an post request waits until files to be ready and commits them according to file
    contents = await file.read()
    
    access_token = get_access_token()

    url = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
    head = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.request("GET", url, headers=head)
    response_data=response.json()
    response_df=pd.DataFrame(response_data)
    string_data = contents.decode('utf-8')
    #Csv arrangement on account of ; 
    df_csv = pd.read_csv(io.StringIO(string_data), sep=';')
    
    #Control hu parameter 
    response_df=response_df[response_df['hu'].isnull()==False]
    #Convertion of None values to empty string to ease job 
    response_df=response_df.fillna('')
    df_csv=df_csv.fillna('')
    #Find common columns to merge data
    common_columns = df_csv.columns.intersection(response_df.columns)


    matching_rows = []
    #find equal rows based on common columns and hold them in according to columns of response_df 
    for index1, row1 in df_csv.iterrows():
        for index2, row2 in response_df.iterrows():
            if row1[common_columns].equals(row2[common_columns]):
                matching_rows.append(index2)
                break

    result_df = response_df.loc[matching_rows] 

    result_df=result_df.to_json()
    result_df=json.loads(result_df)
    return result_df
    

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="127.0.0.1")



  
