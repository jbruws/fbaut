import sys
import os
import json

# TODO:
# - КАК Я БУДУ ПОДАВАТЬ КРОНУ ДАННЫЕ ДЛЯ ВХОДА В ГИТХАБ????????????
# - Сделать так, чтобы нормально работал пуш через ssh

MAIN_PATH = os.path.dirname(__file__) + "/" + os.path.basename(__file__)
USERNAME = os.getlogin()

class ConfigManager:
    global MAIN_PATH
    global USERNAME
    
    def __init__(self):
        self.rc_dir = None
        self.rc_name = None
        self.config_dir = None

    def help(self, *args):
        print("""
            -- help                    - вывести список команд
            -- cache [список папок]    - добавить файлы/папки в .conbatrc
            -- uncache [список папок]  - убрать файлы/папки из .conbatrc
            -- set_rc /путь/к/папке    - задать рабочую директорию
            -- backup                  - произвести бэкап файлов из .conbatrc
            -- schedule [d/w/m]        - производить авто-бэкап ежедневно/еженедельно/ежемесячно
            -- show_rc                 - вывести содержимое .conbatrc в консоль
            -- git_init [ссылка на гх] - создать локальный репозиторий git и связать его с репозиторием github
            -- quit                    - выйти
        """)

    def set_rc(self, *args):
        self.rc_dir = args[0][0]
        if not os.path.isdir(self.rc_dir):
            print("ОШИБКА: не является директорией")
            return 1
        os.chdir(self.rc_dir)
        self.config_dir = self.rc_dir + "/configs"
        self.rc_name = ".conbatrc"

    def show_rc(self, *args):
        try:
            contents = json.load(open(self.rc_name, "r"))
        except FileNotFoundError:
            print("ОШИБКА: .conbatrc не найден.")
            return 1

        for i in list(contents.keys()):
            if contents[i][0] == "f":
                print("file | {:>20} |".format(i))
            else:
                print("dir  | {:>20} | mask = {:>8}".format(i, contents[i][1]))

    def cache(self, *args):
        filenames = args[0]
        # Если rc-файл пуст, присваиваем переменной пустой словарь
        if not os.path.isfile(self.rc_name):
            rc_contents = {}
        else:
            f = open(self.rc_name, "r")
            rc_contents = json.loads(f.read())
            f.close()

        # Записываем, учитывая тип  (файл/директория)
        # "*" значит отсутствие маски
        for i in filenames:
            if os.path.isfile(i):
                rc_contents[i] = ["f", "*"]
            elif os.path.isdir(i):
                rc_contents[i] = ["d", "*"]
            else:
                print(i + " - несуществующий файл/директория. Пропускаем...")
       
        f = open(self.rc_name, "w")
        f.write(json.dumps(rc_contents, indent=4))
        f.close()

    # Знаю, что код дублируется из cache(), но мне пока что всё равно
    def cache_mask(self, *args):
        mask = args[0][-1]
        filenames = args[0][0:-1]
        
        # Если rc-файл пуст, присваиваем переменной пустой словарь
        if not os.path.isfile(self.rc_name):
            rc_contents = {}
        else:
            f = open(self.rc_name, "r")
            rc_contents = json.loads(f.read())
            f.close()

        # Записываем
        for i in filenames:
            if os.path.isfile(i):
                print("Сохранять с маской можно только директории. Пропускаем...")
            elif os.path.isdir(i):
                rc_contents[i] = ["d", mask]
            else:
                print(i + " - несуществующая директория. Пропускаем...")
       
        f = open(self.rc_name, "w")
        f.write(json.dumps(rc_contents, indent=4))
        f.close()

    def uncache(self, *args):
        filenames = args[0]
        if not os.path.isfile(self.rc_name):
            print("ОШИБКА: файла .conbatrc не существует.")
            return 1
        f = open(self.rc_name, "r")
        rc_contents = json.loads(f.read())
        f.close()
        for i in filenames:
            if i in rc_contents.keys():
                del(rc_contents[i])
        
        f = open(self.rc_name, "w")
        f.write(json.dumps(rc_contents, indent=4))
        f.close()

    def backup(self, *args):
        custom_commit_msg = True
        if self.rc_dir == None: # если вызывается cron'ом
            set_rc(args[0][0])
            custom_commit_msg = False

        file_list = json.load(open(self.rc_name, "r"))
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        else:
            # rm не стирает скрытые директории, так что .git остаётся
            os.system("rm -r " + self.config_dir + "/*") 

        for i in file_list.keys():
            if file_list[i][1] == "*": # без маски
                os.system("cp -r --parents " + i + " " + self.config_dir)
            else:
                os.system("find " + i + " -name \"" + file_list[i][1] + "\" -exec cp --parents {} " + self.config_dir + " \;")

        # если есть git-репозиторий
        if os.path.isdir(self.config_dir + "/.git"):
            os.chdir(self.config_dir)
            os.system('git add -A')

            # используем пользовательское название коммита, если оно есть
            if args != ([],) and custom_commit_msg:
                commit_msg = " ".join(args[0][:])
            else:
                try:
                    commit_count = int(os.popen("git rev-list --count HEAD").read())
                except ValueError:
                    commit_count = 0
                commit_msg = "Копия #{}".format(commit_count + 1)
                
            os.system('git commit -m "{}"'.format(commit_msg))
            os.system('git push -u origin master')
            os.chdir(self.rc_dir)

    def git_init(self, *args):
        origin_link = args[0][0]
        if os.path.isdir(self.config_dir + "/.git"):
            print("ВНИМАНИЕ: репозиторий Git уже существует в рабочей директории.")
            return 1

        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        
        os.chdir(self.config_dir)
        os.system("git init")
        os.system("git remote add origin " + origin_link)
        os.chdir(self.rc_dir)

    # Всё ещё не работает, но концепт понятен. Допилю в Qt-версии
    def schedule(self, *args):
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

        conbat_cronjob = cronjob_types[job_type] + " " + MAIN_PATH + " backup " + self.rc_dir + " # conbat job\n"
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

    def quit(self, *args):
        sys.exit()

    def preprocess(self, arg_list):
        for i in range(len(arg_list)):
            if "~" in arg_list[i]:
                arg_list[i] = arg_list[i].replace("~", "/home/{}".format(USERNAME))
        return arg_list

if __name__ == "__main__":
    args = sys.argv
    manager = ConfigManager()
    
    if len(args) > 1: # Если указана функция для запуска...
        eval("manager.{}({})".format(args[1], str(args[2:]))) # ...запускаем только её
        quit()   

    while True:
        command = input("> ").split(" ")
        command = manager.preprocess(command)
        if command[0] not in ["set_rc", "help", "quit"] and manager.rc_dir == None:
            print("ВНИМАНИЕ: не установлена директория с .conbatrc; запустите set_rc [путь к директории]")
        elif command[0] not in globals()['ConfigManager'].__dict__:
            print("ВНИМАНИЕ: неизвестная команда")
        else:
            eval("manager.{}({})".format(command[0], str(command[1:])))
