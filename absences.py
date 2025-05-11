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

def get_hours(pid,sid):
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
    hours_raw = requests.get(f"https://mese.webuntis.com/WebUntis/api/classreg/absencetimes/student?startDate={str(year)}0905&endDate={str(date)}&studentId={int(pid)}&excuseStatusId=-1&excludeAbsences=false&excludeLateness=false",cookies=cookies,headers=headers)
    hours = hours_raw.json()
    absences = []
    excused = 0
    missing_hours = 0
    unexcused = 0
    for absence in hours['data']['absences']:
        absences.append(absence)
        if absence['isExcused'] is True:
            excused += 1
        else:
            unexcused +=1
    for mh in hours['data']['absenceTimes']:
        missing_hours += int(mh['missedHours'])
    print(len(absences))
    print(f"Fehlstunden: {str(missing_hours)}")
    print(f"{str(excused)} / {str(unexcused)}")
    return excused,unexcused,absences,f"Fehlstunden: {str(missing_hours)}"


class Absences(Screen):
    sid = StringProperty()
    pid = StringProperty()
    overall_absences = StringProperty()
    missing_hours = StringProperty()

    def on_pre_enter(self, *args):
        excused,unexcused,absences,self.missing_hours = get_hours(self.pid,self.sid)
        self.overall_absences =f"([color=80FF00]{str(excused)}[/color][color=FFFFFF]/[/color][color=FF3333]{str(unexcused)}[/color])"
        for absence in absences:
            unformatted_start_date = str(absence['startDate'])
            unformatted_end_date = str(absence ['endDate'])
            unformatted_start_time = str(absence['startTime'])
            unformatted_end_time = str(absence['endTime'])
            container = self.ids.dynamic_absences
            excuse_color = ""
            absence_time = ""
            start_date = datetime.strptime(unformatted_start_date,'%Y%m%d')
            end_date = datetime.strptime(unformatted_end_date,'%Y%m%d')
            start_time = datetime.strptime(unformatted_start_time,'%H%M')
            end_time = datetime.strptime(unformatted_end_time,'%H%M')
            main_size = Window.width * 0.045
            second_size = Window.width* 0.035
            if absence['isExcused'] is True:
                excuse_color = '80FF00'
            else:
                excuse_color = 'C62828'
            if end_date != start_date:
                absence_time = f"{str(start_date.strftime('%d.%m.%Y'))}: {str(start_time.strftime('%H:%M'))} - {str(end_time.strftime('%H:%M'))}"
            
            else:
                absence_time = f"{str(start_date.strftime('%d.%m'))}: {str(start_time.strftime('%H:%M'))} - {str(end_date.strftime('%d.%m.%Y'))} : {str(end_time.strftime('%H:%M'))}"
   
            button = Button(
                text = f"[size={int(main_size)}][color={excuse_color}]{absence_time}[/color][/size]\n[size={int(second_size)}][color=FFFFFF]{str(absence['text'])}[/color][/size]",
                size_hint_y=None,
                height= Window.height * 0.15,
                markup = True,
                halign = "left",
                valign = "middle",
                background_color=( 0.894, 0.424, 0.008, 1),
                background_normal= "",
                width= Window.width * 0.9
            )
            button.text_size = (button.width - Window.width * 0.01, None)  # Begrenze den Textbereich
            button.halign = "left"
            container.add_widget(button)
            


    def to_grades(self):
        transfer = self.manager.get_screen('grades')
        transfer.sid = self.sid
        transfer.pid = str(self.pid)
        container = self.ids.dynamic_absences
        container.clear_widgets()
        self.manager.current='grades'
    
    def logout(self):
        container = self.ids.dynamic_absences
        container.clear_widgets()
        self.manager.current= 'login'
