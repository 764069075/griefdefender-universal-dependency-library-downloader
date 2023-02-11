from zipfile import is_zipfile, ZipFile
from requests import get
from concurrent.futures import ThreadPoolExecutor
from os.path import exists, split, splitext, abspath, join
from os import mkdir, makedirs, startfile,system
from glob import glob
from hashlib import new
from json import loads
from sys import exit
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich.progress import Progress,TransferSpeedColumn
from rich.panel import Panel
from rich import box


try:

    console = Console()
    progress = Progress(
        *Progress.get_default_columns(),
        TransferSpeedColumn(),
        transient=True,
        expand=True,
    )
    jpath = []
    workers = 0
    proxies = {}

    def introduce():
        introduce = ''\
        +'欢迎使用 Welcome'\
        +'\n\n'\
        +'griefdefender全版本万能依赖库下载器 library-downloader'\
        +'\n\n'\
        +'GPL-3.0 license GITHUB 开源地址 website：'\
        +'\n\n'\
        +'https://github.com/764069075/griefdefender-universal-dependency-library-downloader'
        console.print(
            Panel(
                Text(introduce,style='bold blue',justify='center'),
                title = "[bold]Introduce",
                subtitle = "griefdefender-library-downloader",
                border_style = 'cyan3',
                # padding= (1,8,1,8),
                box=box.ASCII2,
                expand=True
                )
        )

    introduce()
    system('pause')

    def menu():

        functions = ['下载依赖文件',
                     '校验依赖文件 [待开发]',
                     f'插件路径设置 \n{jpath}' if jpath != [] else '插件路径设置 (未配置)',
                     f'代理设置 \n{proxies}' if proxies != {} else '代理设置 (未配置)',
                     f'线程设置 [{workers}]' if workers != 0 else '线程设置 (未配置)',
                     '退出']
        menu = ''

        for i, k in enumerate(functions):
            line = str(i + 1) + '. ' + str(k) + '\n\n'
            menu += line

        console.print(
            Panel(
                Text(menu, style='bold green',justify='center'),
                title="[bold]主菜单",
                subtitle="GD依赖库下载器",
                border_style='green1',
                padding=(2, 1, 0, 1),
                expand=True
            )
        )


    def proxy(proxy = None):

        if proxy == None:

            console.print('\n[deep_pink4]请填写以下代理信息')

            proxy = ':'.join([Prompt.ask('[blue]代理IP地址'), str(IntPrompt.ask('[blue]代理端口'))])

        proxies = {

            "http": f"http://{proxy}/",
            # "https": f"http://{proxy}/" https会连接超时

        }

        console.print('\n[purple]您的代理已配置为:',proxies)

        return proxies


    def worker(workers = None):

        if workers == None:

            workers = IntPrompt.ask('\n[cyan3]请填写启用线程数1~16',default='8',show_default=False)

            while(not 0 < workers < 17):

                workers = IntPrompt.ask('\n[red]不在允许范围,请重新填写启用线程数',default='8',show_default=False)

        console.print('\n[purple]您的下载线程数已配置为:', workers)

        return workers


    def JarPath(jpath = None):

        if jpath == None:

            jpath = Prompt.ask('\n[green]请输入gd插件完整路径').replace("\\","/").replace("\"","")

        while(not is_zipfile(jpath)):

            jpath = Prompt.ask('\n[red]请提供正确的gd插件完整路径应该以.jar结尾').replace("\\","/").replace("\"","")

        console.print('\n[green]√ [purple]插件路径已配置为:', jpath)

        return [jpath]


    def JarDirPath(jardir = None):

        if jardir == None:

            jardir = 'gd-plugins'

        console.print('\n正在检测文件夹的存在...')

        if not exists(jardir):

            console.print('\n未发现存放文件夹,正在创建')

            mkdir(jardir)

            # console.print(f'\n[magenta]😉 文件夹{jardir},创建完毕')

            with open(join(jardir,'请将gd插件拖入此目录.txt'),'w',encoding='utf')as w:
                w.write('请把需要下载依赖库的gd插件放入与我同目录之下,\n\n放入后即可返回程序进行下一步的操作.')

            console.print(f'\n[green]√ 文件夹 {jardir} 创建成功,请将gd插件拖入此文件夹中')

            startfile(jardir)

            system('pause')

            return []

        else:
            console.print('\n发现存放文件夹,正在读取插件...')

            while(sum([is_zipfile(i) for i in glob(join(jardir,'*.*'))]) < 1):

                console.print(f'\n[red]未发现gd插件,请在文件夹 {jardir}中 放入插件...')

                startfile(jardir)

                system('pause')

                if not exists(jardir):
                    console.print('\n文件夹已被[red]删除')
                    mkdir(jardir)
                    console.print('\n已[green]重建[/]文件夹,[cyan2]请将gd插件拖入此文件夹中')

            jpath = list(filter(lambda i:is_zipfile(i),glob(join(jardir,'*.*'))))

            # Console.print('\n'+jpath)

            jarinfo = ''

            for i,k in enumerate(jpath):
                jarinfo += f'{i+1}. {split(k)[-1]}\n'

            console.print('\n',
                Panel(
                    Text(jarinfo, style='bold magenta'),
                    title="[bold]Success-成功读取插件",
                    subtitle="Jar插件读取器",
                    border_style='green',
                    padding=(1, 1, 0, 1),
                    box=box.ASCII_DOUBLE_HEAD,
                    expand=False
                )
            )

            return jpath

    def LoadJarJsons(jpath):

        versions = {}
        for i in jpath:
            console.print(f'\n\n[yellow]正在读取 {split(i)[-1]}')
            versions.setdefault(i,[])

            with ZipFile(i, 'r') as zf:
                for k in zf.namelist():
                    if splitext(k)[-1] == '.json' and '/' not in k:
                        console.print(f'[green]· 发现版本[/] {splitext(k)[0]}')
                        versions[i].append(k)

        return versions

    def ChoiceVersion(versions):

        for i,v in list(versions.items()):
            console.print(f'\n[cyan1]正在筛选 {split(i)[-1]} 下载版本')

            if len(v) > 1:

                downversions = []

                while(len(downversions) == 0):
                    selected = Prompt.ask('\n[purple]请输入需要下载依赖库的对应版本号，例： 1.12.2 [blue]如果需要下载多个版本请使用+号隔开,例： 1.18.2+1.16.4+1.12.2 \n')
                    console.print(f'\n[yellow]正在解析您输入的版本: [/]{selected}')
                    downversions = list(filter(lambda s:s in v,[k + '.json' for k in selected.split('+')]))

                    if len(downversions) < 1:
                        console.print('[red]    未读取到相匹配的版本，请重新输入')
                    else:
                        break

                console.print('[yellow]解析后的待下载版本:\n')
                for k in downversions:
                    console.print('·', k[:-5])

                if Confirm.ask('\n[cyan2]是否解析正确，符合您的需求？',default='y'):
                    versions[i] = downversions
                else:
                    if Confirm.ask('\n[yellow]是否重新输入？',default='y'):
                        return ChoiceVersion(versions)
                    else:
                        return False

            elif len(v) == 1:
                console.print('\n[yellow] 仅发现 1 种版本无需筛选.')
            else:
                console.print('\n[red]  未读取到任何版本')
                versions.pop(i)

        return versions

    def LoadLibs(versions):
        for i in versions:
            with ZipFile(i,'r')as zf:
                for json in versions[i]:
                    json_data = loads(zf.read(json))
                    save_dir = splitext(split(i)[-1])[0]
                    yield json_data,save_dir

    def DownLoadFile(metadata,save_path,task_id):
        if not exists(split(save_path)[0]):
            makedirs(split(save_path)[0])
        with open(save_path,'wb')as w , get(metadata['url'], proxies=proxies,stream=True)as f:
            total_size = int(f.headers['Content-length'])
            progress.update(task_id, total=total_size,filename=save_path,description=f'[red]正在下载{split(save_path)[-1]}')
            progress.start_task(task_id)
            for content in f.iter_content(chunk_size=256):
                w.write(content)
                progress.update(task_id,advance=len(content))
        progress.update(task_id,description=f'[green]完成{split(save_path)[-1]}')
        progress.remove_task(task_id)

    def ValidFile(metadata,save_path):
        with open(save_path,'rb')as r:
            file_sha1 = new('sha1',r.read()).hexdigest()
        if file_sha1 != metadata['sha1']:
            return False
        else:
            return True

    def select(select = None):

        global jpath,workers,proxies

        if select == None:

            select = IntPrompt.ask('\n[cyan1]请选择菜单功能',choices=['1','2','3','4','5','6'],default="1",show_default=False,show_choices=True)

        if select == 6:

            console.print('\n[red]程序即将关闭\n')
            system('TIMEOUT /T 3 /NOBREAK')
            exit()

        elif select == 5:

            if Confirm.ask('\n[cyan3]是否启用默认线程数?(8)',default='y'):
                workers = worker(8)
            else:
                workers = worker()

        elif select == 4:

            if Confirm.ask('\n[cyan3]是否跟随本地代理?',default='y'):
                proxies = proxy('localhost')
            else:
                proxies = proxy()

        elif select == 3:

            if Confirm.ask('\n[cyan3]直接提供插件完整路径?否则从文件夹读取',default='y'):
                jpath = JarPath()
            else:
                jpath = JarDirPath()

        elif select == 2:

            pass

        else:
            if len(jpath) < 1:

                console.print('\n[cyan]未指定插件,自动执行插件选定程序')

                return 3

            if workers < 1:

                console.print('\n[cyan]未指定线程,自动执行线程选定程序')

                return 5

            if proxies == {}:

                console.print('\n[cyan]未指定代理,已自动执行选定本地代理程序')

                proxies = proxy('localhost')

            versions = ChoiceVersion(LoadJarJsons(jpath))
            if len(versions) == 0:
                console.print('[red bold]未发现gd插件依赖库文件信息,请检查您的jar文件是否正确')
                system('pause')
            else:
                with progress,ThreadPoolExecutor(workers)as TPE:
                    for json_data,save_dir in LoadLibs(versions):

                        version = json_data['version']
                        length = len(json_data['libraries'])
                        progress.console.print(f'[green]正在下载[/] {version}  [green]总计[/] {length}')
                        system('TIMEOUT /T 3 /NOBREAK')

                        for rate,metadata in enumerate(json_data['libraries']):

                            task_id = progress.add_task(f'{split(metadata["url"])[-1]}',start=False)
                            save_path = join('gd-libs-downloads', save_dir, 'lib', metadata['path'])
                            if exists(save_path):
                                progress.update(task_id,description=f'[yellow]校验中{split(metadata["url"])[-1]}')
                                if ValidFile(metadata, save_path):
                                    progress.update(task_id,completed=1,total=1,description=f'[green]完成{split(save_path)[-1]}')
                                    continue
                            progress.update(task_id, description=f'[cyan1]即将下载{split(metadata["url"])[-1]}')
                            TPE.submit(DownLoadFile,metadata,save_path,task_id)

                    TPE.shutdown(wait=True)
                    console.rule('\n[green]下载完毕啦')
                    system('pause')
                startfile(abspath('gd-libs-downloads'))

    while(True):

        menu()

        choice = select()

        while(choice != None):

            select(choice)

            choice = select(1)

        # system('clear')

except Exception:
    console.print_exception()
    console.print('\n[cyan2 bold]出错啦 😂😂😂')
    system('pause')