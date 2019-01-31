from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import base64
from requests import request
from pprint import pprint
import  json
import demjson
import os
import time
from datetime import datetime
import socket
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app_id = 'c2867a08b8f741b9bef1900b2c12c55a'
app_key = 'ebQiA77NHGeX_pi-HnWxlmuTU1g'

# 引用私密金鑰
# path/to/serviceAccount.json 請用自己存放的路徑
cred = credentials.Certificate('C:/Users/ECA LAB/serviceAccount.json')

# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(cred)

# 初始化firestore
db = firestore.client()


class Auth():


    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(self.app_key.encode('utf8'), ('x-date: ' + xdate).encode('utf8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = 'hmac username="' + self.app_id + '", ' + \
                        'algorithm="hmac-sha1", ' + \
                        'headers="x-date", ' + \
                        'signature="' + signature + '"'
        return {
            'Authorization': authorization,
            'x-date': format_date_time(mktime(datetime.now().timetuple())),
            'Accept - Encoding': 'gzip'
        }


def internet(host="8.8.8.8", port=53, timeout=3):
      """
      Host: 8.8.8.8 (google-public-dns-a.google.com)
      OpenPort: 53/tcp
      Service: domain (DNS/TCP)
      """
      try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
      except Exception as ex:
        print (ex.message)
        return False


if __name__ == '__main__' :
    while internet() == False :
        time.sleep(2)
    try :
        fp = open("./start.txt","r")
        chk = fp.read()
        fp.close()
        if int(chk) == 1 :
            var = 1
        else :
            var = 0
    except Exception as e :
        fp = open( "./error_message.txt", "a")
        fp.write("Program initialization failed !" + "\n\n")
        fp.write("時間 : %s \n\n" % time.ctime())
        fp.close()
        var = 0
    
    while True :
        error_val_r1 = 0
        error_val_r2 = 0
        a = Auth(app_id, app_key)
        try :
            response01 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeByFrequency/City/NewTaipei/965?$top=50&$select=PlateNumb&$format=JSON', headers= a.get_auth_header())
            decodejson01 =  demjson.decode(response01.content)
        except Exception as e :
            error_val_r1 = 1
            fp = open( "./error_message.txt", "a")
            fp.write("PTX RealTimeByFrequency Error!" + "\n\n")
            fp.write("時間 : %s \n\n" % time.ctime())
            fp.close()
        
        try :
            response02 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeNearStop/City/NewTaipei/965?$top=50&$format=JSON', headers= a.get_auth_header())
            decodejson02 =  demjson.decode(response02.content)
        except Exception as e :
            error_val_r2 = 1
            fp = open( "./error_message.txt", "a")
            fp.write("PTX RealTimeNearStop Error!" + "\n\n")
            fp.write("時間 : %s \n\n" % time.ctime())
            fp.close()

        if error_val_r1 == 1 and error_val_r2 == 1 :
            error_val = 1
        else :
            error_val = 0

        datalist = {}
        write_check = 0

        if error_val_r1 == 0 :
            try :
                for item in decodejson01 :
                    datalist[item['PlateNumb']] = {}
                    datalist[item['PlateNumb']]['PlateNumb'] = item['PlateNumb']                  
                    if item['Direction'] == 0 :
                        datalist[item['PlateNumb']]['Direction'] = '金瓜石'
                    else:
                        datalist[item['PlateNumb']]['Direction'] = '板橋'
                    if item['DutyStatus'] == 0 :
                        datalist[item['PlateNumb']]['DutyStatus'] = '正常'
                    elif item['DutyStatus'] == 1 :
                        datalist[item['PlateNumb']]['DutyStatus'] = '開始'
                    else:
                        datalist[item['PlateNumb']]['DutyStatus'] = '結束'
                    if item['BusStatus'] == 0 :
                        datalist[item['PlateNumb']]['BusStatus'] = '正常'
                    elif item['BusStatus'] == 1 :
                        datalist[item['PlateNumb']]['BusStatus'] = '車禍'
                    elif item['BusStatus'] == 2 :
                        datalist[item['PlateNumb']]['BusStatus'] = '故障'
                    elif item['BusStatus'] == 3 :
                        datalist[item['PlateNumb']]['BusStatus'] = '塞車'
                    elif item['BusStatus'] == 4 :
                        datalist[item['PlateNumb']]['BusStatus'] = '緊急求援'
                    elif item['BusStatus'] == 5 :
                        datalist[item['PlateNumb']]['BusStatus'] = '加油'
                    elif item['BusStatus'] == 90 :
                        datalist[item['PlateNumb']]['BusStatus'] = '不明'
                    elif item['BusStatus'] == 91 :
                        datalist[item['PlateNumb']]['BusStatus'] = '去回不明'
                    elif item['BusStatus'] == 98 :
                        datalist[item['PlateNumb']]['BusStatus'] = '偏移路線'
                    elif item['BusStatus'] == 99 :
                        datalist[item['PlateNumb']]['BusStatus'] = '非營運狀態'
                    elif item['BusStatus'] == 100 :
                        datalist[item['PlateNumb']]['BusStatus'] = '客滿'
                    elif item['BusStatus'] == 101 :
                        datalist[item['PlateNumb']]['BusStatus'] = '包車出租'
                    else :
                        datalist[item['PlateNumb']]['BusStatus'] = '未知'
                    datalist[item['PlateNumb']]['Speed'] = item['Speed']
                    write_check = 1

            except Exception as e :
                error_val = 1
                write_check = 0
                fp = open( "./error_message.txt", "a")
                fp.write("Error Code 1, at item in decodejson01 : " + str(e) + "\n\n")
                fp.write("decodejson01 : " + str(decodejson01) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()
 
        if error_val_r2 == 0 :
            try:
                for item in decodejson02 :
                    if item['PlateNumb'] not in datalist :
                        datalist[item['PlateNumb']] = {}
                        datalist[item['PlateNumb']]['PlateNumb'] = item['PlateNumb']
                        if item['Direction'] == 0 :
                            datalist[item['PlateNumb']]['Direction'] = '金瓜石'
                        else :
                            datalist[item['PlateNumb']]['Direction'] = '板橋'
                    datalist[item['PlateNumb']]['StopName'] = item['StopName']
                    if item['A2EventType'] == 0 :
                        datalist[item['PlateNumb']]['A2EventType'] = '離站'
                    else :
                        datalist[item['PlateNumb']]['A2EventType'] = '進站'
                    write_check = 1

            except Exception as e :
                error_val = 1
                write_check = 0
                fp = open( "./error_message.txt", "a")
                fp.write("Error Code 2, at item in decodejson02 : " + str(e) + "\n\n")
                fp.write("decodejson02 : " + str(decodejson02) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()
                
        if error_val == 0 and write_check == 1 :
            try :
                print("System working!")
                for item in datalist :
                    if 'StopName' in datalist[item] :
                        doc = {
                            '車牌': datalist[item]['PlateNumb'],
                            '開往': datalist[item]['Direction'],
                            '停靠站': datalist[item]['StopName']['Zh_tw'],
                            '進站離站': datalist[item]['A2EventType'],
                            'Date': str(datetime.now().strftime("%Y%m%d")),
                            'Time': str(datetime.now().strftime("%H%M"))
                        }
                    else :
                        doc = {
                            '車牌': datalist[item]['PlateNumb'],
                            '開往': datalist[item]['Direction'],
                            'Date': str(datetime.now().strftime("%Y%m%d")),
                            'Time': str(datetime.now().strftime("%H%M"))
                        }
                    doc_ref = db.collection("965").document(str(datetime.now().strftime("%Y%m%d")))
                    plat_ref = doc_ref.collection(str(datalist[item]['PlateNumb'])).document(str(datetime.now().strftime("%H%M")))
                    plat_ref.set(doc)

            except Exception as e :
                error_val = 1
                write_check = 0
                fp = open( "./error_message.txt", "a")
                fp.write("Error Code 4, at item in datalist : " + str(e) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()
        
        if error_val == 0 :
            try :
                time.sleep( 60 - int(datetime.now().strftime("%S")))
            except Exception as e :
                time.sleep( 50 )
        else :
            time.sleep( 15 )