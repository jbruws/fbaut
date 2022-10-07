import sys
import os
import json

# TODO:
# - КАК Я БУДУ ПОДАВАТЬ КРОНУ ДАННЫЕ ДЛЯ ВХОДА В ГИТХАБ????????????

rc_dir = None
rc_name = None
config_dir = None
MAIN_PATH = os.path.dirname(__file__) + "/" + os.path.basename(__file__)
USERNAME = os.getlogin()

def help(*args):
    print("""
        -- help                    - вывести список команд\n
        -- cache [список папок]    - добавить файлы/папки в .conbatrc\n
        -- uncache [список папок]  - убрать файлы/папки из .conbatrc\n
        -- set_rc /путь/к/папке    - задать рабочую директорию\n
        -- backup                  - произвести бэкап файлов из .conbatrc\n
        -- schedule [d/w/m]        - производить авто-бэкап ежедневно/еженедельно/ежемесячно\n
        -- show_rc                 - вывести содержимое .conbatrc в консоль\n
        -- git_init [ссылка на гх] - создать локальный репозиторий git и связать его с репозиторием github\n
        -- quit                    - выйти
    """)

def set_rc(*args):
    global rc_dir
    global rc_name
    global config_dir
    rc_dir = args[0][0]
    os.chdir(rc_dir)
    config_dir = rc_dir + "/configs"
    rc_name = ".conbatrc"

def show_rc(*args):
    try:
        contents = json.load(open(rc_name, "r"))
    except FileNotFoundError:
        print("ОШИБКА: .conbatrc не найден.")

    for i in list(contents.keys()):
        if contents[i] == "f":
            print("file: " + i)
        else:
            print("dir:  " + i)

def cache(*args):
    filenames = args[0]
    # Если rc-файл пуст, присваиваем переменной пустой словарь
    if not os.path.isfile(rc_name):
        rc_contents = {}
    else:
        f = open(rc_name, "r")
        rc_contents = json.loads(f.read())
        f.close()

    # Записываем, учитывая тип  (файл/директория)
    for i in filenames:
        if os.path.isfile(i):
            rc_contents[i] = "f"
        elif os.path.isdir(i):
            rc_contents[i] = "d"
        else:
            print(i + " - несуществующий файл/директория. Пропускаем...")
   
    f = open(rc_name, "w")
    f.write(json.dumps(rc_contents, indent=4))
    f.close()

def uncache(*args):
    filenames = args[0]
    if not os.path.isfile(rc_name):
        print("ОШИБКА: нечего удалять")
        return -1
    f = open(rc_name, "r")
    rc_contents = json.loads(f.read())
    f.close()
    for i in filenames:
        if i in rc_contents.keys():
            del(rc_contents[i])
    
    f = open(rc_name, "w")
    f.write(json.dumps(rc_contents, indent=4))
    f.close()

def backup(*args):
    global rc_dir
    global rc_name
    if rc_dir == None: # если вызывается cron'ом
        set_rc(args[0][0])

    file_list = json.load(open(rc_name, "r"))
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    else:
        # трём все в папке бэкапов, кроме .git (и .gitignore?)
        os.system("rm -r !(.git*)" + config_dir) 

    for i in file_list.keys(): 
        os.system("cp -r --parents " + i + " " + config_dir)

    # если есть git-репозиторий
    if os.path.isdir(config_dir + "/.git"):
        os.chdir(config_dir)
        os.system('git add -A')
        try:
            commit_count = int(os.popen("git rev-list --count HEAD").read())
        except ValueError: # По сути, этого не должно происходить
            commit_count = 0
        os.system('git commit -a -m "Копия #{}"'.format(commit_count + 1))
        os.system('git push -u origin master')
        os.chdir(rc_dir)

def git_init(*args):
    origin_link = args[0][0]
    if os.path.isdir(config_dir + "/.git"):
        print("ВНИМАНИЕ: репозиторий Git уже существует в рабочей директории.")
        return -1

    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    
    os.chdir(config_dir)
    os.system("git init")
    os.system("git remote add origin " + origin_link)
    os.system('git commit -a -m "Initial commit"')
    os.system('git push -u origin master')
    os.chdir(rc_dir)

# Всё ещё не работает, но концепт понятен. Допилю в Qt-версии
def schedule(*args):
    job_type = args[0][0]
    cronjob_types = {"d": "@daily", "w": "@weekly", "m": "@monthly"}
    cron_status = os.popen("systemctl --no-pager status cronie").read()

    # Включаем cron при необходимости
    if "disabled; preset: disabled" in cron_status or "inactive (dead)" in cron_status:
        print("cron выключен. Запускаем сервис...")
        os.system("sudo systemctl enable cronie")
        os.system("sudo systemctl start cronie")
    
    # Создаём файл (при необходимости) и читаем
    crontab_path = "/var/spool/cron/{}".format(USERNAME)
    if not os.path.isfile(crontab_path):
        print("Файла crontab для пользователя {} не существует. Создаём...".format(USERNAME))
        os.system("sudo touch {}".format(crontab_path))
        os.system("sudo chown {} {}".format(USERNAME, crontab_path))
    f = open(crontab_path, "r")
    crontab_contents = f.readlines()
    f.close()

    conbat_cronjob = cronjob_types[job_type] + " " + MAIN_PATH + " backup " + rc_dir + " # conbat job\n"
    conbat_cronjob_id = 0

    # удаляем старую запись и добавляем новую на её место
    for i in range(len(crontab_contents)-1):
        if "# conbat job" in crontab_contents[i]:
            crontab_contents.pop(i)
            conbat_cronjob_id = i
            break

    crontab_contents.insert(conbat_cronjob_id, conbat_cronjob)

    f = open(crontab_path, "w")
    for i in crontab_contents:
        f.write(i)
    f.close()

def quit(*args):
    sys.exit()

def preprocess(arg_list):
    for i in range(len(arg_list)):
        if "~" in arg_list[i]:
            arg_list[i] = arg_list[i].replace("~", "/home/{}".format(USERNAME))
    return arg_list

def main():
    args = sys.argv
    if len(args) > 1: # Если указана функция для запуска...
        globals()[args[1]](args[2:]) # ...запускаем только её
        return 0

    while True:
        command = input("> ").split(" ")
        command = preprocess(command)
        if command[0] not in ["set_rc", "help", "quit"] and rc_dir == None:
            print("ВНИМАНИЕ: не установлена директория с .conbatrc; запустите set_rc [путь к директории]")
        elif command[0] not in globals():
            print("ВНИМАНИЕ: неизвестная команда")
        else:
            globals()[command[0]](command[1:])

if __name__ == "__main__":
    main()
