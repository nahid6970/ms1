import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import os
from os.path import exists
from os.path import expanduser
from pathlib import Path

import shutil
import subprocess

home = expanduser("~")
user = os.getlogin()
source = "/usr/share/applications/dtos-hub.desktop"
dest = home + "/.config/autostart/dtos-hub.desktop"
settings = home + "/.config/dtos-hub/settings.conf"

def shell_exists(shell):
    if Path(f"/bin/{shell}").is_file():
        return f"{shell} exists."
    else:
        return f"{shell} is not found."

print(shell_exists('bash'))
print(shell_exists('fish'))
print(shell_exists('zsh'))

class MyWindow1(Gtk.Window):
    def __init__(self):
        super().__init__(title="DTOS Hub")

        self.set_border_width(10)
        self.set_default_size(640, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        frame1 = Gtk.Frame(label="DTOS Hub")

        grid1 = Gtk.Grid(row_spacing    = 10,
                         column_spacing = 10,
                         column_homogeneous = True)

        image1 = Gtk.Image()
        image1.set_from_file("/home/dt/nc/Org/test/python-app/image1.png")

        # This worked but had deprecation warnings!
        # label1 = Gtk.Label("Welcome to DTOS! Need help using DTOS or customizing it?")
        label1 = Gtk.Label(label="Welcome to DTOS! Need help using DTOS or customizing it?")
        label1.set_hexpand(True)

        label2 = Gtk.Label(label="Or maybe you just want to learn more about Linux? We've got you covered.")
        label2.set_hexpand(True)

        label3 = Gtk.Label()
        label4 = Gtk.Label()

        button1 = Gtk.Button(label="About DTOS")
        button1.set_hexpand(True)
        button1.connect("clicked", self.on_button1_clicked)

        button2 = Gtk.Button(label="Knowledge Base")
        button2.set_hexpand(True)
        button2.connect("clicked", self.on_button2_clicked)

        button3 = Gtk.Button(label="Video Tutorials")
        button3.set_hexpand(True)
        button3.connect("clicked", self.on_button3_clicked)

        button4 = Gtk.Button(label="Contribute")
        button4.set_hexpand(True)
        button4.connect("clicked", self.on_button4_clicked)

        button5 = Gtk.Button(label="Change Shell")
        button5.set_hexpand(True)
        button5.connect("clicked", self.on_button5_clicked)

        button6 = Gtk.Button(label="Change Color Scheme")
        button6.set_hexpand(True)
        button6.connect("clicked", self.on_button6_clicked)

        button7 = Gtk.Button(label="Exit")
        button7.set_hexpand(True)
        button7.connect("clicked", Gtk.main_quit)

        check = Gtk.CheckButton(label="Autostart")
        check.connect("toggled", self.startup_toggle)
        check.set_active(eval(self.load_settings()))

        grid1.attach(image1,  0, 0, 3, 2)
        grid1.attach(label1,  0, 2, 3, 2)
        grid1.attach(label2,  0, 4, 3, 2)
        grid1.attach(label3,  0, 6, 3, 1)
        grid1.attach(button1, 0, 7, 1, 1)
        grid1.attach(button2, 1, 7, 1, 1)
        grid1.attach(button3, 2, 7, 1, 1)
        grid1.attach(button4, 0, 8, 1, 1)
        grid1.attach(button5, 1, 8, 1, 1)
        grid1.attach(button6, 2, 8, 1, 1)
        grid1.attach(button7, 1, 9, 1, 1)
        grid1.attach(label4,  0, 10, 3, 1)
        grid1.attach(check,   2, 11, 1, 1)

        self.add(frame1)
        frame1.add(grid1)

    def on_button1_clicked(self, widget):
        print("User chose: About DTOS")
        subprocess.run(["xdg-open", "https://distro.tube/dtos/"])

    def on_button2_clicked(self, widget):
        print("User chose: Knowledge Base")
        subprocess.run(["xdg-open", "https://distro.tube/kb/"])

    def on_button3_clicked(self, widget):
        print("User chose: Video Tutorials")
        win1.hide()
        win2.show_all()

    def on_button4_clicked(self, widget):
        print("User chose: Contribute")
        subprocess.run(["xdg-open", "https://distro.tube/contribute/"])

    def on_button5_clicked(self, widget):
        print("User chose: Change Shell")
        win1.hide()
        win3.show_all()

    def on_button6_clicked(self, widget):
        print("User chose: Change Color Scheme")
        win1.hide()
        win4.show_all()

    def on_button7_clicked(self, widget):
        print("User chose: Exit")

    def save_settings(self, state):
        with open(settings, "w") as f:
            f.write("autostart=" + str(state))
            f.close()

    def load_settings(self):
        line = "True"
        if os.path.isfile(settings):
            with open(settings, "r") as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    if "autostart" in lines[i]:
                        line = lines[i].split("=")[1].strip().capitalize()
                f.close()
        return line

    def startup_toggle(self, widget):
        if widget.get_active() is True:
            if os.path.isfile(source):
                shutil.copy(source, dest)
        else:
            if os.path.isfile(dest):
                os.unlink(dest)
        self.save_settings(widget.get_active())

class MyWindow2(Gtk.Window):
    def __init__(self):
        super().__init__(title="DTOS Hub: Video Tutorials")

        self.set_border_width(10)
        self.set_default_size(640, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        frame2 = Gtk.Frame(label="Video Tutorials")

        grid2 = Gtk.Grid(row_spacing    = 10,
                         column_spacing = 10,
                         column_homogeneous = True)

        image1 = Gtk.Image()
        image1.set_from_file("/home/dt/nc/Org/test/python-app/image1.png")

        label1 = Gtk.Label(label="Video tutorials are organized into playlists by topic.")
        label1.set_hexpand(True)

        label2 = Gtk.Label()
        label3 = Gtk.Label()

        button8 = Gtk.Button(label="Arch Linux")
        button8.set_hexpand(True)
        button8.connect("clicked", self.on_button8_clicked)

        button9 = Gtk.Button(label="Command Line")
        button9.set_hexpand(True)
        button9.connect("clicked", self.on_button9_clicked)

        button10 = Gtk.Button(label="Customization")
        button10.set_hexpand(True)
        button10.connect("clicked", self.on_button10_clicked)

        button11 = Gtk.Button(label="Dmscripts")
        button11.set_hexpand(True)
        button11.connect("clicked", self.on_button11_clicked)

        button12 = Gtk.Button(label="Doom Emacs")
        button12.set_hexpand(True)
        button12.connect("clicked", self.on_button12_clicked)

        button13 = Gtk.Button(label="FOSS Games")
        button13.set_hexpand(True)
        button13.connect("clicked", self.on_button13_clicked)

        button14 = Gtk.Button(label="GUI Apps")
        button14.set_hexpand(True)
        button14.connect("clicked", self.on_button14_clicked)

        button15 = Gtk.Button(label="Haskell")
        button15.set_hexpand(True)
        button15.connect("clicked", self.on_button15_clicked)

        button16 = Gtk.Button(label="Shell Scripting")
        button16.set_hexpand(True)
        button16.connect("clicked", self.on_button16_clicked)

        button17 = Gtk.Button(label="Vim")
        button17.set_hexpand(True)
        button17.connect("clicked", self.on_button17_clicked)

        button18 = Gtk.Button(label="Virtual Machines")
        button18.set_hexpand(True)
        button18.connect("clicked", self.on_button18_clicked)

        button19 = Gtk.Button(label="XMonad")
        button19.set_hexpand(True)
        button19.connect("clicked", self.on_button19_clicked)

        button20 = Gtk.Button(label="Back To Main Menu")
        button20.set_hexpand(True)
        button20.connect("clicked", self.on_button20_clicked)

        button21 = Gtk.Button(label="Exit")
        button21.set_hexpand(True)
        button21.connect("clicked", Gtk.main_quit)

        grid2.attach(image1,   0, 0, 4, 2)
        grid2.attach(label1,   0, 2, 4, 2)
        grid2.attach(label2,   0, 4, 4, 2)
        grid2.attach(button8,  0, 6, 1, 1)
        grid2.attach(button9,  1, 6, 1, 1)
        grid2.attach(button10, 2, 6, 1, 1)
        grid2.attach(button11, 3, 6, 1, 1)
        grid2.attach(button12, 0, 7, 1, 1)
        grid2.attach(button13, 1, 7, 1, 1)
        grid2.attach(button14, 2, 7, 1, 1)
        grid2.attach(button15, 3, 7, 1, 1)
        grid2.attach(button16, 0, 8, 1, 1)
        grid2.attach(button17, 1, 8, 1, 1)
        grid2.attach(button18, 2, 8, 1, 1)
        grid2.attach(button19, 3, 8, 1, 1)
        grid2.attach(label3,   0, 9, 4, 1)
        grid2.attach(button20, 0, 10, 2, 1)
        grid2.attach(button21, 2, 10, 2, 1)

        self.add(frame2)
        frame2.add(grid2)

    def on_button8_clicked(self, widget):
        print("Video Tutorials: Arch Linux")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku16Ncr9H_BAZSzWecjaSWlvY"])

    def on_button9_clicked(self, widget):
        print("Video Tutorials: Command Line")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku174EnRTbP4DzU2W80Q1vqtm"])

    def on_button10_clicked(self, widget):
        print("Video Tutorials: Customization")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku161_sqWcKCc2USL4LcSJ_kq"])

    def on_button11_clicked(self, widget):
        print("Video Tutorials: Dmscripts")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku15ur-I5LiVnBacrKD29Lv1-"])

    def on_button12_clicked(self, widget):
        print("Video Tutorials: Doom Emacs")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku15uYCnmxWPO17Dq6hVabAB4"])

    def on_button13_clicked(self, widget):
        print("Video Tutorials: FOSS Games")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku15eRaNDc1kFgHVQOgzKjife"])

    def on_button14_clicked(self, widget):
        print("Video Tutorials: GUI Apps")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku14oJ3sn9D5zpvSLVG0y2Nss"])

    def on_button15_clicked(self, widget):
        print("Video Tutorials: Haskell")
        subprocess.run(["xdg-open", "https://www.youtube.com/watch?v=fJRBeWwdby8"])

    def on_button16_clicked(self, widget):
        print("Video Tutorials: Shell Scripting")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku15YdkGmHjW2A31oPaQ5pEUw"])

    def on_button17_clicked(self, widget):
        print("Video Tutorials: Vim")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku15tivUyt0D-mERePLEzrWUz"])

    def on_button18_clicked(self, widget):
        print("Video Tutorials: Virtual Machines")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku16N_IpNYzdWTNogpoe1O3TC"])

    def on_button19_clicked(self, widget):
        print("Video Tutorials: Xmonad")
        subprocess.run(["xdg-open", "https://www.youtube.com/playlist?list=PL5--8gKSku144jIsizdhdxq_fKTmBBGBA"])

    def on_button20_clicked(self, widget):
        print("Back To Main Menu")
        win2.hide()
        win1.show_all()

    def on_button21_clicked(self, widget):
        print("Exit")
        button21.connect("clicked", Gtk.main_quit)

class MyWindow3(Gtk.Window):
    def __init__(self):
        super().__init__(title="DTOS Hub: Change " + user + "'s Shell")

        self.set_border_width(10)
        self.set_default_size(640, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        frame3 = Gtk.Frame(label="Change " + user + "'s Shell")

        grid3 = Gtk.Grid(row_spacing    = 10,
                         column_spacing = 10,
                         column_homogeneous = True)

        image1 = Gtk.Image()
        image1.set_from_file("/home/dt/nc/Org/test/python-app/image1.png")

        label1 = Gtk.Label(label="Change " + user + "'s default shell.")
        label1.set_hexpand(True)

        label2 = Gtk.Label()
        label3 = Gtk.Label()

        shellBtn0 = Gtk.RadioButton(label="Don't change")
        shellBtn0.connect("clicked", self.on_toggled, "'Don't change'", "No shell selected.")

        shellBtn1 = Gtk.RadioButton.new_with_label_from_widget(shellBtn0, label="Bash")
        shellBtn1.connect("clicked", self.on_toggled, "Bash", "/bin/bash")

        shellBtn2 = Gtk.RadioButton.new_with_label_from_widget(shellBtn1, label="Fish")
        shellBtn2.connect("clicked", self.on_toggled, "Fish", "/bin/fish")

        shellBtn3 = Gtk.RadioButton.new_with_label_from_widget(shellBtn2, label="Zsh")
        shellBtn3.connect("clicked", self.on_toggled, "Zsh", "/bin/zsh")

        shellBtn4 = Gtk.Button(label="Back To Main Menu")
        shellBtn4.set_hexpand(True)
        shellBtn4.connect("clicked", self.on_shellBtn4_clicked)

        shellBtn5 = Gtk.Button(label="Exit")
        shellBtn5.set_hexpand(True)
        shellBtn5.connect("clicked", Gtk.main_quit)


        grid3.attach(image1,    0, 0, 4, 2)
        grid3.attach(label1,    0, 2, 4, 2)
        grid3.attach(label2,    0, 4, 4, 2)
        grid3.attach(shellBtn0, 0, 6, 1, 1)
        grid3.attach(shellBtn1, 1, 6, 1, 1)
        grid3.attach(shellBtn2, 2, 6, 1, 1)
        grid3.attach(shellBtn3, 3, 6, 1, 1)
        grid3.attach(label3,    0, 7, 3, 1)
        grid3.attach(shellBtn4, 0, 8, 2, 1)
        grid3.attach(shellBtn5, 2, 8, 2, 1)

        self.add(frame3)
        frame3.add(grid3)

    def on_toggled(self, button, name, shell):
        if button.get_active():
            state = "on"

            if shell == "/bin/bash":
               print ("Setting bash as", user, "'s shell")
               if Path(bash_exists).is_file():
                  print(f'/bin/bash exists.')
                  subprocess.run(["pkexec", "chsh", user, "-s", "/bin/bash"])
               else:
                  print(shell, "is not installed.")

            if shell == "/bin/fish":
               print ("Setting fish as", user, "'s shell")
               if Path(fish_exists).is_file():
                  print(f'/bin/fish exists.')
                  subprocess.run(["pkexec", "chsh", user, "-s", "/bin/fish"])
               else:
                  print(shell, "is not installed.")

            if shell == "/bin/zsh":
               print ("Setting zsh as", user, "'s shell")
               if Path(zsh_exists).is_file():
                  print(f'/bin/zsh exists.')
                  subprocess.run(["pkexec", "chsh", user, "-s", "/bin/zsh"])
               else:
                  print(shell, "is not installed.")
        else:
            print("Button", name, "was turned", state)

    def on_shellBtn4_clicked(self, widget):
        print("Back To Main Menu")
        win3.hide()
        win1.show_all()

class MyWindow4(Gtk.Window):
    def __init__(self):
        super().__init__(title="DTOS Hub: Change Color Scheme")

        self.set_border_width(10)
        self.set_default_size(640, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        frame4 = Gtk.Frame(label="Change Color Scheme")

        grid4 = Gtk.Grid(row_spacing    = 10,
                         column_spacing = 10,
                         column_homogeneous = True)

        image1 = Gtk.Image()
        image1.set_from_file("/home/dt/nc/Org/test/python-app/image1.png")

        label1 = Gtk.Label(label="Change " + user + "'s default shell.")
        label1.set_hexpand(True)

        label2 = Gtk.Label()
        label3 = Gtk.Label()

        colorBtn0 = Gtk.RadioButton(label="Don't change")
        colorBtn0.connect("clicked", self.on_clicked, "Don't change")

        colorBtn1 = Gtk.RadioButton.new_with_label_from_widget(colorBtn0, label="DoomOne")
        colorBtn1.connect("clicked", self.on_clicked, "DoomOne")

        colorBtn2 = Gtk.RadioButton.new_with_label_from_widget(colorBtn1, label="Dracula")
        colorBtn2.connect("clicked", self.on_clicked, "Dracula")

        colorBtn3 = Gtk.RadioButton.new_with_label_from_widget(colorBtn2, label="GruvboxDark")
        colorBtn3.connect("clicked", self.on_clicked, "GruvboxDark")

        colorBtn4 = Gtk.RadioButton.new_with_label_from_widget(colorBtn3, label="MonokaiPro")
        colorBtn4.connect("clicked", self.on_clicked, "MonokaiPro")

        colorBtn5 = Gtk.RadioButton.new_with_label_from_widget(colorBtn4, label="Nord")
        colorBtn5.connect("clicked", self.on_clicked, "Nord")

        colorBtn6 = Gtk.RadioButton.new_with_label_from_widget(colorBtn5, label="OceanicNext")
        colorBtn6.connect("clicked", self.on_clicked,"OceanicNext")

        colorBtn7 = Gtk.RadioButton.new_with_label_from_widget(colorBtn6, label="Palenight")
        colorBtn7.connect("clicked", self.on_clicked, "Palenight")

        colorBtn8 = Gtk.RadioButton.new_with_label_from_widget(colorBtn7, label="SolarizedDark")
        colorBtn8.connect("clicked", self.on_clicked, "SolarizedDark")

        colorBtn9 = Gtk.RadioButton.new_with_label_from_widget(colorBtn8, label="SolarizedLight")
        colorBtn9.connect("clicked", self.on_clicked, "SolarizedLight")

        colorBtn10 = Gtk.RadioButton.new_with_label_from_widget(colorBtn9, label="TomorrowNight")
        colorBtn10.connect("clicked", self.on_clicked, "TomorrowNight")

        colorBtn12 = Gtk.Button(label="Back To Main Menu")
        colorBtn12.set_hexpand(True)
        colorBtn12.connect("clicked", self.on_colorBtn12_clicked)

        colorBtn13 = Gtk.Button(label="Exit")
        colorBtn13.set_hexpand(True)
        colorBtn13.connect("clicked", Gtk.main_quit)

        grid4.attach(image1,     0, 0, 4, 2)
        grid4.attach(label1,     0, 2, 4, 2)
        grid4.attach(label2,     0, 4, 4, 2)
        grid4.attach(colorBtn0,  0, 6, 1, 1)
        grid4.attach(colorBtn1,  1, 6, 1, 1)
        grid4.attach(colorBtn2,  2, 6, 1, 1)
        grid4.attach(colorBtn3,  3, 6, 1, 1)
        grid4.attach(colorBtn4,  0, 7, 1, 1)
        grid4.attach(colorBtn5,  1, 7, 1, 1)
        grid4.attach(colorBtn6,  2, 7, 1, 1)
        grid4.attach(colorBtn7,  3, 7, 1, 1)
        grid4.attach(colorBtn8,  0, 8, 1, 1)
        grid4.attach(colorBtn9,  1, 8, 1, 1)
        grid4.attach(colorBtn10, 2, 8, 1, 1)
        grid4.attach(label3,     0, 9, 4, 1)
        grid4.attach(colorBtn12, 0, 10, 2, 1)
        grid4.attach(colorBtn13, 2, 10, 2, 1)

        self.add(frame4)
        frame4.add(grid4)

    def on_clicked(self, widget, choice):
        if widget.get_active():
            state = "on"

            if choice == "Don't change":
               print ("Choice is 'don't change'")
            else:
               subprocess.run(["sed", "-i", 's/import Colors.*/import Colors.' + choice + '/g', home + "/.xmonad/README.org"])
               subprocess.run(["sed", "-i", 's/import Colors.*/import Colors.' + choice + '/g', home + "/.xmonad/xmonad.hs"])
               subprocess.run(["sed", "-i", 's/^colors: .*/colors: \\*' + choice + '/g', home + "/.config/alacritty/alacritty.yml"])
               subprocess.run(["xmonad", "--restart"])
        else:
            print("Something else:", choice)


    def on_colorBtn12_clicked(self, widget):
        print("Back To Main Menu")
        win4.hide()
        win1.show_all()

win1 = MyWindow1()
win2 = MyWindow2()
win3 = MyWindow3()
win4 = MyWindow4()

win1.connect("destroy", Gtk.main_quit)
win2.connect("destroy", Gtk.main_quit)
win3.connect("destroy", Gtk.main_quit)
win4.connect("destroy", Gtk.main_quit)

win1.show_all()
Gtk.main()
