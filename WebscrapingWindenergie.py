import datetime
import time
from firebase import firebase
from urllib.request import urlopen as uReq
import json
import pytz

TimeZone = "Europe/London"
fmt = '%Y-%m-%dT%H:%M'
Firebase = firebase.FirebaseApplication("https://rend-a7592.firebaseio.com/",None)




def SendFirebase(Json,Datum): #Json is een list

    Resultaat = Firebase.get(f"/Windenergie/{Datum}/",None)
    if Resultaat == None: 
        for Data in Json :
            result = Firebase.post(f"/Windenergie/{Datum}/",Data) 
    
    else:
        for Data in Json:
            for Value in Resultaat:
                ValueList = Resultaat.get(Value)
                if(ValueList['RealTimeAvailable']== False and Data['RealTimeAvailable'] == True and 
                    ValueList['ForcastDate'] == Data['ForcastDate']):
                    result1 = Firebase.put(f"/Windenergie/{Datum}/{Value}", 'RealTimeAvailable', Data['RealTimeAvailable'])
                    result = Firebase.put(f"/Windenergie/{Datum}/{Value}/RealTime", 'RealForcast', Data['RealTime']['RealForcast'])
                    
                    break


def ReadPageUrl(TodayDate):
    Scrape_Url = f"https://griddata.elia.be/eliabecontrols.prod/interface/windforecasting/forecastdata?beginDate={TodayDate}&endDate={TodayDate}&region=1&isEliaConnected=&isOffshore=.xml"
    
    #Downloading the page
    PageData = uReq(Scrape_Url)
    Page_XML = PageData.read()
    PageString = str(Page_XML)
    PageData.close();
    
    return PageString

def ConverToJson(PageString):
    RemoveItems = "b'"
    for item in RemoveItems : 
        PageString=  PageString.replace(item , "")
    
    #Maakt een list 
    DataJson = json.loads(PageString)
    return DataJson
    
def GetData(DataJson,Datum):
    SendData = []
    for Data in DataJson : 
        if  Data['realtime'] == None : 
            SendData.append({
                'ForcastDate' :Data['startsOn'],
                'DayAHeadForcast':Data['dayAheadForecast'],
                'RealTimeAvailable':False,
                'RealTime':{
                    'RealForcast' : None
                }
            })
        else :
            SendData.append({
                'ForcastDate': Data['startsOn'],
                'DayAHeadForcast':Data['dayAheadForecast'],
                'RealTimeAvailable':True,
                'RealTime':{
                    'RealForcast' : Data['realtime']
                }
            })

        #SendData = json.loads(SendData)
        #print(SendData[0])
    #print(SendData)

    SendFirebase(SendData,Datum)

def main(): 
    utc = pytz.utc
    utc.zone
    Zone = pytz.timezone(TimeZone)
    TodayDate = datetime.date.today()
    print("Initial Done")
    while True :
        try:
            TodayDate = datetime.date.today()
            Page_String = ReadPageUrl(TodayDate)
            DataJson = ConverToJson(Page_String)
            GetTime = datetime.datetime.now(Zone)
            GetTime = GetTime.strftime(fmt) + ":00+00:00"
            GetData(DataJson,TodayDate)

            print("Done")
            time.sleep(240)
        except Exception as Error:
            print(Error)


if __name__ == "__main__":
    main()