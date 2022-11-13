import sys
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# TODO:
# - КАК Я БУДУ ПОДАВАТЬ КРОНУ ДАННЫЕ ДЛЯ ВХОДА В ГИТХАБ????????????
# - Сделать так, чтобы нормально работал пуш через ssh

MAIN_PATH = os.path.dirname(__file__) + "/" + os.path.basename(__file__)
USERNAME = os.getlogin()

class ManagerGUI:
    global MAIN_PATH
    global USERNAME

    def __init__(self):
        
        ## Основное
        self.app = QApplication(sys.argv)
        self.window = QDialog()
        self.grid_main = QGridLayout()
        self.window.setLayout(self.grid_main)
        self.window.setGeometry(0, 0, 500, 250)

        ## Данные rc
        self.rc_dir = None
        self.rc_name = None
        self.config_dir = None

        # Определяем вкладки
        self.tabs = QTabWidget(self.window)
        self.tab_rc = QWidget()
        self.tab_git = QWidget()
        
        self.grid_rc = QGridLayout()
        self.grid_git = QGridLayout()
        self.tab_rc.setLayout(self.grid_rc)
        self.tab_git.setLayout(self.grid_git)
        
        self.tabs.addTab(self.tab_rc, "rc")
        self.tabs.addTab(self.tab_git, "git+cron")

        ## ВКЛАДКА 1

        # Выбор рабочей директории
        self.set_rc_in = QLineEdit(self.window)
        self.grid_rc.addWidget(self.set_rc_in, 0, 0)

        self.set_rc_submit = QPushButton(self.window)
        self.set_rc_submit.clicked.connect(self.set_rc)
        self.set_rc_submit.setText("Выбрать rc")
        self.grid_rc.addWidget(self.set_rc_submit, 0, 1)
        
        # Кнопка для бэкапа
        self.backup_submit = QPushButton(self.window)
        self.backup_submit.clicked.connect(self.backup)
        self.backup_submit.setText("БЭКАП!")
        self.grid_rc.addWidget(self.backup_submit, 1, 2)
        
        # Кэширование
        self.cache_in = QLineEdit(self.window)
        self.grid_rc.addWidget(self.cache_in, 1, 0, 2, 1)

        self.cache_submit = QPushButton(self.window)
        self.cache_submit.clicked.connect(self.cache)
        self.cache_submit.setText("Кэшировать")
        self.grid_rc.addWidget(self.cache_submit, 1, 1)

        self.cache_mask_submit = QPushButton(self.window)
        self.cache_mask_submit.clicked.connect(self.cache_mask)
        self.cache_mask_submit.setText("Кэшировать по маске")
        self.grid_rc.addWidget(self.cache_mask_submit, 2, 1)

        # Вывод show_rc
        self.show_rc_out = QLabel(self.window)
        self.show_rc_out.setText("--------- .conbatrc ---------")
        self.grid_rc.addWidget(self.show_rc_out, 3, 1, 1, 2)

        self.show_rc_submit = QPushButton(self.window)
        self.show_rc_submit.clicked.connect(self.show_rc)
        self.show_rc_submit.setText("Показать/скрыть rc")
        self.grid_rc.addWidget(self.show_rc_submit, 0, 2)

        ## ВКЛАДКА 2

        # Создание git-репозитория
        self.git_init_in = QLineEdit(self.window)
        self.grid_git.addWidget(self.git_init_in, 0, 0, 1, 2)

        self.git_init_submit = QPushButton(self.window)
        self.git_init_submit.clicked.connect(self.git_init)
        self.git_init_submit.setText("Создать git")
        self.grid_git.addWidget(self.git_init_submit, 0, 2)

        # cron
        self.schedule_choice_text = QLabel()
        self.schedule_choice_text.setText("Проводить бэкап ")
        self.schedule_choice_text.setAlignment(Qt.AlignRight)
        self.grid_git.addWidget(self.schedule_choice_text, 1, 0)

        self.schedule_choices = QComboBox(self.window)
        self.schedule_choices.addItem("ежедневно")
        self.schedule_choices.addItem("еженедельно")
        self.schedule_choices.addItem("ежемесячно")
        self.grid_git.addWidget(self.schedule_choices, 1, 1)

        self.schedule_submit = QPushButton(self.window)
        self.schedule_submit.clicked.connect(self.schedule)
        self.schedule_submit.setText("Подтвердить")
        self.grid_git.addWidget(self.schedule_submit, 1, 2)

        # Вывод команд (вне вкладок)
        self.commands_out = QLabel(self.window)
        self.commands_out.setText("-----")
        self.commands_out.setAlignment(Qt.AlignCenter)
        self.grid_main.addWidget(self.commands_out, 1, 0)

        # Показ вкладок и окна
        self.grid_main.addWidget(self.tabs, 0, 0)
        self.window.show()
        
    def preprocess(self, args):
        # заменяем тильду в аргументе на домашнюю директорию пользователя
        if type(args) == str:
            return args.replace("~", "/home/{}".format(USERNAME))
        elif type(args) == list:
            for i in args:
                i.replace("~", "/home/{}".format(USERNAME))
            return args
        else:
            print("ОШИБКА: preprocess() принимает строки или списки строк")
            return ""

    def rc_is_not_set(self): # ёмкое название
        if None in [self.rc_name, self.rc_dir, self.config_dir]:
            return True
        return False
    
    def show_rc(self):
        if self.rc_is_not_set():
            self.commands_out.setText("ОШИБКА: rc-файл не задан")
            return 1

        try:
            contents = json.load(open(self.rc_name, "r"))
        except FileNotFoundError:
            return("ОШИБКА: .conbatrc не найден.")

        contents_string = "---------- .conbatrc ----------\n"
        for i in list(contents.keys()):
            if contents[i][0] == "f":
                contents_string += "file | {:>20} |\n".format(i)
            else:
                contents_string += "dir  | {:>20} | mask = {:<8}\n".format(i, contents[i][1])
        if self.show_rc_out.text() == contents_string:
            self.show_rc_out.setText("---------- .conbatrc ----------")
        else:
            self.show_rc_out.setText(contents_string)
        
        self.commands_out.setText("-----")

    def set_rc(self):
        arg = self.preprocess(self.set_rc_in.text())
        self.rc_dir = arg
        if not os.path.isdir(self.rc_dir):
            self.commands_out.setText("ОШИБКА: не является директорией")
            return 1
        os.chdir(self.rc_dir)
        self.config_dir = self.rc_dir + "/configs"
        self.rc_name = ".conbatrc"
        
        self.commands_out.setText("-----")

    def cache(self):
        if self.rc_is_not_set():
            self.commands_out.setText("ОШИБКА: rc-файл не задан")
            return 1
        
        filenames = self.preprocess(self.cache_in.text().split())

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
        
        self.commands_out.setText("-----")

    # Знаю, что код дублируется из cache(), но мне пока что всё равно
    def cache_mask(self):
        if self.rc_is_not_set():
            self.commands_out.setText("ОШИБКА: rc-файл не задан")
            return 1
        
        args = self.preprocess(self.cache_in.text().split())
        mask = args[0]
        filenames = args[1:]
        
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

        self.commands_out.setText("-----")

    def uncache(self):
        args = self.preprocess(args)
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

    def backup(self):
        #custom_commit_msg = True

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

            # (временно убрал) используем пользовательское название коммита, если оно есть
            #if args != ([],) and custom_commit_msg:
            #    commit_msg = " ".join(args[0][:])
            #else:
            try:
                commit_count = int(os.popen("git rev-list --count HEAD").read())
            except ValueError:
                commit_count = 0
            commit_msg = "Копия #{}".format(commit_count + 1)
                
            os.system('git commit -m "{}"'.format(commit_msg))
            os.system('git push -u origin master')
            os.chdir(self.rc_dir)
        
        self.commands_out.setText("-----")

    def git_init(self):
        origin_link = self.preprocess(self.git_init_in)
        if os.path.isdir(self.config_dir + "/.git"):
            self.commands_out.setText("ОШИБКА: репозиторий Git уже существует в рабочей директории.")
            return 1

        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        
        os.chdir(self.config_dir)
        os.system("git init")
        os.system("git remote add origin " + origin_link)
        os.chdir(self.rc_dir)
        
        self.commands_out.setText("-----")

    # Всё ещё не работает, но концепт понятен. Допилю в Qt-версии
    def schedule(self):
        if self.rc_is_not_set():
            self.commands_out.setText("ОШИБКА: rc-файл не задан")
            return 1
        
        job_type = self.schedule_choices.currentText()
        cronjob_types = {"ежедневно": "@daily", "еженедельно": "@weekly", "ежемесячно": "@monthly"}
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
        conbat_cronjob_line_id = 0

        # удаляем старую запись и добавляем новую на её место
        for i in range(len(crontab_contents)-1):
            if "# conbat job" in crontab_contents[i]:
                crontab_contents.pop(i)
                conbat_cronjob_line_id = i
                break

        crontab_contents.insert(conbat_cronjob_line_id, conbat_cronjob)

        f = open(crontab_path, "w")
        for i in crontab_contents:
            f.write(i)
        f.close()
        
        self.commands_out.setText("-----")

if __name__ == "__main__":
    gui = ManagerGUI()
    sys.exit(gui.app.exec_())

