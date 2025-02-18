from datetime import datetime, timedelta
import requests
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from functools import partial
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty


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
            if grade['subject'] == sub and float(grade['grade']['mark']['markDisplayValue']) != 0.0:
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
      if float(grade['grade']['mark']['markDisplayValue']) != 0.0 :
        overall[0] += round(float(grade['grade']['mark']['markDisplayValue']),1)
        if round(float(grade['grade']['mark']['markDisplayValue']),1) >= 6.0:
            overall[1] += 1
        else:
            overall[2] += 1
            print(str(grade))
        counter += 1
          
    print(("Notenanzahl: ")+str(counter))
    print(f"({str(overall[1])}/{str(overall[2])})")
    main_average = round(overall[0]/counter,1)
    print("Durchschnitt: "+str(main_average))
    a = averages.items()
    for average in a:
        print(average)

    return str(main_average),str(f"([color=008000]{overall[1]}[/color]/[color=FF0000]{overall[2]}[/color])"),a
    
class Grades(Screen):
    sid = StringProperty()
    pid = StringProperty()
    overall_average = StringProperty("0.0")
    oa_color = ListProperty([0,0,0,1])
    ratio = StringProperty("(0/0)")
    subject = ""
    subjects = ListProperty()
    def to_subject(self, instance,subject):
            transfer1 = self.manager.get_screen('subject')
            transfer1.sid = self.sid
            transfer1.pid = self.pid
            transfer1.subject = subject
            self.manager.current = 'subject'
    def on_pre_enter(self, *args):
        self.overall_average,self.ratio,subjects_raw=get_grades(self.sid,self.pid)
        if float(self.overall_average) >= 6.0:
            self.oa_color = [0, 0.5, 0, 1]
        else:
            self.oa_color = [1,0,0,1]

        print("Overall Average:"+self.overall_average)
        self.subjects = [{'subject': key, 'grade': value} for key, value in subjects_raw]
        print("Länge Liste: "+ str(len(self.subjects)))
        container = self.ids.dynamic_subjects


        for subject in self.subjects:
            button = Button(
                text=f"{subject['subject']}: {subject['grade']}",
                size_hint_y=None,
                height=50,
                width=320,
                on_press= partial(self.to_subject, subject= subject['subject'])
            )
            container.add_widget(button)
    

