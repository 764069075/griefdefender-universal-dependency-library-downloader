from zipfile import is_zipfile,ZipFile
from requests import get
from concurrent.futures import ThreadPoolExecutor
from os.path import exists,split,splitext,abspath
from os import mkdir,makedirs,startfile
from glob import glob
from hashlib import new
from json import loads
from sys import exit
from threading import active_count
from time import sleep

files='./jar/'

print('开始读取jar文件夹下的jar包数据。。。')

sleep(1)

if not exists(files):
    
    print('未能找到jar文件夹。。开始创建。。。\n')

    sleep(1)

    mkdir(files)

    print('jar文件夹创建成功！请将jar包放入此文件夹。\n')

    sleep(1)

    with open(files+'请将jar拖动至此目录下.txt','w',encoding='utf')as t:

        t.write('请将需下载库的griefdefender插件放入jar文件夹下，也就是与我同一目录下。然后返回程序按下回车（Enter）键，开始下载。\n\n你可同时放多个jar包')

    startfile(abspath(files))

    sleep(1)

    input('如果已经放入jar文件到jar文件夹，请按Enter键：')

def jiance(p):

    path = glob(p)
    
    return [i for i in path if is_zipfile(i)]

print('\n*** 正在检测jar文件 ***\n')

sleep(1)

while len(jiance(files+'*.jar')) < 1:

    print('未能检测到合格的jar包。。\n')

    print('(*￣3￣)╭   请将jar包放入jar文件夹。。。\n')

    startfile(abspath('./jar'))

    with open(files+'请将jar拖动至此目录下.txt','w',encoding='utf')as t:

        t.write('请将需下载库的griefdefender插件放入jar文件夹下，也就是与我同一目录下。然后返回程序按下回车（Enter）键，开始下载。\n\n你可同时放多个jar包')

    if input('放入后，请按Enter键(如需退出，请输入 n )') == 'n':

        exit()

pt=jiance(files+'*.jar')

print('\n> 发现 %d 个jar <'%(len(pt)))

sleep(1)

for i,k in zip(pt,range(len(pt))):

    print(str(k+1)+'.',split(i)[-1])

sleep(1)

print('\n\n-------开始下载-------\n')

sleep(1)

print('依赖文件将会被自动下载并分类到downloads文件夹下。。。\n')

sleep(1)

def dlfile(url,path,file_name,version,jindu,length):
    
    if not exists(split(path)[0]):

        makedirs(split(path)[0])

    with open(path,'wb')as t:
        
        print('## 正在下载 |'+split(path)[-1]+' |文件序列%d |<如下载过久说明文件过大，请耐心等待，直至下载程序结束>'%(jindu))
        
        t.write(get(url).content)
        
        print('√ 下载完成 |%s |%s |文件序列'%(file_name,version)+str(jindu)+' |共'+str(length)+' |剩'+str(active_count()-1)+'个文件正在下载')

worker = input('请输入 需要开启的 下载线程数量（最大32，建议不超过cpu核心数的2倍,不能低于1。。。）:')

while (not worker.isdigit()) or int(worker) < 1 or int(worker) > 32:

    worker = input('请重新输入 需要开启的 下载线程数量（最大32，建议不超过cpu核心数的2倍,不能低于1。。。）:')

TPE=ThreadPoolExecutor(int(worker))

data_file='./downloads/'

for i in jiance(files+'*.jar'):

    print('\n※正在读取%s\n'%(split(i)[-1]))

    sleep(1)
#     需要下载的json数据所在文件
    jss=[]
#     打开压缩包
    with ZipFile(i,'r') as jar:
#     读取所有文件
        for k in jar.namelist():
#           筛选需要的文件
            if splitext(k)[-1] == '.json' and '/'not in k:

                print('· 发现版本%s'%(splitext(k)[0]))
#               保存所有的依赖库版本文件名
                jss.append(k)
        while len(jss) != 1:

            banben = input('\n请输入需要下载的版本库，例：1.12.2 如果需要下载多个版本请使用+号隔开,例：1.18.2+1.16.4+1.12.2 输入完毕后按Enter回车键\n>> ')

            bb = [k+'.json' for k in banben.split('+')]

            print('\n正在解析输入的版本。。。\n')

            sleep(1)

            banben = [k for k in bb if k in jss]

            print('解析后的版本：\n')

            for k in banben:

                print('·',k[:-5])
        
            if input('\n是否解析正确？如有误请输入 n 重新输入，正确请直接回车：') == '':

                jss = banben
                
                break
#       读取每个文件的内容
        for k in jss:

            print('\n开始下载版本：' + splitext(k)[0] + ' 依赖库文件。。。')

            sleep(2)

            js=loads(jar.read(k))
#           提前准备存放路径
            file_name=splitext(split(i)[-1])[0]+'/'

            ver = js['version']
            
            file_data_path=data_file+file_name+ver+'/lib/'
            
            if not exists(file_data_path):
                
                makedirs(file_data_path)
#           获取每个文件里的每个数据的下载链接与存放路径
            for d,c in zip(js['libraries'],range(1,len(js['libraries'])+1)):
                
                url=d['url']
                
                file_path=d['path']
                
                sha_1=d['sha1']

                al = len(js['libraries'])
                
                end_path=file_data_path+file_path
                
                if exists(end_path):

                    print('(文件已存在 开始校验。。。)',end=' |')

                    with open(end_path,'rb') as p:
                        
                        sha1=new('sha1',p.read()).hexdigest()
                        
                    if sha1 == sha_1:
                        
                        print('√ 校验完毕 |数据吻合 |跳过 |文件序列%d |共%d'%(c,len(js['libraries'])))
                        
                        continue
                        
                    else:
                        
                        print('× 校验完毕 |数据异常 |重下 |文件序列%d'%(c))
                        
                TPE.submit(dlfile,url,end_path,file_name[:-1],ver,c,al)
                
TPE.shutdown(wait=True)

print('\no(￣▽￣)ｄ已全部下载完毕。。。')

input('\n按任意键打开downloads文件夹...并退出')

startfile(abspath(data_file))

exit()