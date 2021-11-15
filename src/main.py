# coding=utf-8
import time
import csv
from pypinyin import lazy_pinyin
from thefuzz import process, fuzz
from tkinter import Tk, Text, Listbox, Frame, E, W, LEFT, RIGHT
from tkinter.font import Font


class DataMatcher(object):
	"""
	题目数据的初始化, 提供模糊查询功能.
	"""

	DATA_FILE = './data.csv'

	def __init__(self):
		super(DataMatcher, self).__init__()
		self.init_data(self.DATA_FILE)

	def init_data(self, filepath):
		with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
			reader = csv.reader(csvfile)
			self.raw_data = list(map(lambda row: (row[0], row[1]), reader))
			self.pinyin_data = [(' '.join(lazy_pinyin(x[0])), ' '.join(lazy_pinyin(x[1]))) for x in self.raw_data]
			self.words = {x[0]: idx for idx, x in enumerate(self.pinyin_data)}

	def get_close_match(self, words):
		words = ' '.join(lazy_pinyin(words))
		results = process.extractBests(words, self.words.keys(), scorer=fuzz.token_set_ratio)
		results.extend(process.extractBests(words, self.words.keys(), scorer=fuzz.token_sort_ratio))
		scored = {}
		for result in results:
			scored[result[0]] = max(result[1], scored.get(result[0], 0))
			if scored[result[0]] == 0:
				scored.pop(result[0])
		results = sorted([(self.raw_data[self.words[sent]], score) for sent, score in scored.items()], key=lambda x: x[1], reverse=True)
		return results


class ViewController(Tk):

	def __init__(self):
		super(ViewController, self).__init__()
		self.input_callback = None

		self.input_text = ''
		self.last_changed_input_time = 0
		self.cur_height = self.winfo_height()
		self.cur_width = self.winfo_width()

		self.init_view()

	def init_view(self):
		self.font = Font(font='微软雅黑', size=10)
		self.txt_input = Text(self, height=1, font=self.font)
		self.frame_result = Frame(self)
		self.list_question = Listbox(self.frame_result, font=self.font, width=50)
		self.list_answer = Listbox(self.frame_result, font=self.font)
		self.refresh_layout()

		self.bind('<Configure>', self.on_configure)
		self.wm_attributes('-topmost', 1)

	def refresh_layout(self):
		self.txt_input.pack(expand=1, fill='both')
		self.frame_result.pack(expand=1, fill='both')
		self.list_question.pack(expand=1, side=LEFT, fill='both')
		self.list_answer.pack(expand=1, side=RIGHT, fill='both')

	def on_configure(self, event):
		if not event:
			return
		if event.height != self.cur_height or event.width != self.cur_width:
			self.cur_height = event.height
			self.cur_width = event.width
			self.refresh_layout()
			print(self.cur_height, self.cur_width)

	def set_input_callback(self, input_callback):
		self.input_callback = input_callback

	def on_input(self, words):
		if callable(self.input_callback):
			self.input_callback(words)

	def set_match_results(self, results):
		self.list_question.delete(0, 'end')
		self.list_answer.delete(0, 'end')
		for result in results:
			self.list_question.insert('end', '%s - %s' % (result[0], result[1]))
			self.list_answer.insert('end', result[2])

	def start_loop(self):
		self.after(60, self.tick_wrap)
		self.mainloop()

	def tick_wrap(self):
		self.after(60, self.tick_wrap)
		self.tick()

	def tick(self):
		ts = time.time()
		cur_text = self.txt_input.get(1.0, 'end')
		if cur_text != self.input_text and ts - self.last_changed_input_time > 0.3:
			self.on_input(cur_text)
			self.last_changed_input_time = ts
			self.input_text = cur_text


class Main(object):

	def start(self):
		self.matcher = DataMatcher()
		self.vc = ViewController()
		self.vc.set_input_callback(self.match_words)
		self.vc.start_loop()

	def match_words(self, words):
		results = self.matcher.get_close_match(words)
		results = map(lambda x: (x[1], x[0][0], x[0][1]), results)
		# results = map(lambda x: '{score:3} - {question:<35} - {answer}'.format(score=x[1], question=x[0][0], answer=x[0][1]), results)
		self.vc.set_match_results(results)


if __name__ == '__main__':
	Main().start()
