import json
import argparse
import requests_html
from requests_html import requests
from datetime import datetime, timedelta

def formatMsg(tdelta, msg):
    d = {'days': tdelta.days}
    d['hours'], rem = divmod(tdelta.seconds, 3600)
    d['minutes'], d['seconds'] = divmod(rem, 60)

    if d['days'] > 0:
        msg = msg + str(d['days']) + ' days '
    if d['hours'] > 0:
        msg = msg + str(d['hours']) + ' hours '
    if d['minutes'] > 0:
        msg = msg + str(d['minutes']) + ' minutes '
    if d['seconds'] > 0:
        msg = msg + str(d['seconds']) + ' seconds'

    return msg

def getParams():
    session = requests_html.HTMLSession()
    res = session.get('https://cebcare.ceb.lk/Incognito/OutageMap')
    elements  = res.html.find('#map_canvas > form > input[type=hidden]')

    cookiesDict = {}
    token = elements[0].attrs['value']
    headers = {'RequestVerificationToken': token}

    for cookie in res.cookies:
        cookiesDict[cookie.name] = cookie.value

    return cookiesDict, headers

def request(accNo):
    url = 'https://cebcare.ceb.lk/Incognito/GetCalendarData?from={0}&to={1}&acctNo={2}'
    cookies, headers = getParams()
    today = datetime.today().strftime('%Y-%m-%d')
    days3 = (datetime.today() + timedelta(days=3)).strftime('%Y-%m-%d')

    return requests.get(url.format(today, days3, accNo), cookies = cookies, headers = headers)

def printInfo(res_json):
    interruptions = res_json['interruptions']
    
    count = 0
    for interruption in interruptions:
        if interruption['status'] == 'Active' or interruption['status'] == 'Upcoming':
            if count > 0:
                print()
                
            dtStart = datetime.strptime(interruption['startTime'], '%Y-%m-%dT%H:%M:%S')
            dtEnd = datetime.strptime(interruption['endTime'], '%Y-%m-%dT%H:%M:%S')

            print(interruption['interruptionTypeName'])
            print('From:',dtStart.strftime('%Y-%m-%d %I:%M:%S %p'),'To:', dtEnd.strftime('%Y-%m-%d %I:%M:%S %p'))
            print('Status:', interruption['status'])

            if(interruption['status'] == 'Active'):
                print(formatMsg(dtEnd - datetime.now(), 'Power will be back in '))
            else:
                print(formatMsg(dtEnd - datetime.now(), 'Next power cut in '))
            
            count = count + 1

    if count < 1:
        print('No data available')
    
def main():
    parser = argparse.ArgumentParser(description='CEB Power Cut Schedule')
    parser.add_argument('-a', '--account', required=True, action="store", dest='acc', default=0, help='specify the CEB account number')
    args = parser.parse_args()

    res = request(args.acc)
    
    if res.ok:
        printInfo(res.json())

if __name__ == "__main__":
    main()
