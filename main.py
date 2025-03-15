import kivy
from grades import Grades
from subject import Subject
from absences import Absences
from datetime import datetime, timedelta
import requests
from kivy.app import App
from login import Login
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

Builder.load_file('classmate.kv')
Window.size = (400, 807)



class StartApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Login(name='login'))
        sm.add_widget(Grades(name='grades'))
        sm.add_widget(Absences(name='absences'))
        sm.add_widget(Subject(name='subject'))
        return sm

if __name__ == "__main__":
    StartApp().run()




#
#    get_grades = requests.get(f"https://mese.webuntis.com/WebUntis/api/classreg/grade/gradeList?personId={person_id}&startDate=20240905&endDate=20241112", cookies=cookies1, headers=headers)
#    print(get_grades.status_code)
#    grades = get_grades.json()
#    print(grades)
