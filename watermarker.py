# from see import *; log_on(__file__)
import gui, processing, folder
import os, shutil, tkMessageBox
from pygubu.builder import ttkstdwidgets
from ftpuploader import FTPUploader
import threading

def run():
	settings = app.get_gui_settings(full=True)
	if not settings['input']:
		tkMessageBox.showwarning("Folder Error", "please check the input setting")
		return
	if not settings['artist']:
		tkMessageBox.showwarning("Folder Error", "please check the artist setting")
		return
	if not os.path.isdir(settings['base folder']):
		tkMessageBox.showwarning("Folder Error", "please check the base folder setting")
		return
	if not os.path.isdir(settings['wfiles folder']):
		tkMessageBox.showwarning("Folder Error", "please check the wfiles folder setting")
		return
	if os.path.isdir('%s%s/' % (settings['base folder'], settings['artist'])):
		tkMessageBox.showwarning("Folder Error", "that artist folder already exists, please select another folder")
		return
	app.run_button['text']='wait'
	app.run_button['state'] = 'disabled'
	app.ftp_button['state'] = 'disabled'

	threading.Thread(target=process, args=([settings])).start()

def ftp_upload():
	settings = app.get_gui_settings(full=True)
	if not settings['ftp server']:
		tkMessageBox.showwarning("Folder Error", "please check the ftp server setting")
		return
	if not settings['ftp user']:
		tkMessageBox.showwarning("Folder Error", "please check the ftp user setting")
		return
	if not settings['ftp password']:
		tkMessageBox.showwarning("Folder Error", "please check the ftp password setting")
		return

	app.status['text'] = 'status: uploading ftp files'
	app.run_button['state'] = 'disabled'
	app.ftp_button['text']='wait'
	app.ftp_button['state'] = 'disabled'

	threading.Thread(target=process_ftp, args=([settings])).start()

def process_ftp(settings):
	sender = FTPUploader(settings['ftp server'], settings['ftp user'], settings['ftp password'])

	upload_folder = settings['base folder']+settings['artist']
	# log(upload_folder)
	sender.upload(upload_folder, settings['artist'])

	app.status['text'] = 'status:'
	app.run_button['state'] = 'normal'
	app.ftp_button['text']='ftp upload'
	app.ftp_button['state'] = 'normal'

def process(settings):
	folder_setup = folder.FolderSetup(settings['base folder'], settings['artist'], settings["tools folder"], app, settings['do mp3'], settings['do flac'])

	if settings['input'][-4:] == '.zip':
		folder_setup.setup_zip(settings['input'])
	else:
		folder_setup.setup_folder(settings['input'])

	folder_setup.files_rename()
	
	if settings['do mp3']:
		folder_setup.convert_mp3(settings['mp3 encoding'], settings['artist'], settings['tags'])
	if settings['do flac']:
		folder_setup.convert_flac(settings['flac encoding'])

	audio_mixer = processing.WatermarkProcessor(settings['temp folder'], settings['wfiles folder'], settings['tools folder'], app)
	files_list = os.listdir(folder_setup.output_folder_full)
	org_files = len(files_list)
	files_list_length = len(files_list)
	for i, wav in enumerate(files_list):
		app.status['text'] = 'status: watermarking file %d of %d' % (i + 1, files_list_length)
		audio_mixer.watermark_audio_file(folder_setup.output_folder_full+wav, settings['mix volume'], settings['mix curve'], settings['mp3 encoding'], settings['artist'], settings['tags'], folder_setup.output_folder_demo+wav, settings['prefix'], settings['suffix time'], settings['suffix demo'], settings['suffix'], settings['intro silence'] * 2)
	if not settings['save org folder']: shutil.rmtree(settings['base folder']+settings['artist']+'/org')

	ammount_files = len(os.listdir(folder_setup.output_folder_full))

	app.status['text'] = 'status: completed %d of %d files sucessfully' % (ammount_files, org_files)
	app.run_button['text']='run'
	app.run_button['state'] = 'normal'
	app.ftp_button['state'] = 'normal'

if __name__ == '__main__':
	root = gui.tk.Tk()
	app = gui.MyApplication(root)
	app.set_callbacks(run, ftp_upload)
	app.run()

