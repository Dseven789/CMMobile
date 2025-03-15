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

#Window.size = (400,600)

def get_subject_grades(sid,pid,subject):
    headers = {'Content-Type': 'application/json'}
    cookies =  {'JSESSIONID' : sid}
    date = datetime.today() 
    year = (datetime.now()).strftime('%Y')
    year_to_test = int(year)
    test_date = datetime(year_to_test,9,5)
    mark = 0
    exams = []
    counter = 0
    if date < test_date:
         date = (datetime.now()).strftime('%Y%m%d')
         year = (datetime.now() - timedelta(days= 365)).strftime('%Y')
    else:
        year = (datetime.now()).strftime('%Y')
    get_grades = requests.get(f"https://mese.webuntis.com/WebUntis/api/classreg/grade/gradeList?personId={int(pid)}&startDate={str(year)}0905&endDate={str(date)}", cookies=cookies, headers=headers)
    grades_unformatted = get_grades.json()
    for grade in grades_unformatted['data']:
        if subject == grade['subject'] and float(grade['grade']['mark']['markDisplayValue']) != 0.0:
            mark += float(grade['grade']['mark']['markDisplayValue'])
            counter+= 1
            exams.append(grade)
    if counter != 0:
        mark = round(mark/counter,2)
        if float(mark) >= 6.0:
            oa_color = [0, 0.5, 0, 1]
        else:
            oa_color = [1,0,0,1]
        print(exams)
    else:
        oa_color = [0, 0.5, 0, 1] 
    return str(mark),oa_color,exams
        

class Subject(Screen):  
    sid = StringProperty()
    pid = StringProperty()
    subject = StringProperty()
    main_mark = StringProperty("0.0")
    oa_color = ListProperty([0,0,0,0])
    def on_pre_enter(self, *args):
        self.main_mark,self.oa_color,exams = get_subject_grades(self.sid,self.pid,self.subject)
        container = self.ids.dynamic_exams
        for exam in exams:
            unformatted_date = str(exam['grade']['date'])
            date = datetime.strptime(unformatted_date, '%Y%m%d')
            if float(exam['grade']['mark']['markDisplayValue']) >= 6.0:
                grade = f"[color=008000]{str(exam['grade']['mark']['markDisplayValue'])}[/color]"
            else:
                grade = f"[color=FF0000]{str(exam['grade']['mark']['markDisplayValue'])}[/color]"
            size1 = Window.width * 0.05
            if exam['grade']['text'] == '':
                exam_name = exam['grade']['examType']['name']
            else:
                exam_name = exam['grade']['text']
            if len(exam_name) <= 43:
                size2 = Window.width * 0.03
            elif len(exam_name) <= 62:
                size2 = Window.width * 0.03
            elif len(exam_name) <= 72:
                size2 = Window.width * 0.03
            else:
                size2 = Window.width * 0.03

            button = Button(
                text=f"[size={int(size1)}][color=FFFFFF]{str(date.strftime('%d.%m.%Y'))}"+" : [/color]"+grade+ "[/size]\n" +f"[size={int(size2)}][color=FFFFFF]{str(exam_name)}[/color][/size]",
                size_hint_y=None,
                height=92,
                markup = True,
                halign = "left",
                valign = "middle",
                background_color=( 0.894, 0.424, 0.008, 1),
                background_normal= "",
                width=322
            )
            button.text_size = (button.width - 20, None)  # Begrenze den Textbereich
            button.halign = "left"  # Setzt den Text linksbündig
            container.add_widget(button)
    

        
    def to_grades(self):
        transfer = self.manager.get_screen('grades')
        transfer.sid = self.sid
        transfer.pid = str(self.pid)
        container = self.ids.dynamic_exams
        container.clear_widgets()
        self.manager.current='grades'
    
    def logout(self):
        container = self.ids.dynamic_exams
        container.clear_widgets()
        self.manager.current= 'login'