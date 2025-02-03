import kivy
from datetime import datetime, timedelta
import requests
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty

base_url = 'https://mese.webuntis.com/WebUntis/jsonrpc.do?school=lbs-brixen'

def authenticate(username,password):
    try:
        headers = {'Content-Type': 'application/json'}

        data = {
            "id": "1",
            "method": "authenticate",
            "params": {
                "user": f"{username}",
                "password": f"{password}",
                "client": "classmate-mobile"
            },
            "jsonrpc": "2.0"
        }

        
        response = requests.post(base_url, json=data, headers=headers)

        
        if response.status_code == 200:
            json = response.json()
            print(json)
            session_id = response.cookies['JSESSIONID']
            person_id = json['result']['personId']
            print(f"ID: {person_id}")
            print(f'Erfolgreich angemeldet! Session ID: {session_id}')
        else:
            print('Login fehlgeschlagen:', response.json())


        cookies = {'JSESSIONID' : session_id}

        get_api_token = requests.get("https://mese.webuntis.com/WebUntis/api/token/new", cookies=cookies, headers=headers)

        if get_api_token.status_code == 200:
            print(get_api_token.headers)
            api_token= get_api_token.text
            print(f"API-Token:{api_token}")

        else:
            print("API-Token Request FAILED")
        
        return session_id,person_id
    except: 
        return "None","None"

Window.size = (400,600)

class Login(Screen):
    untis_un = StringProperty()
    untis_pw= StringProperty()
    login_btn = ObjectProperty()
    def login(self):
       untis_session_id,person_id = authenticate(self.untis_un,self.untis_pw)
       if (untis_session_id == "None"):
           loginerror = Popup(title= "Error",
                        content= Label(text="Falscher Benutzername oder falsches Passwort!"),
                        size_hint=(None,None),size=(420,180))
           loginerror.open()
       else:
           transfer = self.manager.get_screen('grades')
           transfer.sid = untis_session_id
           transfer.pid = str(person_id)
           self.manager.current='grades'
      
           
     
def get_grades(sid,pid):
    headers = {'Content-Type': 'application/json'}
    cookies =  {'JSESSIONID' : sid}
    date = datetime.today() 
    year = (datetime.now()).strftime('%Y')
    year_to_test = int(year)
    test_date = datetime(year_to_test,9,5)
    if date < test_date:
         date = (datetime.now()).strftime('%Y%m%d')
         year = (datetime.now() - timedelta(days= 365)).strftime('%Y')
    else:
        year = (datetime.now()).strftime('%Y')
    subjects_raw = requests.get(f"https://mese.webuntis.com/WebUntis/api/classreg/grade/grading/list?studentId={int(pid)}&schoolyearId=22",cookies=cookies,headers=headers)
    get_grades = requests.get(f"https://mese.webuntis.com/WebUntis/api/classreg/grade/gradeList?personId={int(pid)}&startDate={str(year)}0905&endDate={str(date)}", cookies=cookies, headers=headers)
    grades_unformatted = get_grades.json()
    subjects_json = subjects_raw.json()
    subjects = []
    averages = {}
    for subject in subjects_json['data']['lessons']:
        if subject['subjects'] != "":
            subjects.append(subject['subjects'])

    for sub in subjects:
        mark = 0
        mark_count = 0
        for grade in grades_unformatted['data']:
            if grade['subject'] == sub:
                mark += float(grade['grade']['mark']['markDisplayValue'])
                mark_count += 1

        if mark_count == 0:
            averages[sub] = 0
        else:
            mark = round(mark / mark_count,1)
            averages[sub] = mark
    
    
    counter = 0
    overall = [0,0,0]
    for grade in grades_unformatted['data']:
      overall[0] += round(float(grade['grade']['mark']['markDisplayValue']),1)
      if round(float(grade['grade']['mark']['markDisplayValue']),1) >= 6.0:
          overall[1] += 1
      else:
          overall[2] += 1
      counter += 1
          
    print(("Notenanzahl: ")+str(counter))
    print(f"({str(overall[1])}/{str(overall[2])})")
    main_average = round(overall[0]/counter,1)
    print("Durchschnitt: "+str(main_average))
    a = averages.items()
    for average in a:
        print(average)

    return str(main_average),str(f"([color=008000]{overall[1]}[/color]/[color=FF0000]{overall[2]}[/color])"),a
    

class absences(Screen):
    pass



class grades(Screen):
    sid = StringProperty()
    pid = StringProperty()
    overall_average = StringProperty("0.0")
    oa_color = ListProperty([0,0,0,1])
    ratio = StringProperty("(0/0)")
    subjects = ListProperty()
    def on_pre_enter(self, *args):
        self.overall_average,self.ratio,subjects_raw=get_grades(self.sid,self.pid)
        if float(self.overall_average) >= 6.0:
            self.oa_color = [0, 0.5, 0, 1]
        else:
            self.oa_color = [1,0,0,1]

        print("Overall Average:"+self.overall_average)
        self.subjects = [{'subject': key, 'grade': value} for key, value in subjects_raw]
        container = self.ids.dynamic_subjects

        for subject in self.subjects:
            button = Button(
                text=f"{subject['subject']}: {subject['grade']}",
                size_hint_y=None,
                height=50,
                width=320
            )
            container.add_widget(button)


class StartApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Login(name='login'))
        sm.add_widget(grades(name='grades'))
        sm.add_widget(absences(name='absences'))
        return sm

if __name__ == "__main__":
    StartApp().run()




#
#    get_grades = requests.get(f"https://mese.webuntis.com/WebUntis/api/classreg/grade/gradeList?personId={person_id}&startDate=20240905&endDate=20241112", cookies=cookies1, headers=headers)
#    print(get_grades.status_code)
#    grades = get_grades.json()
#    print(grades)
