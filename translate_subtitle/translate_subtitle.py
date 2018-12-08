#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import os
import time
import pysrt
import shutil
from selenium import webdriver


# Translate Subtitle ver 1.1
# PARAMETER ==========================================================================================================

target_path = "/Users/Graph/Desktop/test"

# language combination
input, output = "en", "ja" # you can find language notation from web address.

dual_subtitle = False

make_backup_folder = False
backup_folder = "_backup"

# -------------------------------------------------------------------------------------------------------------------
limit_amount = 4000 #avoid maximum word limit
selenium_path = "/Applications/chromedriver"
url = "https://translate.google.com/?hl=ja#view=home&op=translate&sl={}&tl={}&text=tmp".format(input, output)
# ====================================================================================================================


class TranslationSRT():

	def __init__(self):

		self.driver = webdriver.Chrome(selenium_path)

	def open_page(self):

		self.driver.get(url)

	def translate(self, text):

		self.driver.get(url)

		element = self.driver.find_element_by_xpath('//*[@id="source"]')
		self.driver.execute_script("arguments[0].value=arguments[1]", element, text)
		time.sleep(3)
		result = self.driver.find_element_by_xpath('//*[@class="tlid-translation translation"]').text

		return result

if dual_subtitle == True:
	suffix = "_eng-jp"
else:
	suffix = "_jp"

# get all srt file
def find_all_file(path):
	for root, dirs, files in os.walk(path):
		yield root
		if root.find(backup_folder) == -1:
			for file in files:
				yield os.path.join(root, file)

list_srt = []
for full_file_path in find_all_file(target_path):
	split_full_file_path = os.path.split(full_file_path)
	file_path = split_full_file_path[0]
	file_name = split_full_file_path[1]
	if file_name.find(".srt") != -1 and file_name.find(suffix) == -1:
		file_info = {}
		file_info["name"] = file_name
		file_info["path"] = file_path
		list_srt.append(file_info)

if len(list_srt) != 0:
	print ("[ APP ] Launching Selenium Chrome...\n", flush= True)

	app = TranslationSRT()
	app.open_page()

	count_loop = 0
	for srt in list_srt:
		count_loop += 1
		# check backup
		backup_path = target_path + "/" + backup_folder
		if not os.path.exists(backup_path):
			os.mkdir(backup_path)

		file_name = srt["name"].split(".")
		print ("[ PROCESS ] Translating... {}/{}  {}".format(count_loop, len(list_srt), srt["name"]), flush= True)

		sub_set = pysrt.open(srt["path"] + "/" + srt["name"])

		sub_eng = []
		for sub in sub_set:
			str_en = sub.text.replace("\n", " ")
			if str_en.strip() == "":
				str_en = "-"
			sub_eng.append(str_en)

		# avoid limit
		stock, result = "", ""
		count_limit = 0
		for sub in sub_eng:
			if count_limit + len(sub) < limit_amount:
				count_limit += len(sub)
				stock += sub + "\n"
			else:
				result += app.translate(stock) + "\n"
				count_limit = 0
				count_limit += len(sub)
				stock = ""
				stock += sub + "\n"

		if len(stock) != 0:
			result += app.translate(stock) + "\n"

		result = result.split("\n")

		for index, sub in enumerate(sub_set):
			subtext_eng = sub_eng[index]
			subtext_ja = result[index]
			if dual_subtitle == True:
				sub.text = subtext_eng + "\n" + subtext_ja
			else:
				sub.text = subtext_ja

		# backup
		shutil.move(srt["path"] + "/" + srt["name"], backup_path + "/" + srt["name"])
		sub_set.save(srt["path"] + "/" + file_name[0] + suffix + "." + file_name[1], "utf-8")

	app.driver.close()
	print ("\n[ APP ] Translation and backup done.")
else:
	print ("[ ERROR ] No srt file found.")