import requests
import time
import random
import datetime
import re
import sqlite3 as sq

url1='https://www.camboozle.com/female-cams' #20
url2='https://www.camboozle.com/male-cams' #5
url3='https://www.camboozle.com/couple-cams' #2
url4='https://www.camboozle.com/trans-cams' #3
urls=['https://www.camboozle.com/female-cams','https://www.camboozle.com/male-cams',
'https://www.camboozle.com/couple-cams','https://www.camboozle.com/trans-cams']
pages=[20,5,2,3]

def gethtml(url, pages):


	for i in range(1,pages+1):
		a=requests.get(url = url, params = f'page={i}', headers = {'User-agent': 'Mozilla 5.0'})
		b=a.text
		#print(b)

		f=open('text1.txt', 'a', encoding='utf-8')
		f.write(b)
		f.close()

		tsleep=((random.randint(10,200)) /10)
		print(f'скачана страница {i} из {pages}, сплю {tsleep} секунд')
		time.sleep(   tsleep )  


def readhtml():
	''' читает html файл с тхт, возвращает прочтенное'''

	with open('text1.txt', encoding='utf-8') as f:
		datafile = f.readlines()
		return datafile



###### СЛУЖЕБНАЯ
def timetofloat(num):
	if '.' in num:
		num=float(num)
		return num
	else:
		num=int(num)/60
		return round(num,1)
##### 


##### ДЛЯ ПОЛУЧЕНИЯ  ВРЕМЕНИ И ПРОСМОТРОВ
def make_time_views_list():
	"""возвращает строки с временем и зрителями"""
	lsttime=[]
	for line in readhtml():
		if 'class="cams"' in line:
			lsttime.append(line)   
	return lsttime
def convert_time_views():
	'''конвертирует из html строк в список [['1.2 hrs','50 vivers'], ['37 mins', '80 viewers']]'''
	lsttime=make_time_views_list()
	timelist=[]
	viewlist=[]

	for i in range(len(lsttime)):# делает список в минуты и просмотры
		lsttime[i]=lsttime[i].split(',')
		timelist.append( timetofloat(  (lsttime[i][0].split('>')[1])[:-4] )  ) 

		viewlist.append(     re.sub(   "[^0-9]", "",   (lsttime[i][1].split('<')[0])    )  )     
	return timelist, viewlist
#####



##### ДЛЯ СБОРА НИКОВ
def make_data_room_list():
	"""возвращает строки с именами комнат"""
	lst=[]
	for line in readhtml():
		if 'data-room' in line:
			lst.append(line)   
	return lst


def convert_data_room():
	'''конвертирует из html строк в список ников [user1, user2, user3]'''

	poslst=[]
	lst=make_data_room_list()
	lst=lst[::2]
	for i in range(len(lst)):
		lst[i]=lst[i].split('"')[3]
		poslst.append(i+1)
	return lst, poslst
#########




#### ДЛЯ ПОЛУЧЕНИЯ ВОЗРАСТА И ПОЛА
def make_age_gender():
	"""в"""
	age_gender_lst=[]
	for line in readhtml():
		if 'class="age gender' in line:
			age_gender_lst.append(line)   
	return age_gender_lst


def convert_age_gender():
	'''конвер'''
	age_gender_lst=make_age_gender()
	agelist=[]
	genderlist=[]

	for i in range(len(age_gender_lst)):# делает список в минуты и просмотры
		age_gender_lst[i]=age_gender_lst[i].split('gender')
		age_gender_lst[i]=age_gender_lst[i][1].split('"')
		genderlist.append(age_gender_lst[i][0])
		
		agelist.append(     re.sub(   "[^0-9]", "",   (age_gender_lst[i][1])    )  )
	
   
	return agelist, genderlist
################



######### ДЛЯ ПОЛУЧЕНИЯ ОПИСАНИЯ
def make_description():
	description_lst=[]
	for line in readhtml():
		if 'li title="' in line:
			description_lst.append(line)   
	return description_lst

def convert_description():
	lst=make_description()

	for i in range(len(lst)):
		lst[i]=lst[i].split("<a href=")
		lst[i]=lst[i][0].split("</li>")
		lst[i]=lst[i][0][11:-1]

	return lst
########










def add_to_dict():
	'''добавляет в словарь'''
	
	dr=convert_data_room()
	nicklst=dr[0]
	poslst=dr[1]

	tw=convert_time_views()
	timelist=tw[0]
	viewlist=tw[1]

	ag=convert_age_gender()
	agelist=ag[0]
	genderlist=ag[1]

	dsr=convert_description()




	a={}
	dtime=str(datetime.datetime.now().strftime("%a %Y/%m/%d %H:%M:%S"))



	with sq.connect('cbdb.db') as con:
		for i in range(len(nicklst)):

		
						
			if i%250==0:
				print('записано ', i,' из ', len(nicklst)-1)
			cur=con.cursor()	
			cur.execute(f'''CREATE TABLE IF NOT EXISTS models (	
				name TEXT,
				time_msk TEXT,
				position INTEGER,
				duration_hours INTEGER,
				viewers INTEGER,
				age INTEGER,
				gender TEXT,
				description TEXT
				 )
				''')

			if agelist[i]!='': #заменяет пустые значения на not stated
				agelist[i]=int(agelist[i])
			else: agelist[i]='not stated'
			cur.execute(f'''INSERT INTO models VALUES 
				('{nicklst[i]}','{dtime}','{poslst[i]}','{float(timelist[i])}', '{int(viewlist[i])}',
				'{(agelist[i])}','{(genderlist[i])}', '{dsr[i]}')''')
			
		print('запись завершена')



def clearhtml():
	'''очищает html текстовый файл, чтобы загрузить новые значения потом'''
	f=open('text1.txt', 'w', encoding='utf-8')
	f.close()





def loooop():
	count=0

	urls=['https://www.camboozle.com/female-cams','https://www.camboozle.com/male-cams',
	'https://www.camboozle.com/couple-cams','https://www.camboozle.com/trans-cams']
	pages=[1,1,1,1]
	clearhtml()
	while True:
		for i in range(len(urls)):	
			gethtml(urls[i],pages[i])

			add_to_dict()
			clearhtml()
		tsleep=200
		count+=1
		print(f'цикл {count} завершен. сплю {tsleep} секунд')
		time.sleep(tsleep)
	

loooop()


