import pandas as pd

from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.behaviors.compoundselection import CompoundSelectionBehavior
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty
from kivy.vector import Vector
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.textfield import MDTextField
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList

posl = []
labw = []
vol = []
smpn = []

class ScrollViewWidget(FocusBehavior, CompoundSelectionBehavior, ScrollView):

    def __init__(self, **kwargs):
        super(ScrollViewWidget, self).__init__(**kwargs)

        self.ids = {1: 'scroller'}
        self.size = (640, 428)
        self.do_scroll_y = True
        self.scroll_y = 1
        self.add_widget(MDList(background_palette='Pink'))

# Custom label class which uses button behavior.
# Draws the round well buttons and adds the associated functions
class RoundButton(ButtonBehavior, Label):
    background_color = ListProperty((0.5, 0.5, 0.5, 0.5))

    def __init__(self, **kwargs):
        super(RoundButton, self).__init__(**kwargs)
        self.draw()
        self.test = 'test'

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def update_txt(self, str):
        self.text = str

    def get_txt(self):
        return self.text

    def draw(self, *args):
        with self.canvas.before:
            self.shape_color = Color(rgba=(23 / 255, 84 / 255, 150 / 255, 0.5))
            self.shape = Ellipse(pos=self.pos, size=self.size)
            self.bind(pos=self.update_shape, size=self.update_shape)
            self.text = 'Pos'

    def on_background_color(self, *args):
        self.shape_color.rgba = self.background_color

    def on_press(self, *args):
        print(str(self.pos) + ' : ' + str(self.size))
        self.background_color = (1, 0.5, 0, 1)
        posl.append(self.get_txt())

        temp_vol = ''
        temp_labw = ''
        temp_smpn = ''

        pltmap = self.parent
        parent2 = pltmap.parent
        parent3 = parent2.parent

        for child in parent3.children:
            if type(child) == GridLayout:
                x = 0

                for gchild in child.children:
                    if type(gchild) == Spinner:
                        labw.append(gchild.text)
                        temp_labw = gchild.text
                        print('Platen: ' + str(labw))

                    elif type(gchild) == MDTextField and x == 0:
                        smpn.append(gchild.text)
                        temp_smpn = gchild.text
                        print('Sample name: ' + str(smpn))
                        x += 1

                    elif type(gchild) == MDTextField and x == 1:
                        vol.append(gchild.text)
                        temp_vol = gchild.text
                        print('Volume: ' + str(vol))

            if type(child) == ScrollViewWidget:
                sv = child.children
                mdlist = sv[0]
                mdlist.add_widget(TwoLineListItem(text=(str(len(smpn))
                                                  + '. Position: '
                                                  + (self.get_txt())),
                                                  secondary_text=('Sample: '
                                                  + temp_smpn + '  - ''Volume: '
                                                  + temp_vol + '  \u03BCL - '
                                                  'Plate: ' + temp_labw),
                                                  theme_text_color='Custom',
                                                  secondary_theme_text_color='Custom',
                                                  text_color=(1, 1, 1, 1),
                                                  secondary_text_color=(1, 1, 1, 1),
                                                  font_style='H6',
                                                  secondary_font_style='Caption',
                                                  divider='Inset'))

    def collide_point(self, x, y):
        return Vector(x, y).distance(self.center) <= self.width / 2

    pass

# Root widget class creates the 2x2 layout of the application
# Adds each associated widget including the custom PlateMap widget defined below
class RootScreen(FocusBehavior, CompoundSelectionBehavior, GridLayout):

    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)
        self.rows = 2
        self.cols = 2
        self.col_default_width = 640
        self.rows_default_width = 428
        self.col_force_default = True

        Window.size = (1280, 856)

        pltm = PlateMap()
        anhl = AnchorLayout()
        lab = Label()

        lab.text = 'Worklist Generator v1.0 - Sam Burns'

        anhl.add_widget(Image(source='px-96-Well_plate.png'))
        anhl.add_widget(pltm)
        self.add_widget(anhl)
        self.add_widget(lab)

        sv = ScrollViewWidget()
        sl = GridLayout(rows=5, cols=1,
                        row_default_height=45,
                        row_force_default=True,
                        col_default_width=400,
                        col_force_default=True,
                        spacing=[0, 40],
                        padding=[100, 0, 0, 0])

        sl.add_widget(MDTextField(ids={1: 'Vol'},
                                  hint_text='Volume in \u03BCL',
                                  hint_text_color=(1, 1, 1, 1),
                                  text_color=(1, 1, 1, 1),
                                  background_color=(1, 1, 1, 1),
                                  mode='rectangle',
                                  max_text_length=5))

        sl.add_widget(MDTextField(hint_text='Sample Name',
                                  text_color=(1, 1, 1, 1),
                                  background_color=(1, 1, 1, 1),
                                  mode='rectangle'))

        act_button = Button(text='Reset Worklist', size=(50, 33))
        act_button.bind(on_release=self.cleardata)

        gen_button = Button(text='Generate Worklist', size=(50, 33))
        gen_button.bind(on_release=self.gen_wl)

        lt = ['Cos_96', '4titude', 'Greiner_1mL', 'Greiner_2mL']

        spin = Spinner(text='Plate Select',
                       values=(lt),
                       size_hint=(None, None),
                       size=(400, 45))

        def show_select(spin, text):
            print('The spinner', spin, 'has text', text)

        spin.bind(text=show_select)

        sl.add_widget(spin)
        sl.add_widget(act_button)
        sl.add_widget(gen_button)

        self.add_widget(sv)
        self.add_widget(sl)

    def gen_wl(self, *args):
        df = pd.DataFrame({'Position': posl, 'Labware': labw, 'Sample Name': smpn, 'Volume': vol})
        df.to_csv('worklist.csv', index=False)
        print(df)

    def cleardata(self, *args):
        for cld in self.children:
            val = cld.ids
            for k in val.keys():
                if int(k) == 1:
                    gcld = cld.children
                    gcld[0].clear_widgets()

        for gcld in cld.children:
            if type(gcld) == PlateMap:
                print(gcld)
                gcld.canvas.clear()
                gcld.clear_widgets()
                gcld.PopulateButtons()

        posl.clear()
        labw.clear()
        vol.clear()
        smpn.clear()

# This creates the custom plate map layout object. It will insatiate the plate image and
# add the custom RoundButton() label widget to the PlateMap layout
class PlateMap(FocusBehavior, CompoundSelectionBehavior, GridLayout):

    def __init__(self, **kwargs):
        super(PlateMap, self).__init__(**kwargs)
        self.cols = 12
        self.rows = 8
        self.row_default_height = 41
        self.row_force_default = True
        self.col_default_width = 41
        self.col_force_default = True
        self.touch_multiselect = True
        self.multiselect = True
        self.spacing = [4, 4]
        self.padding = [52, 36, 20, 20]

        platepos = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}

        iter = 1

        for x in range(1, 9):
            for i in range(1, 13):
                pp = platepos[x] + str(i)
                rb = RoundButton()
                rb.update_txt(pp)
                self.add_widget(rb)
                iter += 1

    def Pressbtn(self, button):
        for child in self.children:
            if button == child:
                num = self.children.index(child)
                cld = self.children[num]

                with cld.canvas:
                    Color(rgba=(230 / 255, 84 / 255, 150 / 255, 1))

    def ResetButtons(self):
        for child in self.children:
            with child.canvas:
                Color(rgba=(0, 0, 0, 0))

    def PopulateButtons(self):
        platepos = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
        iter = 1

        for x in range(1, 9):
            for i in range(1, 13):
                pp = platepos[x] + str(i)
                rb = RoundButton()
                rb.update_txt(pp)
                self.add_widget(rb)
                iter += 1

# Main class for the application creates the MDKivy application
class PlateApp(MDApp):

    def build(self):
        self.root = root = RootScreen()
        root.bind(size=self._update_rect, pos=self._update_rect)

        with root.canvas.before:
            Color(rgb=(100 / 256, 100 / 256, 100 / 256, 0.2))
            self.rect = Rectangle(size=root.size, pos=root.pos)
        return root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def Pressbtn(self, *args):
        pass

    def ResetButtons(self):
        pass

if __name__ == '__main__':
    PlateApp().run()
