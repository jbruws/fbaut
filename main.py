import sys
import os
import json

# TODO:
# - поддержка github. При инициализации локального репо сразу запрашивается ссылка на гх, при бэкапе делается commit + push
# - hard-ссылки (ln -h) вместо копирования файлов, для инкрементальности и красивого git diff'а 
# - КАК Я БУДУ ПОДАВАТЬ КРОНУ ДАННЫЕ ДЛЯ ВХОДА В ГИТХАБ????????????

rc_dir = None
rc_path = None
MAIN_PATH = os.path.dirname(__file__) + "/" + os.path.basename(__file__)
USERNAME = os.getlogin()

def help(*args):
    print("""
        -- help                 - вывести список команд\n
        -- cache [список папок] - добавить файлы/папки в .conbatrc\n
        -- backup               - произвести бэкап файлов из .conbatrc\n
        -- schedule [d/w/m]     - производить авто-бэкап ежедневно/еженедельно/ежемесячно\n
        -- show                 - вывести содержимое .conbatrc в консоль
        -- quit                 - выйти
    """)

def set_rc(*args):
    global rc_dir
    global rc_path
    #print(args)
    rc_dir = args[0][0]
    rc_path = rc_dir + "/.conbatrc"

def show_rc(*args):
    try:
        contents = json.load(open(rc_path, "r"))
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
    if not os.path.isfile(rc_path):
        rc_contents = {}
    else:
        f = open(rc_path, "r")
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
   
    f = open(".conbatrc", "w")
    f.write(json.dumps(rc_contents, indent=4))
    f.close()

# нерабочая версия со ссылками
def cache_ln(*args):
    global rc_path
    global rc_dir
    
    backup_path = rc_dir + "/configs"
    
    f = args[0][0]
    if not (os.path.isfile(f) or os.path.isdir(f)):
        print("ВНИМАНИЕ: " + f + " - неизвестный файл.")
        return 1
    
    if os.path.isfile(f):
        file_parent_path = "/".join(f.split("/")[:-1])
        print(backup_path + file_parent_path)
        #os.system("mkdir -p " + backup_path + file_parent_path)
        #os.system("ln " + f + " " + backup_path + file_parent_path + "/" + f)
    else:
        print(backup_path + f)
        #os.system("mkdir -p " + backup_path + f)
        subdirs = os.popen("find " + f + " -type d").read().split("\n")
        print(subdirs)
        for i in subdirs:
            #os.system("mkdir -p " + backup_path + i)
            print(i)
        for i in subdirs:
            orig_files = os.popen("find " + i + " -type f").read().split("\n") # почему-то выдаёт и файлы из папки со скриптом
            for j in orig_files:
                print(j, backup_path + j)
                #os.system("ln " + j + " " + backup_path + j)

def backup(*args):
    global rc_dir
    global rc_path
    #print(args)
    if rc_dir == None: # если вызывается cron'ом
        rc_dir = args[0][0]
        rc_path = rc_dir + "/.conbatrc"

    backup_path = rc_dir + "/configs"
    # Если папка configs есть, удаляем и создаём заново.
    file_list = json.load(open(rc_path, "r"))
    if os.path.isdir(backup_path):
        os.system("rm -r " + backup_path)
    os.mkdir(backup_path)

    for i in file_list.keys(): 
        os.system("cp -r --parents " + i + " " + backup_path)

# Всё ещё не работает, но концепт понятен. Допилю в Qt-версии
def schedule(*args):
    #print(args)
    job_type = args[0][0]
    cronjob_types = {"d": "@daily", "w": "@weekly", "m": "@monthly"}
    cron_status = os.popen("systemctl --no-pager status cronie").read()

    # Проверяем, включён ли cron
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

def main():
    args = sys.argv
    if len(args) > 1: # Если указана функция для запуска...
        globals()[args[1]](args[2:]) # ...запускаем только её
        return 0

    function_map = {
            "set_rc": set_rc,
            "help": help,
            "cache": cache,
            "backup": backup,
            "schedule": schedule,
            "show": show_rc,
            "quit": sys.exit
    }

    while True:
        command = input("> ").split(" ")
        if command[0] not in ["set_rc", "help", "quit"] and rc_dir == None:
            print("ВНИМАНИЕ: не установлена директория с .conbatrc; запустите set_rc [путь к директории]")
        elif command[0] not in function_map:
            print("ВНИМАНИЕ: неизвестная команда")
        else:
            function_map[command[0]](command[1:])

if __name__ == "__main__":
    main()
