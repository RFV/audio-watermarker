# from see import *; log_on(__file__)
import subprocess, re, os

w01 = ('W01.wav', 1.113220) # clip length is 1.113220 sec
w02 = ('W02.wav', 0.847619) # clip length is 0.847619 sec
w03 = ('W03.wav', 1.834785) # clip length is 1.834785 sec
w04 = ('W04.wav', 2.339365) # clip length is 2.339365 sec
w05 = ('W05.wav', 2.520408) # clip length is 2.520408 sec

w_files = ((120, 8.0, ((w03, 0), (w04, 8), (w02, 8), (w02, 8), (w02, 8), (w01, 0), (w05, 9), (w02, 8), (w02, 8), (w02, 8)), 9.0),
		   (60,  8.0, ((w03, 0), (w04, 8), (w02, 8), (w02, 8), (w02, 8), (w01, 0), (w05, 9), (w02, 8), (w02, 8), (w02, 8)), 6.0),
		   (30,  7.0, ((w03, 0), (w04, 6), (w02, 7), (w02, 8), (w02, 8), (w01, 0), (w05, 9), (w02, 8), (w02, 8), (w02, 8)), 4.0),
		   (17,  5.0, ((w03, 6), (w02, 6), (w02, 9)), 2.5),
		   (10,  3.0, ((w01, 4), (w02, 4), (w02, 5)), 2.0),
		   (5,   1.5, ((w01, 2), (w02, 2), (w02, 2)), 1.5),
		   (0,   0.5, ((w01, 1), (w02, 2)), 0.5))

class AudioProcessor(object):
	def __init__(self, tools_folder, gui):
		super(AudioProcessor, self).__init__()
		self.tools_folder = tools_folder
		self.gui = gui
		self.still = subprocess.STARTUPINFO()
		self.still.dwFlags |= subprocess.STARTF_USESHOWWINDOW

	def get_clip_length(self, clip_file_name):# full path name of file
		'''returns the length of clip in seconds'''
		command_string = r'"%ssox.exe" "%s" -n stat' % (self.tools_folder, clip_file_name)
		output = subprocess.check_output(command_string, stderr=subprocess.STDOUT, startupinfo=self.still)
		return float(re.search('Length \(seconds\): *(\d*\.\d*)', output).group(1))

	def get_bit_depth(self, clip_file_name):
		command_string = r'"%ssox.exe" --i "%s"' % (self.tools_folder, clip_file_name)
		output = subprocess.check_output(command_string, stderr=subprocess.STDOUT, startupinfo=self.still)
		return re.search('Precision      : (.*?)-bit', output).group(1)

	def get_sample_rate(self, clip_file_name):
		command_string = r'"%ssox.exe" --i "%s"' % (self.tools_folder, clip_file_name)
		output = subprocess.check_output(command_string, stderr=subprocess.STDOUT, startupinfo=self.still)
		return re.search('Sample Rate    : (.*)', output).group(1)

	def encode_flac_folder(self, full_folder, flac_folder, flac_rate):
		wav_files = os.listdir(full_folder)
		wav_files_lenght = len(wav_files)
		for i, wav in enumerate(wav_files):
			self.gui.status['text'] = 'status: converting flac file %d of %d' % (i+1, wav_files_lenght)
			command_string = r'"%ssox.exe" "%s%s" -C%s "%s%s.flac"' % (self.tools_folder, full_folder, wav, flac_rate, flac_folder, wav[:-4])
			subprocess.call(command_string, startupinfo=self.still)

	def encode_mp3_folder(self, full_folder, mp3_folder, bitrate, artist, comment):
		wav_files = os.listdir(full_folder)
		wav_files_lenght = len(wav_files)
		for i, wav in enumerate(wav_files):
			self.gui.status['text'] = 'status: converting mp3 file %d of %d' % (i+1, wav_files_lenght)
			command_string = r'"%slame.exe" -b%s --tt "(www.soundimage.eu) - %s" --ta "%s" --tv TPUB="www.soundimage.eu" --tv WOAR="http://www.soundimage.eu" --tv WPUB="http://www.soundimage.eu" --tv TCOM="%s" --tc "%s" "%s%s" "%s%s.mp3"' % (self.tools_folder, bitrate, wav[:-4], artist, artist, comment, full_folder, wav, mp3_folder, wav[:-4])
			subprocess.call(command_string, startupinfo=self.still)


class WatermarkProcessor(AudioProcessor):
	def __init__(self, work_files_location, w_files_location, tools_folder, gui):
		super(WatermarkProcessor, self).__init__(tools_folder, gui)
		self.work_files_location = work_files_location
		self.w_files_location = w_files_location
		self.tools_folder = tools_folder
		self.temp_file = self.work_files_location + '/temp_clip.wav'
		self.gui = gui

	def _get_relative_volume_r128(self, clip_file_name, offset, length):
		# 1 cut a piece out of the file
		command_string = r'"%ssox.exe" "%s" "%s" trim %f %f' % (self.tools_folder, clip_file_name, self.temp_file, offset, offset + length)
		
		subprocess.call(command_string, startupinfo=self.still)

		command_string = r'%sbs1770gain/bs1770gain.exe "%s"' % (self.tools_folder, self.temp_file)
		
		output = subprocess.check_output(command_string, stderr=subprocess.STDOUT, startupinfo=self.still)
		os.remove(self.temp_file)

		# 3 convert RMS value to a % float value and return the value
		return pow(10, float(re.search('integrated:  (-\d*\.\d*) LUFS', output).group(1)) / 20.0)

	def _make_wfile_piece(self, clip_number, wfile_name, volume, padding_length):
		# take wfile clip and adjust volume -> tempfile
		command_string = r'"%ssox.exe" -v %f "%s" "%s"' % (self.tools_folder, volume, wfile_name, self.temp_file)
		
		subprocess.call(command_string, startupinfo=self.still)
		# take the tempfile and create a named piece
		command_string = r'"%ssox.exe" "%s" "%s%02d.wav" pad 0.0 %f' % (self.tools_folder, self.temp_file, self.work_files_location, clip_number, padding_length)
		
		subprocess.call(command_string, startupinfo=self.still)
		os.remove(self.temp_file)

	def _make_full_wfile(self, number_of_clips, wfile_name, start_time):
		#first put initial padding in
		command_string = r'"%ssox.exe" "%s00.wav" "%s000.wav" pad %f 0' % (self.tools_folder, self.work_files_location, self.work_files_location, start_time)
		
		subprocess.call(command_string, startupinfo=self.still)
		# put the pieces together
		pieces_string = '"%s000.wav" ' % self.work_files_location
		for clip_number in xrange(1, number_of_clips): pieces_string += '"%s%02d.wav" ' % (self.work_files_location, clip_number)
		command_string = r'"%ssox.exe" %s "%s%s"' % (self.tools_folder, pieces_string, self.work_files_location, wfile_name)
		
		subprocess.call(command_string, startupinfo=self.still)
		# clean up and remove old peices
		os.remove('%s000.wav' % self.work_files_location)
		for clip_number in xrange(number_of_clips): os.remove('%s%02d.wav' % (self.work_files_location, clip_number))
		
	def _mix(self, input_file_name, wfile_name, bitrate, artist, comment, output_file_name):
		command_string = r'"%ssox.exe" "%s" -r 44100 "%sr.wav"' % (self.tools_folder, input_file_name,  output_file_name[:-4])
		subprocess.call(command_string, startupinfo=self.still)

		command_string = r'"%ssox.exe" -m "%sr.wav" "%s%s" "%sp.wav"' % (self.tools_folder, output_file_name[:-4], self.work_files_location, wfile_name, output_file_name[:-4])
		subprocess.call(command_string, startupinfo=self.still)

		#normalization
		command_string = r'"%ssox.exe" --norm "%sp.wav" "%s"' % (self.tools_folder, output_file_name[:-4], output_file_name)
		subprocess.call(command_string, startupinfo=self.still)

		only_name = os.path.split(os.path.abspath(output_file_name))[1][:-4]
		command_string = r'"%slame.exe" --noreplaygain -b%s --tt "(www.soundimage.eu) - %s" --ta "%s" --tv TPUB="www.soundimage.eu" --tv WOAR="http://www.soundimage.eu" --tv WPUB="http://www.soundimage.eu" --tv TCOM="%s" --tc "%s" "%s" "%s.mp3"' % (self.tools_folder, bitrate, only_name, artist, artist, comment, output_file_name, output_file_name[:-4])
		subprocess.call(command_string, startupinfo=self.still)
		try:
			os.remove(output_file_name)
			os.remove("%sp.wav" % output_file_name[:-4])
			os.remove("%sr.wav" % output_file_name[:-4])
		except:
			print 'delete error: %s' % output_file_name

	def watermark_audio_file(self, input_file_name, volume_factor, curve_factor, bitrate, artist, comment, output_file_name, prefix, timing_suffix, demo_suffix, suffix, start):
		# log('watermark', input_file_name)
		clip_length = self.get_clip_length(input_file_name)
		clip_number = 0

		for method in w_files:
			if clip_length >= method[0]: break

		offset = method[1] # start the offset at the default location from where mixing should begin
		ending = method[3] # the ending length which must not have any WFile mixing done to the IFile

		# continue building a volume adjusted WFile (individual pieces) until it is the length of IFile minus the end silent part
		the_end = False

		while not the_end:
			for clip in method[2]:
				# check if it is within the set bounds (between initial silence and ending silence)

				if offset + clip[0][1] + ending < clip_length:
					# get the relative volume of that peice of the IFile
					linear_volume = self._get_relative_volume_r128(input_file_name, offset, clip[0][1])
					# create new volume adjusted WFile + padding at end, named according to the clip_number
					wfile_name = self.w_files_location + clip[0][0]
					lin_vol = (linear_volume**((curve_factor*2)**2)+0.2)
					if offset + clip[0][1] + clip[1] < clip_length:
						padding = clip[1]
					else:
						padding = 0
					self._make_wfile_piece(clip_number, wfile_name, lin_vol*volume_factor*7, padding)
					offset += clip[0][1] + clip[1]
					clip_number += 1

				else: #end of the Ifile
					the_end = True
					break

		timing_suffix_str = demo_suffix_str = prefix_str = suffix_str = extras = ''
		if demo_suffix: demo_suffix_str = '_demo'
		if timing_suffix: timing_suffix_str = '_%02d%02d' % (clip_length / 60, clip_length % 60)
		if prefix: prefix_str = prefix + '_'
		if suffix: suffix_str = '_' + suffix
		output_file_name_new = output_file_name[:-4]+timing_suffix_str+demo_suffix_str+suffix_str+'.wav'
		#put the pieces together and make a wfile of name wfile.wav in the temp folder
		self._make_full_wfile(clip_number, 'wfile.wav', method[1] * start)
		# mix in and normalise
		self._mix(input_file_name, 'wfile.wav', bitrate, artist, comment, output_file_name_new)