#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Lorenzo Carbonell <a.k.a. atareao>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
from bs4 import BeautifulSoup
import gi
try:
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
except ValueError:
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
from asyncf import async_function


URL = 'https://dle.rae.es'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/39.0.2171.95 Safari/537.36'}


class DictionaryDialog(Gtk.Dialog):
    def __init__(self):
        super().__init__()
        self.set_title("Definiciones")
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.ui()
        self.show_all()

    def ui(self):
        grid = Gtk.Grid()
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        self.get_content_area().add(grid)
        label = Gtk.Label.new("Palabra:")
        grid.attach(label, 0, 0, 1, 1)
        self.entry = Gtk.Entry()
        grid.attach(self.entry, 1, 0, 1, 1)
        self.entry.connect("activate", self.on_activate)
        # self.expander = Gtk.Expander.new("Resultados:")
        self.expander = Gtk.Expander.new()
        self.expander.connect("activate", self.on_expander_activate)
        grid.attach(self.expander, 0, 1, 2, 1)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                  Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_size_request(450, 300)
        self.expander.add(scrolledwindow)

        store = Gtk.ListStore(str)
        self.resultados = Gtk.TreeView(model=store)
        self.resultados.connect("row-activated", self.on_row_activated)
        scrolledwindow.add(self.resultados)
        self.resultados.append_column(Gtk.TreeViewColumn(
            'Definiciones', Gtk.CellRendererText(), text=0))

    def on_row_activated(self, treeview, path, _):
        model = treeview.get_model()
        value = model.get_value(model.get_iter(path), 0)
        self.clipboard.set_text(value, -1)
        print(value)

    def on_expander_activate(self, _):
        self.resize(1, 1)

    def on_activate(self, _):
        def on_search_done(result, _):
            if self.expander.get_expanded() is False:
                self.expander.set_expanded(True)
            model = self.resultados.get_model()
            model.clear()
            for item in result:
                model.append([item])
            self.set_normal_cursor()

        @async_function(on_done=on_search_done)
        def do_search_in_thread():
            items = []
            word = self.entry.get_text()
            if word:
                word = self.entry.get_text()
                url = f"{URL}/{word}"
                response = requests.get(url, headers=HEADERS)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    posts = soup.find_all(True,
                                          {"class": ["j", "j1", "j2", "j3",
                                                     "j4", "j5", "j6", "k2",
                                                     "k3", "k4", "k5", "k6",
                                                     "m", "l2", "f"]})
                    if not posts:
                        print("contecontett")
                    else:
                        definition = ""
                        for post in posts:
                            checkIfWordStartsNumber = str(post.get_text())
                            if checkIfWordStartsNumber[0].isdigit():
                                if definition:
                                    items.append(definition)
                                definition = post.get_text()
                            else:
                                definition += ". " + post.get_text()
            return items

        self.set_wait_cursor()
        do_search_in_thread()

    def set_wait_cursor(self):
        Gdk.Screen.get_default().get_root_window().set_cursor(
            Gdk.Cursor(Gdk.CursorType.WATCH))
        while Gtk.events_pending():
            Gtk.main_iteration()

    def set_normal_cursor(self):
        Gdk.Screen.get_default().get_root_window().set_cursor(
            Gdk.Cursor(Gdk.CursorType.ARROW))
        while Gtk.events_pending():
            Gtk.main_iteration()

    def on_realize(self, *_):
        monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
        scale = monitor.get_scale_factor()
        monitor_width = monitor.get_geometry().width / scale
        monitor_height = monitor.get_geometry().height / scale
        width = self.get_preferred_width()[0]
        height = self.get_preferred_height()[0]
        self.move((monitor_width - width)/2, (monitor_height - height)/2)


if __name__ == "__main__":
    dd = DictionaryDialog()
    dd.run()
