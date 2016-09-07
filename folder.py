# from see import *; log_on(__file__)
import zipfile, os, re, distutils.dir_util, shutil
from processing import AudioProcessor

class FolderSetup(object):
	"""setting up of folder"""
	def __init__(self, base_folder, artist, tools_folder, gui, mp3, flac):
		super(FolderSetup, self).__init__()

		self.output_folder = '%s%s/' % (base_folder, artist)
		os.makedirs(self.output_folder)

		self.output_folder_full = self.output_folder+"full/"
		os.mkdir(self.output_folder_full)

		self.output_folder_org = self.output_folder+"org/"
		os.mkdir(self.output_folder_org)

		if flac:
			self.output_folder_flac = self.output_folder+"flac/"
			os.mkdir(self.output_folder_flac)

		if mp3:
			self.output_folder_mp3 = self.output_folder+"mp3/"
			os.mkdir(self.output_folder_mp3)

		self.output_folder_demo = self.output_folder+"demo/"
		os.mkdir(self.output_folder_demo)

		self.gui = gui
		self.audio_tools = AudioProcessor(tools_folder, gui)

	def setup_zip(self, zip_file_name):
		self.gui.status['text'] = 'status: setting up new folders from zip file'
		with zipfile.ZipFile(zip_file_name, "r") as z:
			# output original zip to "org"
			z.extractall(self.output_folder+"org\\")
			# now only extract the wav files and put into full
			for name in z.namelist():
				if name[-4:] == '.wav':
					#extract files accordingly
					only_name = os.path.split(os.path.abspath(name))[1]
					outfile = open(self.output_folder_full + only_name, 'wb')
					outfile.write(z.read(name))
					outfile.close()

	def setup_folder(self, folder_name):
		self.gui.status['text'] = 'status: setting up the folders'
		distutils.dir_util.copy_tree(folder_name + '/', self.output_folder_org)
		for name in os.listdir(self.output_folder_org):
			if name[-4:] == '.wav':
				shutil.copyfile(self.output_folder_org+name, self.output_folder_full+name)

	def files_rename(self):
		self.gui.status['text'] = 'status: setting correct file names'
		for name in os.listdir(self.output_folder_full):
			# only_name = os.path.split(os.path.abspath(name))[1]
			#file naming stuff
			new_name = name.lower()
			new_name = re.sub(r' ', r'_', new_name)
			new_name = re.sub(r'[!`~@#$%^&*+-,\\/=;?"\']', r'', new_name)
			os.rename(self.output_folder_full+name, self.output_folder_full+new_name)
			
		#'full-version' suffix stuff
		wav_files = os.listdir(self.output_folder_full)
		wav_files.sort()
		full_versions = []
		toggle = False
		wav_search = wav_files[0]
		for wav in wav_files[1:]:
			if wav.startswith(wav_search[:-4]):
				toggle = True
			else:
				if toggle: 
					full_versions.append(wav_search)
					toggle = False
				wav_search = wav
		for fv in full_versions: os.rename(self.output_folder_full+fv, self.output_folder_full+fv[:-4]+"_(full_version).wav")

		wav_files = os.listdir(self.output_folder_full)
		for wav in wav_files:
			bit_depth = self.audio_tools.get_bit_depth(self.output_folder_full+wav)
			if bit_depth != '16':
				bit_depth_suffix_str = '_hd'+bit_depth
				os.rename(self.output_folder_full+wav, self.output_folder_full+wav[:-4]+bit_depth_suffix_str+'.wav')

	def convert_flac(self, flac_rate): #convert all in folder to flac folder
		self.audio_tools.encode_flac_folder(self.output_folder_full, self.output_folder_flac, flac_rate)

	def convert_mp3(self, mp3_rate, artist, comment): #convert all in folder to mp3
		self.audio_tools.encode_mp3_folder(self.output_folder_full, self.output_folder_mp3, mp3_rate, artist, comment)