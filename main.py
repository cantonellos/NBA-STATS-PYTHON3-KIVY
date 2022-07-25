
#IMPORTS

from urllib.request import urlopen
import urllib.request
from html_table_parser.parser import HTMLTableParser
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton, MDRectangleFlatIconButton
from kivymd.uix.list import MDList, OneLineListItem, OneLineIconListItem, OneLineAvatarIconListItem
from kivy.uix.scrollview import ScrollView
from functools import partial
from kivy.utils import platform
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivymd.uix.label import MDLabel
import time
from kivymd.uix.dialog import MDDialog
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDFlatButton, MDRoundFlatButton, MDFillRoundFlatButton
from kivy.factory import Factory
from kivymd.theming import ThemeManager
from kivy.metrics import dp
import ssl
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
# dns.resolver.default_resolver=dns.resolver.Resolver(configure=True)
# dns.resolver.default_resolver.nameservers=['8.8.8.8']
import pymongo
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()




# screen manager
class NbaApp(MDApp):
    def build(self):
        self.screen_manager = ScreenManager()

#create home page
        self.HomePage = HomePage()
        screen = Screen(name='Home')
        self.theme_cls.theme_style = "Dark"
        screen.add_widget(self.HomePage)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

#homepage class
class HomePage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
#keep page keeps the team you last vist in case you visit the same again, to have the data stored
        self.keeppage = ''
#buttons for east or west, the one should be pressed as it opens in one of two opened
        self.btnpressed1 = 0
        self.btnpressed = 1

        # button for east
        self.btneast = MDFillRoundFlatButton(text="East",
                                             theme_text_color="Custom",
                                             text_color=(1, 1, 1, 1),
                                             md_bg_color=(1, 0, 0, 1)
                                             )
        self.btneast.bind(on_press=partial(self.east, self.btnpressed))
        self.btneast.pos_hint = {'x': .3, 'y': .9}
        self.btneast.size_hint_x = 0.2
        self.btneast.size_hint_y = 0.1
        self.add_widget(self.btneast)

        # button for west
        self.btnwest = MDFillRoundFlatButton(text="West",
                                             theme_text_color="Custom",
                                             text_color=(0, 0, 0, 1),
                                             md_bg_color=(0, 0, 0, 1)
                                             )
        self.btnwest.bind(on_press=partial(self.west, self.btnpressed1))
        self.btnwest.pos_hint = {'x': .5, 'y': .9}
        self.btnwest.size_hint_x = 0.2
        self.btnwest.size_hint_y = 0.1
        self.add_widget(self.btnwest)

        # it calls grid header and grid for scroll
        self.create_grid()
        self.create_gridlayout()
       #scraping the teams from the database
        self.scrape_teams()

    # Create header of the gridlayout
    def create_grid(self):
        layout = GridLayout(cols=7, spacing=10, size_hint_y=None, pos_hint={'center_x': .5, 'center_y': .85})
        label1 = Label(text="Rk", size_hint_x=0.15, size_hint_y=None)
        label7 = Label(text="", size_hint_y=None, size_hint_x=0.9)
        label2 = Label(text="Team", size_hint_y=None)
        label3 = Label(text="W", size_hint_x=0.3, size_hint_y=None)
        label4 = Label(text="L", size_hint_x=0.3, size_hint_y=None)
        label5 = Label(text="%W", size_hint_y=None)
        label6 = Label(text="", size_hint_y=None)

        layout.add_widget(label1)
        layout.add_widget(label7)
        layout.add_widget(label2)
        layout.add_widget(label6)
        layout.add_widget(label3)
        layout.add_widget(label4)
        layout.add_widget(label5)

        self.add_widget(layout)

#create gridlayout for the teams
    def create_gridlayout(self):
        self.layout = GridLayout(cols=7, spacing=40, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.layout2 = GridLayout(cols=7, spacing=40, size_hint_y=None)
        self.layout2.bind(minimum_height=self.layout2.setter('height'))

        self.scroll = ScrollView()
        self.scroll.size_hint_x = 1.0
        self.scroll.size_hint_y = 0.8
        self.scroll.pos_hint = {'x': .0, 'y': .0}
        self.scroll.add_widget(self.layout)
        self.add_widget(self.scroll)

#get the data from database for teaams
    def scrape_teams(self):
        #connect to database

        client = pymongo.MongoClient(
            #    "mongodb+srv://users:usersall@megglis.oz019.mongodb.net/Teams_db?retryWrites=true&w=majority")
            "mongodb://users:usersall@megglis-shard-00-00.oz019.mongodb.net:27017,megglis-shard-00-01.oz019.mongodb.net:27017,megglis-shard-00-02.oz019.mongodb.net:27017/Teams_db?ssl=true&replicaSet=atlas-zb6fyo-shard-0&authSource=admin&retryWrites=true&w=majority")

    #get the teams db
        db = client.get_database('Teams_db')

        records = db.Teams_records
#get teams and sort by position(the position taken from database)
        for n in range(0, 2):
            if n == 0:
                team = records.find({'region': 'east'}).sort('position', 1)
            else:
                team = records.find({'region': 'west'}).sort('position', 1)
#define icon global because it gonna be needed in another class too
            global icon

            for x in team:
                count = x['position']
                name = x['name']
                label = x['label']
                wins = x['wins']
                loses = x['loses']
                percentage = x['winpercentage']
                threecharacter = x['threecharacter']
                icon = x['icon']

#some adjustments if the platform is android or not
                if platform == 'android':
                    btn = Button(text=f"{count}.", font_size=50, bold=True, size_hint_y=None, size_hint_x=0.25,
                                 height=130,
                                 background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    iconbtn = Button(background_normal=f'{icon}', size_hint_y=None, size_hint_x=None, height=130,
                                     on_press=partial(self.team, threecharacter, icon))

                    btn1 = Button(text=f"{label}", font_size=50, bold=True, size_hint_y=None, height=130,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn2 = Button(text=f"{wins}", font_size=50, bold=True, size_hint_y=None, size_hint_x=0.3,
                                  height=130,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn3 = Button(text=f"{loses}", font_size=50, bold=True, size_hint_y=None, size_hint_x=0.3,
                                  height=130,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn4 = Button(text=f"{percentage}", font_size=50, bold=True, size_hint_y=None, height=130,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn0 = Button(text="", size_hint_y=None, height=130,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))


                else:
                    btn = Button(text=f"{count}.", font_size=22, bold=True, size_hint_y=None, size_hint_x=0.25,
                                 height=40,
                                 background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    iconbtn = Button(background_normal=f'{icon}', size_hint_y=None, size_hint_x=None, height=80,
                                     on_press=partial(self.team, threecharacter, icon))

                    btn1 = Button(text=f"{label}", font_size=22, bold=True, size_hint_y=None, height=40,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn2 = Button(text=f"{wins}", font_size=22, bold=True, size_hint_y=None, size_hint_x=0.3, height=40,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn3 = Button(text=f"{loses}", font_size=22, bold=True, size_hint_y=None, size_hint_x=0.3,
                                  height=40,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn4 = Button(text=f"{percentage}", font_size=22, bold=True, size_hint_y=None, height=40,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))

                    btn0 = Button(text="", size_hint_y=None, height=40,
                                  background_color=(1, 1, 1, 0), on_press=partial(self.team, threecharacter, icon))
               #make the buttons for east and then for west
                if n == 0:
                    self.layout.add_widget(btn)
                    self.layout.add_widget(iconbtn)
                    self.layout.add_widget(btn1)
                    self.layout.add_widget(btn0)
                    self.layout.add_widget(btn2)
                    self.layout.add_widget(btn3)
                    self.layout.add_widget(btn4)

                else:
                    self.layout2.add_widget(btn)
                    self.layout2.add_widget(iconbtn)
                    self.layout2.add_widget(btn1)
                    self.layout2.add_widget(btn0)
                    self.layout2.add_widget(btn2)
                    self.layout2.add_widget(btn3)
                    self.layout2.add_widget(btn4)

    # EAST FUNCTION : CREATE SCROLL WITH EASTERN TEAMS
    def east(self, count, instance):
        self.btneast.md_bg_color = (1, 0, 0, 1)
        self.btnwest.md_bg_color = (0, 0, 0, 1)

        if self.btnpressed == 0:
            self.scroll.remove_widget(self.layout2)
            self.scroll.add_widget(self.layout)
            self.scroll.scroll_y = 1
        self.btnpressed1 = 0
        self.btnpressed = self.btnpressed + 2

    # WEST FUNCTION:CREATE SCROLL WITH WESTERN TEAMS
    def west(self, count, instance):
        self.btnwest.md_bg_color = (1, 0, 0, 1)
        self.btneast.md_bg_color = (0, 0, 0, 1)

        if self.btnpressed1 == 0:
            self.scroll.remove_widget(self.layout)
            self.scroll.add_widget(self.layout2)
            self.scroll.scroll_y = 1

        self.btnpressed = 0
        self.btnpressed1 = self.btnpressed1 + 1

    # CREATE TEAMPAGE
    def team(self, threecharacter, icon1, instance):
        global three
        global icon
        three = threecharacter
        icon = icon1

        # if the pressed team is the same as before, it doesnt destroy the page but it loads instead
        if self.keeppage != threecharacter:
            self.keeppage = threecharacter

            if megg_app.screen_manager.has_screen('TeamPage') == True:

                screen = megg_app.screen_manager.get_screen('TeamPage')
                megg_app.screen_manager.remove_widget(screen)

                self.TeamPage = TeamPage()
                screen = Screen(name='TeamPage')
                screen.add_widget(self.TeamPage)
                megg_app.screen_manager.add_widget(screen)
                megg_app.screen_manager.current = 'TeamPage'

            else:

                self.TeamPage = TeamPage()
                screen = Screen(name='TeamPage')
                screen.add_widget(self.TeamPage)
                megg_app.screen_manager.add_widget(screen)
                megg_app.screen_manager.current = 'TeamPage'

        else:
            megg_app.screen_manager.current = 'TeamPage'


class TeamPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.btn00 = Button(background_normal='backbtn.png', size_hint_y=None, size_hint_x=None, height=80)
        self.btn00.pos_hint = {'x': .9, 'y': .9}
        self.btn00.bind(on_press=self.home)
        #   self.btn00.size_hint_x = 0.2
        #    self.btn00.size_hint_y = 0.2
        self.add_widget(self.btn00)

        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None, pos_hint={'center_x': .5, 'center_y': .85})

        if platform == 'android':
            btn1 = Button(background_normal=f'{icon}', size_hint_y=None, size_hint_x=None, height=120)
        else:
            btn1 = Button(background_normal=f'{icon}', size_hint_y=None, size_hint_x=None, height=80)

        self.layout.add_widget(btn1)
        self.add_widget(self.layout)
        self.edit_data()

    def edit_data(self):
        client = pymongo.MongoClient(
            #    "mongodb+srv://users:usersall@megglis.oz019.mongodb.net/Teams_db?retryWrites=true&w=majority")
            "mongodb://users:usersall@megglis-shard-00-00.oz019.mongodb.net:27017,megglis-shard-00-01.oz019.mongodb.net:27017,megglis-shard-00-02.oz019.mongodb.net:27017/Players_db?ssl=true&replicaSet=atlas-zb6fyo-shard-0&authSource=admin&retryWrites=true&w=majority")

        db = client.get_database('Players_db')

        records = db.Player
        team = records.find({'team': three})
        rows = []
        count = 0

        posx = -0.25
        posy = 0.6
        for x in team:
            count = count + 1
            posx = posx + 0.25

            if posx >= 1.0:
                posy = posy - 0.1

            if posx >= 1.0:
                posx = 0.0

            name = x['name']
            uniformnumber = x['uniformnumber']
            dname = ""
            for y in range(len(name)):
                if name[y] == " ":
                    for s in range(len(name) - (y + 1)):
                        dname = dname + name[y + 1]
                        y = y + 1
                    break

            dname = (name[0] + "." + dname).replace("(TW)", "")
            dname = dname.replace("-", "-\n")
            self.btnx = MDRectangleFlatButton(text=dname)
            self.btnx.pos_hint = {'x': posx, 'y': posy}
            self.btnx.bind(on_press=partial(self.player, name, uniformnumber))
            self.btnx.size_hint_x = 0.25
            self.btnx.size_hint_y = 0.1
            self.add_widget(self.btnx)

    def player(self, name, uniformnumber, instance):
        client = pymongo.MongoClient(
            "mongodb://users:usersall@megglis-shard-00-00.oz019.mongodb.net:27017,megglis-shard-00-01.oz019.mongodb.net:27017,megglis-shard-00-02.oz019.mongodb.net:27017/Players_db?ssl=true&replicaSet=atlas-zb6fyo-shard-0&authSource=admin&retryWrites=true&w=majority")
        db = client.get_database('Players_db')
        records = db.Player
        player = records.find({'name': name})

        if uniformnumber != "":
            for x in player:
                averagepoints = x['averagepoints']
                averagerebounds = x['averagerebounds']
                averageassists = x['averageassists']
            averagepra = "{:.1f}".format((float(averagepoints) + float(averageassists) + float(averagerebounds)))
            titlename = name.replace("(TW)", "")
            self.dialog = MDDialog(title=f"{titlename}",
                                   radius=[20, 7, 20, 7],
                                   text=f"Points:{averagepoints}\nRebounds:{averagerebounds}\nAssists:{averageassists}\nPRA:{averagepra}",
                                   # overlay_color=( 255, 51, 51, 0.8),
                                   md_bg_color=[208 / 255., 29 / 255., 29 / 255., 1.],

                                   buttons=[MDFlatButton(
                                       text="CANCEL",
                                       theme_text_color="Custom",
                                       on_press=self.dclose
                                   )]

                                   )

            self.dialog.open()
        else:
            titlename = name.replace("(TW)", "")
            self.dialog = MDDialog(title=f"{titlename}",
                                   radius=[20, 7, 20, 7],
                                   text="He hasn't play yet",
                                   md_bg_color=[208 / 255., 29 / 255., 29 / 255., 1.],

                                   buttons=[MDFlatButton(
                                       text="CANCEL",
                                       theme_text_color="Custom",
                                       on_press=self.dclose
                                   )]

                                   )
            self.dialog.open()

    def dclose(self, instance):
        self.dialog.dismiss()

    def home(self, instance):
        megg_app.screen_manager.current = 'Home'


if __name__ == "__main__":
    megg_app = NbaApp()
    megg_app.run()