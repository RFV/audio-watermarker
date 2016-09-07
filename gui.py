# from see import *
import Tkinter as tk
import tkFileDialog, pygubu, json, os
import threading

class MyApplication(pygubu.TkApplication):

    def _create_ui(self):
        #1: Create a builder
        self.builder = pygubu.Builder()

        #2: Load an ui file
        self.builder.add_from_file('gui_layout.ui')

        #3: Create the widget using self.master as parent
        self.mainwindow = self.builder.get_object('Frame_1', self.master)
        self.run_button = self.builder.get_object('Button_run', self.master)
        self.ftp_button = self.builder.get_object('Button_ftp', self.master)
        self.status = self.builder.get_object('Label_status', self.master)

        self.set_title('Watermarker')
        self.load_settings()

        #TEMP
        # entry = self.builder.get_object('Entry_input', self.master)
        # entry.delete(0, tk.END)
        # entry.insert(0, r'C:/Users/RFV/Desktop/0 income/watermarker/work/audio.2/')

        # entry = self.builder.get_object('Entry_artist', self.master)
        # entry.delete(0, tk.END)
        # entry.insert(0, r'RFV')

    def set_callbacks(self, main_run, ftp_run):
        # Configure callbacks
        callbacks = {
            'on_open_zip_clicked': self.select_input_zip,
            'on_open_folder_clicked': self.select_input_folder,
            'on_load_clicked': self.load_click,
            'on_save_clicked': self.save_settings,
            'on_base_clicked': self.select_base_folder,
            'on_temp_clicked': self.select_temp_folder,
            'on_wfiles_clicked': self.select_wfiles_folder,
            'on_tools_clicked': self.select_tools_folder,
            'on_run_clicked': main_run,
            'on_ftp_clicked': ftp_run,
            'on_scale_slide': self.change_vol_display,
            'on_mix_slide': self.change_silence_display,
            'on_curve_slide': self.change_curve_display,
        }
        self.builder.connect_callbacks(callbacks)

    def change_vol_display(self, volume):
        mix = self.builder.get_object('Label_mix_volume', self.master)
        mix['text'] = 'mix %d %%' % int(float(volume) * 100)

    def change_silence_display(self, volume):
        silence = self.builder.get_object('Label_intro', self.master)
        silence['text'] = 'intro %d %%' % int(float(volume) * 200)

    def change_curve_display(self, volume):
        curve = self.builder.get_object('Label_curve', self.master)
        curve['text'] = 'curve %.2f %%' % float(volume)

    def select_input_zip(self):
        filename = tkFileDialog.askopenfilename(filetypes = (("Zip files", "*.zip") ,("All files", "*.*") ))
        entry = self.builder.get_object('Entry_input', self.master)
        entry.delete(0, tk.END)
        entry.insert(0, filename)

    def select_input_folder(self):
        foldername = tkFileDialog.askdirectory()
        entry = self.builder.get_object('Entry_input', self.master)
        entry.delete(0, tk.END)
        entry.insert(0, foldername + '/')

    def select_base_folder(self):
        foldername = tkFileDialog.askdirectory()
        entry = self.builder.get_object('Entry_base_folder', self.master)
        entry.delete(0, tk.END)
        entry.insert(0, foldername + '/')

    def select_temp_folder(self):
        foldername = tkFileDialog.askdirectory()
        entry = self.builder.get_object('Entry_temp_folder', self.master)
        entry.delete(0, tk.END)
        entry.insert(0, foldername + '/')

    def select_wfiles_folder(self):
        foldername = tkFileDialog.askdirectory()
        entry = self.builder.get_object('Entry_wfiles_folder', self.master)
        entry.delete(0, tk.END)
        entry.insert(0, foldername + '/')

    def select_tools_folder(self):
        foldername = tkFileDialog.askdirectory()
        entry = self.builder.get_object('Entry_tools_folder', self.master)
        entry.delete(0, tk.END)
        entry.insert(0, foldername + '/')

    def load_click(self):
        filename = os.path.split(tkFileDialog.askopenfilename(filetypes = (("Settings files", "*.json") ,("All files", "*.*") )))[1]
        entry = self.builder.get_object('Entry_settings_file', self.master)
        entry.delete(0, tk.END)
        entry.insert(0, filename)
        self.load_settings()

    def load_settings(self):
        settings_file_name = self.builder.get_object('Entry_settings_file', self.master).get()

        #open settings file
        with open(settings_file_name, 'r') as settings_file: settings = json.loads(settings_file.read())

        suffix_time = self.builder.get_variable('timing_variable')
        suffix_time.set({True: 1, False: 0}[settings['suffix time']])

        suffix_demo = self.builder.get_variable('demo_variable')
        suffix_demo.set({True: 1, False: 0}[settings['suffix demo']])

        mix_volume = self.builder.get_object('Scale_mix_volume', self.master)
        mix_volume.set(settings['mix volume'])
        self.change_vol_display(settings['mix volume'])

        curve = self.builder.get_object('Scale_curve', self.master)
        curve.set(settings['mix curve'])
        self.change_curve_display(settings['mix curve'])

        intro_silence = self.builder.get_object('Scale_intro', self.master)
        intro_silence.set(settings['intro silence'])
        self.change_silence_display(settings['intro silence'])

        flac_encoding = self.builder.get_variable('flac_variable')
        flac_encoding.set(settings['flac encoding'])

        mp3_encoding = self.builder.get_variable('mp3_variable')
        mp3_encoding.set(settings['mp3 encoding'])

        self.builder.get_variable('do_mp3_variable').set({True: 1, False: 0}[settings['do mp3']])

        self.builder.get_variable('do_flac_variable').set({True: 1, False: 0}[settings['do flac']])
      
        save_org = self.builder.get_variable('save_org_variable')
        save_org.set({True: 1, False: 0}[settings['save org folder']])

        # trim_begin = self.builder.get_variable('trim_begin_variable')
        # trim_begin.set({True: 1, False: 0}[settings['trim beginning']])

        # trim_end = self.builder.get_variable('trim_end_variable')
        # trim_end.set({True: 1, False: 0}[settings['trim ending']])
     
        self.builder.get_variable('tag_variable').set(settings['tag comment'])

        base_folder = self.builder.get_variable('base_variable')
        base_folder.set(settings['base folder'])

        wfiles_folder = self.builder.get_variable('wfiles_variable')
        wfiles_folder.set(settings['wfiles folder'])

        temp_folder = self.builder.get_variable('temp_variable')
        temp_folder.set(settings['temp folder'])

        tools_folder = self.builder.get_variable('tools_variable')
        tools_folder.set(settings['tools folder'])

        ftp_server = self.builder.get_variable('ftp_server_variable')
        ftp_server.set(settings['ftp server'])

        # ftp_folder = self.builder.get_variable('ftp_folder_variable')
        # ftp_server.set(settings['ftp folder'])

        ftp_user_name = self.builder.get_variable('ftp_user_name_variable')
        ftp_user_name.set(settings['ftp user'])

        ftp_password = self.builder.get_variable('ftp_user_password_variable')
        ftp_password.set(settings['ftp password'])

    def get_gui_settings(self, full=False):
        settings = {}

        suffix_time = self.builder.get_variable('timing_variable')
        settings['suffix time'] = suffix_time.get() == 1

        suffix_demo = self.builder.get_variable('demo_variable')
        settings['suffix demo'] = suffix_demo.get() == 1

        # suffix_bitrate = self.builder.get_variable('bitrate_variable')
        # settings['suffix bitrate'] = suffix_bitrate.get() == 1

        settings['tag comment'] = self.builder.get_variable('tag_variable').get()

        mix_volume = self.builder.get_object('Scale_mix_volume', self.master).get()
        settings['mix volume'] = mix_volume

        curve = self.builder.get_object('Scale_curve', self.master).get()
        settings['mix curve'] = curve

        intro_silence = self.builder.get_object('Scale_intro', self.master).get()
        settings['intro silence'] = intro_silence

        flac_encoding = self.builder.get_object('Entry_encoding_flac', self.master).get()
        settings['flac encoding'] = flac_encoding

        mp3_encoding = self.builder.get_object('Entry_encoding_mp3', self.master).get()
        settings['mp3 encoding'] = mp3_encoding

        # trim_begin = self.builder.get_variable('trim_begin_variable')
        # settings['trim beginning'] = trim_begin.get() == 1

        # trim_end = self.builder.get_variable('trim_end_variable')
        # settings['trim ending'] = trim_end.get() == 1

        settings['do mp3'] = self.builder.get_variable('do_mp3_variable').get() == 1

        settings['do flac'] = self.builder.get_variable('do_flac_variable').get() == 1

        save_org = self.builder.get_variable('save_org_variable')
        settings['save org folder'] = save_org.get() == 1
            
        base_folder = self.builder.get_object('Entry_base_folder', self.master).get()
        settings['base folder'] = base_folder

        wfiles_folder = self.builder.get_object('Entry_wfiles_folder', self.master).get()
        settings['wfiles folder'] = wfiles_folder

        temp_folder = self.builder.get_object('Entry_temp_folder', self.master).get()
        settings['temp folder'] = temp_folder

        tools_folder = self.builder.get_object('Entry_tools_folder', self.master).get()
        settings['tools folder'] = tools_folder

        tools_folder = self.builder.get_object('Entry_ftp_server', self.master).get()
        settings['ftp server'] = tools_folder

        # tools_folder = self.builder.get_object('Entry_ftp_folder', self.master).get()
        # settings['ftp folder'] = tools_folder

        tools_folder = self.builder.get_object('Entry_ftp_user_name', self.master).get()
        settings['ftp user'] = tools_folder

        tools_folder = self.builder.get_object('Entry_ftp_user_password', self.master).get()
        settings['ftp password'] = tools_folder

        if full:
            settings['input'] = self.builder.get_object('Entry_input', self.master).get()
            settings['artist'] = self.builder.get_object('Entry_artist', self.master).get()
            settings['prefix'] = self.builder.get_object('Entry_prefix', self.master).get()
            settings['suffix'] = self.builder.get_object('Entry_suffix', self.master).get()
            settings['tags'] = self.builder.get_object('Entry_tags', self.master).get()
        return settings
   
    def save_settings(self):
        settings = self.get_gui_settings()

        settings_file_name = self.builder.get_object('Entry_settings_file', self.master).get()

        #open settings file
        with open(settings_file_name, 'w') as settings_file:
            settings_file.write(json.dumps(settings, indent=4))
