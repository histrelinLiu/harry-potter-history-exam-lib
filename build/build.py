# coding=utf-8
import os
import shutil


def build():
	os.system('pyinstaller -F -w ../src/main.py')
	shutil.copy('./dist/main.exe', './')
	shutil.copy('../src/data.csv', './')
	shutil.copy('../src/main.py', './')
	shutil.rmtree('./build')
	shutil.rmtree('./dist')
	os.remove('./main.spec')


if __name__ == '__main__':
	build()
