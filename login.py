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



class Login(Screen):
    untis_un = StringProperty()
    untis_pw= StringProperty()
    login_btn = ObjectProperty()
    def login(self):
       untis_session_id,person_id = authenticate(self.untis_un,self.untis_pw)
       if (untis_session_id == "None"):
           loginerror = Popup(title= "Error",
                        content= Label(text="Falscher Benutzername oder falsches Passwort!",
                                       font_size = Window.width * 0.04),
                        size_hint=(None,None),size=(Window.width * 0.9,Window.height * 0.3))
           loginerror.open()
       else:
           transfer = self.manager.get_screen('grades')
           transfer.sid = untis_session_id
           transfer.pid = str(person_id)
           self.manager.current='grades'