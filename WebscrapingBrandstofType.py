import datetime
import time
from firebase import firebase
from urllib.request import urlopen as uReq
import json
import sched, time

Firebase = firebase.FirebaseApplication("https://rend-a7592.firebaseio.com/",None)


def SendFirebase(JsonList,Datum, Change):
    Resultaat = Firebase.get(f"/VerzamelinBrandstofType/{Datum}/",None)
    if Resultaat == None: 
        for Data in JsonList :
            result = Firebase.post(f"/VerzamelinBrandstofType/{Datum}/",Data) 
    
    elif Change == True:
        for Data in JsonList:
            for Value in Resultaat:
                ValueList = Resultaat.get(Value)
                if(ValueList['date'] == Data['date']):
                    Firebase.put(f"/VerzamelinBrandstofType/{Datum}/{Value}", 'liquidFuel', Data['liquidFuel'])
                    Firebase.put(f"/VerzamelinBrandstofType/{Datum}/{Value}", 'naturalGas', Data['naturalGas'])
                    Firebase.put(f"/VerzamelinBrandstofType/{Datum}/{Value}", 'nuclear', Data['nuclear'])
                    Firebase.put(f"/VerzamelinBrandstofType/{Datum}/{Value}", 'water', Data['water'])
                    Firebase.put(f"/VerzamelinBrandstofType/{Datum}/{Value}", 'wind', Data['wind'])
                    Firebase.put(f"/VerzamelinBrandstofType/{Datum}/{Value}", 'other', Data['other'])
                    Firebase.put(f"/VerzamelinBrandstofType/{Datum}/{Value}", 'coal', Data['coal'])

                    break


def ReadPageUrl():
    Scrape_Url = f"https://griddata.elia.be/eliabecontrols.prod/interface/powergeneration/scheduled/generation/oneday/today"
    
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

def GetData(JsonFile, Change, TodayDate):
    GetReportInfo = JsonFile.get('reportInfo')
    GetData = JsonFile.get('data')
    ListData= []
    for Data in GetData:
        ListData.append(
            {
                'Date': Data['date'],
                'liquidFuel': Data['liquidFuel'],
                'naturalGas': Data['naturalGas'],
                'nuclear': Data['nuclear'],
                'water': Data['water'],
                'wind': Data['wind'],
                'other': Data['other'],
                'coal' : Data['coal']
            }
        )
    SendFirebase(ListData,TodayDate,Change)

def ChangeControl(OldJson, NewJson):
    if OldJson == NewJson: 
        return False
    elif OldJson == None:
        return False
    else :
        return True

def main():
    OldJson = None 
    while True: 
        try:
            TodayDate = datetime.date.today()
            XMLPage = ReadPageUrl()
            JsonFormat = ConverToJson(XMLPage)
            Change = ChangeControl(OldJson , JsonFormat)
            # x = JsonFormat.get('reportInfo')
            # y= JsonFormat.get('data')
            # print(x['reportTime'][0:10])
            GetData(JsonFormat, Change, TodayDate)

            time.sleep(900)
            print("Start Over")
            OldJson = JsonFormat

        except Exception as Error:
            print(Error)
    



if __name__ == "__main__":
    main()