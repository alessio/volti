# -*- coding: utf-8 -*-

# Author: Milan Nikolic <gen2brain@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from configparser import ConfigParser

from gi.repository import Gtk, Pango, GdkPixbuf

from volti.defs import *
from volti.utils import log, get_icon_name, get_icon_themes

_PREFERENCES = None

class Preferences:
    """ Preferences window """

    def __init__(self, main_instance):
        """ Constructor """
        self.main = main_instance

        self.cp = ConfigParser()
        self.set_section()

        if not os.path.isfile(CONFIG_FILE):
            self.write_file()

        self.read_file()

    def read_file(self):
        """ Read config file """
        self.cp.read(CONFIG_FILE)
        for option in self.cp.options("global"):
            PREFS[option.lower()] = self.cp.get("global", option).strip()
        PREFS["control"] = self.cp.get(self.section, "control").strip()

    def write_file(self):
        """ Write config file """
        if not os.path.isdir(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR)
            except OSError:
                pass
        for section in self.section, "global":
            if not self.cp.has_section(section):
                self.cp.add_section(section)
        for key, val in list(PREFS.items()):
            if key in ["control"]:
                self.cp.set(self.section, key, val)
            else:
                self.cp.set("global", key, val)
        self.cp.write(open(CONFIG_FILE, "w"))

    def open(self, widget=None, data=None):
        """ Open preferences window """
        global _PREFERENCES
        if _PREFERENCES is None:
            _PREFERENCES = Preferences(self.main)
            _PREFERENCES.init_builder()
            _PREFERENCES.init_card_combobox()
            _PREFERENCES.init_treeview()
            _PREFERENCES.init_theme_combobox()
            _PREFERENCES.window.show_all()
        else:
            _PREFERENCES.window.present()

    def close(self, widget=None):
        """ Close preferences window """
        global _PREFERENCES
        self._set_body()
        self.write_file()
        if _PREFERENCES is not None:
            _PREFERENCES.window.destroy()
            del _PREFERENCES
            _PREFERENCES = None

    def _set_body(self):
        """ Set notification body """
        start, end = self.notify_body_text.get_buffer().get_bounds()
        body = self.notify_body_text.get_buffer().get_text(start, end, False)
        PREFS["notify_body"] = body
        self.main.notify_body = body

    def set_section(self):
        """ Set section name """
        self.section = "card-%s" % PREFS["card_index"]

    def init_builder(self):
        """ Initialize Gtk.Builder """
        try:
            glade_file = os.path.join(RES_DIR,
                    "preferences.glade")
            self.tree = Gtk.Builder()
            self.tree.set_translation_domain(APP_NAME)
            self.tree.add_from_file(glade_file)
        except Exception as err:
            log.exception(str(err))

        self.version_label = self.tree.get_object("version_label")
        self.version_label.set_text("%s %s" % (
            APP_NAME.capitalize(), APP_VERSION))

        self.window = self.tree.get_object("window")
        self.window.connect("destroy", self.close)
        icon_theme = Gtk.IconTheme.get_default()
        if icon_theme.has_icon("multimedia-volume-control"):
            self.window.set_icon_name("multimedia-volume-control")
        else:
            file = os.path.join(RES_DIR,
                    "icons", "multimedia-volume-control.svg")
            self.window.set_icon_from_file(file)

        self.button_close = self.tree.get_object("button_close")
        self.button_close.connect("clicked", self.close)

        self.button_browse = self.tree.get_object("button_browse")
        self.button_browse.connect("clicked", self.on_browse_button_clicked)

        self.mixer_entry = self.tree.get_object("mixer_entry")
        self.mixer_entry.set_text(PREFS["mixer"])
        self.mixer_entry.connect_after("changed", self.on_entry_changed)

        self.scale_spinbutton = self.tree.get_object("scale_spinbutton")
        self.scale_spinbutton.set_value(float(PREFS["scale_increment"]))
        self.scale_spinbutton.connect("value_changed", self.on_scale_spinbutton_changed)

        self.tooltip_checkbutton = self.tree.get_object("tooltip_checkbutton")
        self.tooltip_checkbutton.set_active(bool(int(PREFS["show_tooltip"])))
        self.tooltip_checkbutton.connect("toggled", self.on_tooltip_toggled)

        self.terminal_checkbutton = self.tree.get_object("terminal_checkbutton")
        self.terminal_checkbutton.set_active(bool(int(PREFS["run_in_terminal"])))
        self.terminal_checkbutton.connect("toggled", self.on_terminal_toggled)

        self.draw_value_checkbutton = self.tree.get_object("draw_value_checkbutton")
        self.draw_value_checkbutton.set_active(bool(int(PREFS["scale_show_value"])))
        self.draw_value_checkbutton.connect("toggled", self.on_draw_value_toggled)

        self.notify_checkbutton = self.tree.get_object("notify_checkbutton")
        self.notify_checkbutton.set_active(bool(int(PREFS["show_notify"])))
        self.notify_checkbutton.connect("toggled", self.on_notify_toggled)

        self.notify_body_text = self.tree.get_object("notify_body_text")
        self.notify_body_text.get_buffer().set_text(PREFS["notify_body"])

        self.position_checkbutton = self.tree.get_object("position_checkbutton")
        self.position_checkbutton.set_active(bool(int(PREFS["notify_position"])))
        self.position_checkbutton.connect("toggled", self.on_position_toggled)

        self.timeout_spinbutton = self.tree.get_object("timeout_spinbutton")
        self.timeout_spinbutton.set_value(float(PREFS["notify_timeout"]))
        self.timeout_spinbutton.connect("value_changed", self.on_timeout_spinbutton_changed)

        self.mixer_internal_checkbutton = self.tree.get_object("mixer_internal_checkbutton")
        self.mixer_internal_checkbutton.set_active(bool(int(PREFS["mixer_internal"])))
        self.mixer_internal_checkbutton.connect("toggled", self.on_mixer_internal_toggled)

        self.mixer_values_checkbutton = self.tree.get_object("mixer_values_checkbutton")
        self.mixer_values_checkbutton.set_active(bool(int(PREFS["mixer_show_values"])))
        self.mixer_values_checkbutton.connect("toggled", self.on_mixer_values_toggled)

        self.keys_checkbutton = self.tree.get_object("keys_checkbutton")
        if not HAS_XLIB:
            self.keys_checkbutton.set_sensitive(False)
            self.keys_checkbutton.set_active(False)
        else:
            self.keys_checkbutton.set_active(bool(int(PREFS["keys"])))
        self.keys_checkbutton.connect("toggled", self.on_keys_toggled)

        self.mute_radiobutton = self.tree.get_object("radiobutton_mute")
        self.mixer_radiobutton = self.tree.get_object("radiobutton_mixer")
        if PREFS["toggle"] == "mute":
            self.mute_radiobutton.set_active(True)
        elif PREFS["toggle"] == "mixer":
            self.mixer_radiobutton.set_active(True)
        self.mute_radiobutton.connect("toggled", self.on_radio_mute_toggled)
        self.mixer_radiobutton.connect("toggled", self.on_radio_mixer_toggled)

        self.set_notify_sensitive(bool(int(PREFS["show_notify"])))
        self.set_mixer_sensitive(bool(int(PREFS["mixer_internal"])))

    def init_card_combobox(self):
        """ Initialize combobox with list of audio cards """
        icon_theme = Gtk.IconTheme.get_default()
        if icon_theme.has_icon("audio-card"):
            icon = icon_theme.load_icon(
                    "audio-card", 22, flags=Gtk.IconLookupFlags.FORCE_SVG)
        else:
            file = os.path.join(RES_DIR,
                    "icons", "audio-card.svg")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(file)
            icon = pixbuf.scale_simple(22, 22, GdkPixbuf.InterpType.BILINEAR)

        self.combo_model = Gtk.ListStore(int, GdkPixbuf.Pixbuf, str)
        for index, card in enumerate(self.main.alsactrl.get_cards()):
            if card is not None:
                self.combo_model.append([index, icon, card])

        card_combobox = self.tree.get_object("card_combobox")
        card_combobox.set_model(self.combo_model)
        card_combobox.set_active(int(PREFS["card_index"]))

        cell1 = Gtk.CellRendererPixbuf()
        cell1.set_property("xalign", 0)
        cell1.set_property("xpad", 3)
        card_combobox.pack_start(cell1, False)
        card_combobox.add_attribute(cell1, "pixbuf", 1)

        cell2 = Gtk.CellRendererText()
        cell2.set_property("xpad", 10)
        card_combobox.pack_start(cell2, True)
        card_combobox.add_attribute(cell2, "text", 2)

        card_combobox.connect("changed", self.on_card_combobox_changed)

    def init_treeview(self):
        """ Initialize treeview with mixers """
        self.liststore = Gtk.ListStore(bool, str, int)
        for mixer in self.main.alsactrl.get_mixers(int(PREFS["card_index"])):
            active = (mixer == PREFS["control"])
            if active:
                self.liststore.append([active, mixer, Pango.Weight.BOLD])
            else:
                self.liststore.append([active, mixer, Pango.Weight.NORMAL])

        self.treeview = Gtk.TreeView(self.liststore)
        self.treeview.set_headers_visible(False)

        cell1 = Gtk.CellRendererToggle()
        cell1.set_radio(True)
        cell1.set_property("activatable", True)
        cell1.connect('toggled', self.on_treeview_toggled, self.liststore)
        column1 = Gtk.TreeViewColumn()
        column1.pack_start(cell1, True)
        column1.add_attribute(cell1, 'active', 0)
        self.treeview.append_column(column1)

        cell2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn()
        column2.pack_start(cell2, True)
        column2.add_attribute(cell2, 'text', 1)
        column2.add_attribute(cell2, 'weight', 2)
        self.treeview.append_column(column2)

        scrolledwindow = self.tree.get_object("scrolledwindow")
        scrolledwindow.add(self.treeview)

    def init_theme_combobox(self):
        """ Initialize combobox with list of available themes """
        model = Gtk.ListStore(int, str)
        theme_combobox = self.tree.get_object("theme_combobox")
        theme_combobox.set_model(model)

        self.themes = get_icon_themes(RES_DIR)
        for index, theme in enumerate(self.themes):
            model.append([index, theme])
            if theme == PREFS["icon_theme"]:
                theme_combobox.set_active(index)

        cell = Gtk.CellRendererText()
        theme_combobox.pack_start(cell, True)
        theme_combobox.add_attribute(cell, "text", 1)

        theme_combobox.connect("changed", self.on_theme_combobox_changed)

    def on_browse_button_clicked(self, widget=None):
        """ Callback for browse_button_clicked event """
        buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog = Gtk.FileChooserDialog(
                title=_("Choose external mixer"),
                action=Gtk.FileChooserAction.OPEN,
                buttons=buttons)
        dialog.set_current_folder("/usr/bin")
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_show_hidden(False)

        file_filter_mixers = Gtk.FileFilter()
        file_filter_mixers.set_name(_("Sound Mixers"))
        file_filter_mixers.add_custom(
                Gtk.FileFilterFlags.FILENAME, self.custom_mixer_filter, None)
        file_filter_all = Gtk.FileFilter()
        file_filter_all.set_name(_("All files"))
        file_filter_all.add_pattern("*")
        dialog.add_filter(file_filter_mixers)
        dialog.add_filter(file_filter_all)

        response = dialog.run()
        filename = dialog.get_filename()
        dialog.destroy()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if response == Gtk.ResponseType.OK:
            self.mixer_entry.set_text(filename)
            PREFS["mixer"] = filename
            return filename
        elif response == Gtk.ResponseType.CANCEL:
            return None

    def custom_mixer_filter(self, filter_info=None, data=None):
        """ Custom file filter with names of common mixer apps """
        mixers = ["aumix", "alsamixer", "alsamixergui", "gamix",
                "gmixer", "gnome-alsamixer", "gnome-volume-control"]
        if os.path.basename(filter_info.filename) in mixers:
            return True
        return False

    def on_card_combobox_changed(self, widget=None):
        """ Callback for card_combobox_changed event """
        model = widget.get_model()
        iter = widget.get_active_iter()
        card_index = model.get_value(iter, 0)
        PREFS["card_index"] = card_index

        mixers = self.main.alsactrl.get_mixers(card_index)

        self.set_section()
        if self.cp.has_section(self.section):
            PREFS["control"] = self.cp.get(self.section, "control").strip()
        else:
            PREFS["control"] = mixers[0]

        self.main.update()
        self.liststore.clear()

        for mixer in mixers:
            active = (mixer == PREFS["control"])
            if active:
                self.liststore.append([active, mixer, Pango.Weight.BOLD])
            else:
                self.liststore.append([active, mixer, Pango.Weight.NORMAL])

    def on_treeview_toggled(self, cell, path, model):
        """ Callback for treeview_toggled event """
        iter = model.get_iter_from_string(path)
        active = model.get_value(iter, 0)
        if not active:
            model.foreach(self.radio_toggle, None)
            model.set(iter, 0, not active)
            model.set(iter, 2, Pango.Weight.BOLD)

            PREFS["control"] = model.get_value(iter, 1)
            self.main.control = PREFS["control"]
            self.main.update()
            self.main.menu.toggle_mute.set_active(
                    self.main.alsactrl.is_muted())
            self.write_file()

    def on_theme_combobox_changed(self, widget=None):
        """ Callback for theme_combobox_changed event """
        model = widget.get_model()
        iter = widget.get_active_iter()
        index = model.get_value(iter, 0)

        icon_theme = self.themes[index]
        PREFS["icon_theme"] = icon_theme
        self.main.icon_theme = icon_theme

        volume = self.main.get_volume()
        icon = get_icon_name(volume)
        self.main.update_icon(volume, icon)

    def radio_toggle(self, model, path, iter, data):
        """ Toggles radio buttons status """
        active = model.get(iter, 0)
        if active:
            model.set(iter, 0, not active)
            model.set(iter, 2, Pango.Weight.NORMAL)

    def on_scale_spinbutton_changed(self, widget):
        """ Callback for scale_spinbutton_changed event """
        scale_increment = widget.get_value()
        PREFS["scale_increment"] = scale_increment
        self.main.scale_increment = scale_increment

    def on_tooltip_toggled(self, widget):
        """ Callback for tooltip_toggled event """
        active = widget.get_active()
        PREFS["show_tooltip"] = int(active)
        self.main.show_tooltip = active
        if active:
            self.main.update_tooltip(self.main.get_volume())
        else:
            self.main.set_tooltip_text("")

    def on_draw_value_toggled(self, widget):
        """ Callback for draw_value_toggled event """
        active = widget.get_active()
        PREFS["scale_show_value"] = int(active)
        self.main.scale.slider.set_draw_value(active)

    def on_terminal_toggled(self, widget):
        """ Callback for terminal_toggled event """
        active = widget.get_active()
        PREFS["run_in_terminal"] = int(active)
        self.main.run_in_terminal = active

    def on_entry_changed(self, widget):
        """ Callback for entry_changed event """
        mixer = widget.get_text()
        PREFS["mixer"] = mixer
        self.main.mixer = mixer

    def on_mixer_internal_toggled(self, widget):
        """ Callback for mixer_internal_toggled event """
        active = widget.get_active()
        PREFS["mixer_internal"] = int(active)
        self.main.mixer_internal = active
        self.set_mixer_sensitive(active)

    def on_mixer_values_toggled(self, widget):
        """ Callback for mixer_values_toggled event """
        active = widget.get_active()
        PREFS["mixer_show_values"] = int(active)

    def on_radio_mute_toggled(self, widget):
        """ Callback for radio_mute_toggled event """
        if widget.get_active():
            PREFS["toggle"] = "mute"
            self.main.toggle = "mute"

    def on_radio_mixer_toggled(self, widget):
        """ Callback for radio_mixer_toggled event """
        if widget.get_active():
            PREFS["toggle"] = "mixer"
            self.main.toggle = "mixer"

    def on_keys_toggled(self, widget):
        """ Callback for keys_toggled event """
        active = widget.get_active()
        PREFS["keys"] = int(active)
        self.main.keys = active
        self.main.init_keys_events()

    def on_notify_toggled(self, widget):
        """ Callback for notify_toggled event """
        active = widget.get_active()
        PREFS["show_notify"] = int(active)
        self.main.show_notify = active
        self.main.init_notify()
        self.set_notify_sensitive(active)
        if active and self.main.notify:
            volume = self.main.get_volume()
            icon = get_icon_name(volume)
            self.main.update_notify(volume, icon)

    def on_position_toggled(self, widget):
        """ Callback for position_toggled event """
        active = widget.get_active()
        PREFS["notify_position"] = int(active)
        self.main.notify_position = active
        if self.main.notify:
            self.main.notify.close()
            volume = self.main.get_volume()
            icon = get_icon_name(volume)
            self.main.update_notify(volume, icon)

    def on_timeout_spinbutton_changed(self, widget):
        """ Callback for spinbutton_changed event """
        timeout = widget.get_value()
        PREFS["notify_timeout"] = timeout
        self.main.notify_timeout = timeout

    def set_mixer_sensitive(self, active):
        """ Set widgets sensitivity """
        self.mixer_values_checkbutton.set_sensitive(active)
        self.mixer_entry.set_sensitive(not active)
        self.button_browse.set_sensitive(not active)
        self.terminal_checkbutton.set_sensitive(not active)

    def set_notify_sensitive(self, active):
        """ Set widgets sensitivity """
        self.timeout_spinbutton.set_sensitive(active)
        self.position_checkbutton.set_sensitive(active)
        self.notify_body_text.set_sensitive(active)
        if active and not self.main.notify.check_capabilities():
            self.position_checkbutton.set_sensitive(False)
            self.timeout_spinbutton.set_sensitive(False)
