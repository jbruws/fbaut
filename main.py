import sys
import os
import json

# TODO:
# - поддержка github. При инициализации локального репо сразу запрашивается ссылка на гх, при бэкапе делается commit + push
# - hard-ссылки (ln -h) вместо копирования файлов, для инкрементальности и красивого git diff'а

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

def show_rc(*args):
    try:
        contents = json.load(open(".conbatrc", "r"))
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
    if not os.path.isfile(".conbatrc"):
        rc_contents = {}
    else:
        f = open(".conbatrc", "r")
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

def backup(*args):
    args = args[0]
    if len(args) == 0:
        args = ["."] # стандартная директория - текущая
    # Если папка configs есть, удаляем и создаём заново.
    file_list = json.load(open(args[0] + "/.conbatrc", "r"))
    if os.path.isdir("configs"):
        os.system("rm -r configs")
    os.mkdir("configs")

    for i in file_list.keys(): 
        os.system("cp -r --parents " + i + " configs")

# Всё ещё не работает, но концепт понятен. Допилю в Qt-версии
def schedule(*args):
    args = args[0]
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

    conbat_cronjob = cronjob_types[args[0]] + " " + MAIN_PATH + " backup # conbat job\n"
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
            "help": help,
            "cache": cache,
            "backup": backup,
            "schedule": schedule,
            "show": show_rc,
            "quit": sys.exit
    }

    while True:
        command = input("> ").split(" ")
        if command[0] not in function_map:
            print("WARNING: unknown command")
        else:
            function_map[command[0]](command[1:])

if __name__ == "__main__":
    main()
