#!/usr/bin/python

import sys
from lxml import html
import dryscrape
from insert_sections import insert 
from lxml import etree, html
from StringIO import StringIO

if 'linux' in sys.platform:
    # start xvfb in case no X is running. Make sure xvfb 
    # is installed, otherwise this won't work!
    dryscrape.start_xvfb()




start_url = 'http://webapps.lehigh.edu/registrar/schedule/'
session = dryscrape.Session()

course_data=[]
session.visit(start_url)



q = session.at_xpath('//*[@name="term"]')
q.set("201710")
q.select_option()
q.submit()



print_default=False
print_inst=False
print_teaches=False
print_class=False
print_section=False
print_course=False
data = ''
parser = html.HTMLParser()

major_data= html.parse(StringIO(session.body()),parser)

majors=[]

for value in major_data.xpath('//select[@name="subject"]/option'):
    if value.get("value")!='':
        majors.append(value.get("value"))

if(len(sys.argv)>1):
    for arg in sys.argv:
        if(arg=='inst'):
            print_inst=True
        if(arg=='teaches'):
            print_teaches=True
        if(arg=='class'):
            print_class=True
        if(arg=='section'):
            print_section=True
        if(arg=='course'):
            print_course=True

else:
    print_default=True


for major in majors:        
    q = session.at_xpath('//*[@name="subject"]')
    q.set(major)
    q.select_option()
    q.submit()
    data+=session.body()

tree = html.parse(StringIO(data), parser)

i=0
j=0
class_info = []

add = True
for value in tree.xpath('//td'):
    if(j==11):
        i+=1
        j=0
        add = True
    if(add):
        if(j==0):
            for crn in class_info:
                if(crn[0]==value.text_content()):
                    add = False
            if(add):
                class_info.append([None]*10)
                class_info[i][0]=value.text_content()
            else:
                i-=1
        if(j==1):
            temp=value.text_content()[:12]
            if(temp[-2:].isalpha()):
                temp=temp[:10]
            if(temp[-1:].isalpha()):
                temp=temp[:11]
            class_info[i][1]=temp.split()[0]
            class_info[i][2]=temp[:-4]
            class_info[i][3]=temp[-3:]
        if(j==2 or j==3):
            class_info[i][j+2]=value.text_content()
        if(j==4):
            class_info[i][j+2]=value.text_content()
            class_info[i][j+2]=class_info[i][j+2].replace("'","\'")
        if(j==7):
            class_info[i][7]=value.text_content()
        #class room
        if(j==8):
            class_info[i][8]=value.text_content()
        if(j==10):
            temp = value.text_content()
            if(temp==u'\xa0'):
                temp=''
            class_info[i][9]=temp
    print class_info[i]
    j+=1



if(print_inst):
    insts=[]
    f1=open('instructors.txt', 'w+')
    for inst in class_info:
        
        if inst[6] not in insts and inst[6] != ' ':
            insts.append(inst[6])
            print inst[6]
            f1.write(inst[6]+'\n')
if(print_class):
    classes=[]
    for class_name in class_info:
        if class_name[2] not in classes and class_name[2] != ' ':
            classes.append(class_name[2])
            print class_name[2]
if(print_section):
    for row in class_info:
        sections=[]
        sections.append([row[0],row[1],row[3],row[5],row[6]])
        print [row[0],row[1],row[3],row[5],row[6]]
if(print_course):
    f1=open('courses.txt', 'w+')
    cur=class_info[0][2]
    f1.write(class_info[0][2]+'\n')
    for title in class_info:
        if(cur!=title[2]):
            f1.write(title[2]+'\n')
            cur=title[2]
            print title[2]+"omg"
        print title[2]


if(print_default):
    for row in class_info:
        rc = insert(row) #insert into SQL
        if(rc == 1 or rc == 2):
            print row
            
