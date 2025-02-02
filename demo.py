print("Start ")
import flask
import os
from harsh import get_weather
import json
import pandas as pd
from flask import send_from_directory, request
import subprocess

app = flask.Flask(__name__)
app.secret_key='Itissecret'
app.debug= True

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'),
                               'favicon.ico',mimetype='image/favicon.png')

@app.route('/')
@app.route('/home')
def home():
    return get_weather(52.52,13.41)

@app.route('/demo',methods=['POST'])
def harsh():
    req=request.get_json(force=True)
    # print(req)
    print(req['queryResult']['intent']['displayName'],"---------------")
    

    if req['queryResult']['intent']['displayName']== 'Default Welcome Intent - custom':
        number= req['queryResult']['queryText'].split(',')
        number= [float(i) for i in number]
        print(number)
        lat = number[0]
        long= number[1]
        nf = pd.read_csv("cordinates.csv")
        nf = nf[['lat','long']]
        new_row = {"lat": lat, "long": long}
        nf.loc[len(nf)] = new_row 
        nf.to_csv("cordinates.csv")

    nf = pd.read_csv("cordinates.csv")
     
    if (len(nf>100)):
        nf.drop(nf.index.to_list()[:-1], axis=0)

    nf = nf[['lat','long']]
    lat = list(nf.lat)[-1]
    long = list(nf.long)[-1]
    df = json.loads(get_weather(lat,long))

    ff = req['queryResult']['intent']['displayName']
    if ff=='Default Welcome Intent - custom':
        return {'fulfillmentText': "How may I assist you with your weather-related inquiry?"}
    elif ff=='Cloudcover':
        return {'fulfillmentText': df['Cloudcover']}
    elif ff=='Currenthumidity':
        return {'fulfillmentText':df['Currenthumidity']}
    elif ff=='currentoverviewweather':
        return {'fulfillmentText':df['currentoverviewweather']} #
    elif ff=='Currenttemp':
        return {'fulfillmentText':df['Currenttemp']}
    elif ff=='Dailydaylightduration':
        return {'fulfillmentText':df['Dailydaylightduration']}
    elif ff=='Dailyfeelsliketempmax':
        return {'fulfillmentText':df['Dailyfeelsliketempmax']}
    elif ff=='Dailyfeelsliketempmin':
        return {'fulfillmentText':df['Dailyfeelsliketempmin']}
    elif ff=='Dailyprecipitationprobabilitymax':
        return {'fulfillmentText':df['Dailyprecipitationprobabilitymax']}
    elif ff=='Dailyrainsum':
        return {'fulfillmentText':df['Dailyrainsum']}
    elif ff=='Dailysnowfallsum':
        return {'fulfillmentText':df['Dailysnowfallsum']}
    elif ff=='Dailytempmax':
        return {'fulfillmentText':df['Dailytempmax']}
    elif ff=='Dailytempmin':
        return {'fulfillmentText':df['Dailytempmin']}
    elif ff=='Dailywindspeedmax':
        return {'fulfillmentText':df['Dailywindspeedmax']}
    elif ff=='Feelsliketemp':
        return {'fulfillmentText':df['Feelsliketemp']}
    elif ff=='forecastoverview':
        return {'fulfillmentText':df['Weathercode']}
    elif ff=='Nightduration':
        return {'fulfillmentText':df['Dailynightduration']}
    elif ff=='Visibility':
        return {'fulfillmentText':df['Visibility']}
    
    else:
        return {'fulfillmentText': 'Hello from Script'}
            


if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))

    with open("startngrok.sh", "r") as file:
        script_content = file.read().replace("\r", "")  # Remove '\r' characters
    
    with open("startngrok.sh", "w") as file:
        file.write(script_content)  # Save the fixed script
    
    # Ensure the script is executable (Render should respect this)
    subprocess.run(["chmod", "+x", "startngrok.sh"])
    
    subprocess.Popen(["bash", "startngrok.sh"])
    app.run(host="0.0.0.0", port=port)
