import sys
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# TODO
# - сделать нормальный UI

MAIN_PATH = os.path.dirname(__file__) + "/" + os.path.basename(__file__)
HOME_DIR = os.environ["HOME"]
USERNAME = os.environ["USER"]

class ConfigManager:
    global MAIN_PATH
    global HOME_DIR
    global USERNAME

    def __init__(self, no_gui=False, *args):
        # Данные rc
        self.rc_dir = None
        self.rc_name = None
        self.config_dir = None
        
        # Пути для кэширования/раскэширования
        self.to_be_cached = None
        self.to_be_uncached = None
        
        # без интерфейса
        self.no_gui = no_gui
        
        if self.no_gui:
            self.rc_dir = args[0][0]
            self.rc_name = self.rc_dir + "/.conbatrc"
            self.config_dir = self.rc_dir + "/configs"
            os.chdir(self.rc_dir)
            self.cli_args = args
        else:
            self.create_ui()

    def create_ui(self):
        ## Основное
        self.app = QApplication(sys.argv)
        self.window = QDialog()
        self.grid_main = QGridLayout()
        self.window.setLayout(self.grid_main)
        self.window.setGeometry(0, 0, 500, 250)

        # Определяем вкладки
        self.tabs = QTabWidget(self.window)
        self.tab_rc = QWidget()
        self.tab_git = QWidget()
        self.tab_git_creds = QWidget()
        
        self.grid_rc = QGridLayout()
        self.grid_git = QGridLayout()
        self.grid_git_creds = QGridLayout()
        self.tab_rc.setLayout(self.grid_rc)
        self.tab_git.setLayout(self.grid_git)
        self.tab_git_creds.setLayout(self.grid_git_creds)
        
        self.tabs.addTab(self.tab_rc, "rc")
        self.tabs.addTab(self.tab_git, "git+cron")
        self.tabs.addTab(self.tab_git_creds, "git user info")

        ## ВКЛАДКА 1
        
        ## rc коробка
        self.groupbox_rc = QGroupBox()
        self.grid_groupbox_rc = QGridLayout()
        self.groupbox_rc.setLayout(self.grid_groupbox_rc)

        # Выбор рабочей директории
        self.set_rc_submit = QPushButton(self.window)
        self.set_rc_submit.clicked.connect(self.set_rc_dialog)
        self.set_rc_submit.setText("Выбрать rc")
        self.grid_groupbox_rc.addWidget(self.set_rc_submit, 0, 0, 1, 1)
        
        # Создание файла rc
        self.set_rc_submit = QPushButton(self.window)
        self.set_rc_submit.clicked.connect(self.create_rc_dialog)
        self.set_rc_submit.setText("Создать rc")
        self.grid_groupbox_rc.addWidget(self.set_rc_submit, 1, 0, 1, 1)
        
        self.grid_rc.addWidget(self.groupbox_rc, 0, 0, 4, 1)
        
        ## Кнопка для бэкапа
        self.groupbox_backup = QGroupBox()
        self.grid_groupbox_backup = QGridLayout()
        self.groupbox_backup.setLayout(self.grid_groupbox_backup)
        
        self.backup_submit = QPushButton(self.window)
        self.backup_submit.clicked.connect(self.backup)
        self.backup_submit.setText("БЭКАП!")
        
        self.grid_groupbox_backup.addWidget(self.backup_submit)
        self.grid_rc.addWidget(self.groupbox_backup, 0, 1)
        
        ## Коробка для кэширования
        self.groupbox_cache = QGroupBox()
        self.grid_groupbox_cache = QGridLayout()
        self.groupbox_cache.setLayout(self.grid_groupbox_cache)

        # Кэширование
        self.cache_file_submit = QPushButton(self.window)
        self.cache_file_submit.clicked.connect(self.cache_file_dialog)
        self.cache_file_submit.setText("Кэшировать файл")
        self.grid_groupbox_cache.addWidget(self.cache_file_submit, 0, 0)
        
        self.cache_dir_submit = QPushButton(self.window)
        self.cache_dir_submit.clicked.connect(self.cache_dir_dialog)
        self.cache_dir_submit.setText("Кэшировать папку")
        self.grid_groupbox_cache.addWidget(self.cache_dir_submit, 0, 1)

        self.cache_mask_in = QLineEdit(self.window)
        self.grid_groupbox_cache.addWidget(self.cache_mask_in, 1, 0)

        self.cache_mask_submit = QPushButton(self.window)
        self.cache_mask_submit.clicked.connect(self.cache_mask_dialog)
        self.cache_mask_submit.setText("Кэшировать по маске")
        self.grid_groupbox_cache.addWidget(self.cache_mask_submit, 1, 1)

        self.grid_rc.addWidget(self.groupbox_cache, 1, 1)

        ## Коробка для раскэширования
        self.groupbox_uncache = QGroupBox()
        self.grid_groupbox_uncache = QGridLayout()
        self.groupbox_uncache.setLayout(self.grid_groupbox_uncache)

        # Раскэширование
        self.uncache_file = QPushButton(self.window)
        self.uncache_file.clicked.connect(self.uncache_file_dialog)
        self.uncache_file.setText("Удалить файл")
        self.grid_groupbox_uncache.addWidget(self.uncache_file, 0, 0)
        
        self.uncache_dir = QPushButton(self.window)
        self.uncache_dir.clicked.connect(self.uncache_dir_dialog)
        self.uncache_dir.setText("Удалить папку")
        self.grid_groupbox_uncache.addWidget(self.uncache_dir, 0, 1)

        self.grid_rc.addWidget(self.groupbox_uncache, 2, 1)

        # Вывод show_rc
        self.show_rc_out = QLabel(self.window)
        self.show_rc_out.setText("_ .conbatrc _")
        #self.show_rc_out.resize(100, 100)
        self.grid_rc.addWidget(self.show_rc_out, 0, 4)

        #self.show_rc_submit = QPushButton(self.window)
        #self.show_rc_submit.clicked.connect(self.show_rc)
        #self.show_rc_submit.setText("Показать/скрыть rc")
        #self.grid_rc.addWidget(self.show_rc_submit, 0, 2)

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

        ## ВКЛАДКА 3

        # имя пользователя
        self.git_username_label = QLabel(self.window)
        self.git_username_label.setText("Имя пользователя GitHub")
        self.grid_git_creds.addWidget(self.git_username_label, 0, 2)
        self.git_creds_username = QLineEdit(self.window)
        self.grid_git_creds.addWidget(self.git_creds_username, 0, 0, 1, 2)

        # токен
        self.git_token_label = QLabel(self.window)
        self.git_token_label.setText("Токен GitHub")
        self.grid_git_creds.addWidget(self.git_token_label, 1, 2)
        self.git_creds_token = QLineEdit(self.window)
        self.grid_git_creds.addWidget(self.git_creds_token, 1, 0, 1, 2)

        # Вывод команд (вне вкладок)
        self.commands_out = QLabel(self.window)
        self.reset_output()
        self.commands_out.setAlignment(Qt.AlignCenter)
        self.grid_main.addWidget(self.commands_out, 1, 0)

        # Показ вкладок и окна
        self.grid_main.addWidget(self.tabs, 0, 0)
        self.window.show()

    ## Проверка rc и обработка команд

    def rc_check(func): 
        def check_and_run(self):
            if self.rc_is_not_set():
                self.reset_output("err", "rc-файл не задан")
                return 1
            else:
               func(self)
        return check_and_run
    
    def rc_is_not_set(self): # ёмкое название
        if None in [self.rc_name, self.rc_dir, self.config_dir]:
            return True
        return False

    def preprocess(self, args):
        # заменяем тильду в аргументе на домашнюю директорию пользователя
        if type(args) == str:
            args = args.replace("~", f"{HOME_DIR}")
        elif type(args) == list:
            for (i, s) in enumerate(args):
                args[i] = s.replace("~", f"{HOME_DIR}")
        else:
            print("ОШИБКА: preprocess() принимает строки или списки строк")
        return args

    def reset_output(self, mode="blank", msg=""):
        if mode == "success":
            self.commands_out.setText("Выполнено")
        elif mode == "err":
            self.commands_out.setText("ОШИБКА: " + msg)
        else:
            self.commands_out.setText("...")

    ## Файловые диалоги

    def generic_dialog(self, target_type="file"):
        choice_window = QFileDialog()
        choice_window.setFileMode(choice_window.ExistingFiles)
        choice_window.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden) # отображение скрытых файлов
        choice_window.setDirectory(HOME_DIR)
        if target_type == "dir": # Директории не принимаются по умолчанию
            choice_window.setFileMode(QFileDialog.Directory)
        else:
            choice_window.setFileMode(QFileDialog.AnyFile)
        if choice_window.exec_():
            names = choice_window.selectedFiles()[0]
            return names
        self.reset_output("err", "файл не указан")
        return None

    def set_rc_common(self, dir_name):
        if dir_name == None: # если юзер ничего не выбрал
            return 1

        self.rc_dir = dir_name
        os.chdir(self.rc_dir)
        self.config_dir = self.rc_dir + "/configs"
        self.rc_name = ".conbatrc"
        self.reset_output("success")

        self.show_rc()

    # ну и жесть. надо бы привести все это в порядок
    def create_rc_dialog(self): 
        rc_dir = self.generic_dialog("dir")
        full_name = rc_dir + "/.conbatrc"
        if not os.path.isfile(full_name):
            # создаём файл
            os.system("echo {} > " + full_name)
        else:
            self.reset_output("err", ".conbatrc уже есть в этой директории")
        self.set_rc_common(rc_dir)

    def set_rc_dialog(self):
        rc = self.generic_dialog()
        self.set_rc_common("/".join((rc.split("/"))[:-1])) # Подаём все, кроме последнего элемента

    @rc_check
    def cache_file_dialog(self):
        self.to_be_cached = self.generic_dialog("file")
        #print(filename)
        if self.to_be_cached != None:
            self.cache()

    @rc_check
    def cache_dir_dialog(self):
        self.to_be_cached = self.generic_dialog("dir")
        if self.to_be_cached != None:
            self.cache()
    
    @rc_check
    def cache_mask_dialog(self):
        self.to_be_cached = self.generic_dialog("dir")
        if self.to_be_cached != None:
            self.cache_mask()

    @rc_check
    def uncache_file_dialog(self):
        self.to_be_uncached = self.generic_dialog("file")
        if self.to_be_uncached != None:
            self.uncache()
    
    @rc_check
    def uncache_dir_dialog(self):
        self.to_be_uncached = self.generic_dialog("dir")
        if self.to_be_uncached != None:
            self.uncache()
    
    ## Собственно команды

    @rc_check
    def show_rc(self):
        try:
            contents = json.load(open(self.rc_name, "r"))
        except FileNotFoundError:
            self.reset_output("err", ".conbatrc не найден")
            return 1

        contents_string = "__________ .conbatrc __________\n"
        for i in list(contents.keys()):
            if contents[i][0] == "f":
                contents_string += "file | {:>20} |\n".format(i)
            else:
                contents_string += "dir  | {:>20} | mask = {:<8}\n".format(i, contents[i][1])
        if self.show_rc_out.text() == contents_string:
            self.show_rc_out.setText("__________ .conbatrc __________")
        else:
            self.show_rc_out.setText(contents_string)
        
    @rc_check
    def cache(self):
        filename = self.preprocess(self.to_be_cached)

        # Если rc-файл пуст, присваиваем переменной пустой словарь
        if not os.path.isfile(self.rc_name):
            rc_contents = {}
        else:
            f = open(self.rc_name, "r")
            rc_contents = json.loads(f.read())
            f.close()

        # Записываем, учитывая тип  (файл/директория)
        # "*" значит отсутствие маски
        if os.path.isfile(filename):
            rc_contents[filename] = ["f", "*"]
        elif os.path.isdir(filename):
            rc_contents[filename] = ["d", "*"]
        else:
            print(filename + " - несуществующий файл/директория. Пропускаем...")
       
        f = open(self.rc_name, "w")
        f.write(json.dumps(rc_contents, indent=4))
        f.close()
        
        self.reset_output("success")
        self.show_rc()
    
    @rc_check
    def cache_mask(self):
        if self.cache_mask_in.text() == "":
            self.reset_output("err", "введите маску файла")
            return 1
        args_raw = [self.cache_mask_in.text(), self.to_be_cached]
        args = self.preprocess(args_raw)
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

        self.reset_output("success")
        self.show_rc()
    
    @rc_check
    def uncache(self):
        chosen_file = self.to_be_uncached

        f = open(self.rc_name, "r")
        rc_contents = json.loads(f.read())
        f.close()

        if chosen_file in rc_contents.keys():
            del(rc_contents[chosen_file])
            f = open(self.rc_name, "w")
            f.write(json.dumps(rc_contents, indent=4))
            f.close()
            self.reset_output("success")
            self.show_rc()
        else:
            self.reset_output("err", "указанного файла нет в rc")
            return 1

    @rc_check
    def backup(self):
        #custom_commit_msg = True

        file_list = json.load(open(self.rc_name, "r"))
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        else:
            # rm не стирает скрытые директории (и файлы), так что .git и .conbatrc остаются
            os.system("rm -r " + self.config_dir + "/*") 

        for i in file_list.keys():
            if file_list[i][1] == "*": # без маски
                os.system("find \"" + i + "\" -not -path \"" + self.config_dir + "\" -exec cp -r --parents {} " + self.config_dir + " \;")
            else: # с маской
                os.system("find \"" + i + "\" -name \"" + file_list[i][1] + "\" -not -path \"" + self.config_dir + "\" -exec cp -r --parents {} " + self.config_dir + " \;")

        # если есть git-репозиторий
        if os.path.isdir(self.config_dir + "/.git"):
            f = open(".reponame", "r")
            repo_name = f.readlines()[0]
            f.close()

            os.chdir(self.config_dir)
            os.system('git add -A')

            try:
                commit_count = int(os.popen("git rev-list --count HEAD").read())
            except ValueError:
                commit_count = 0
            commit_msg = "Копия #{}".format(commit_count + 1)
            
            if self.no_gui:
                gh_username = self.cli_args[1]
                gh_token = self.cli_args[2]
            else:
                gh_username = self.git_creds_username.text()
                gh_token = self.git_creds_token.text()
                
            os.system('git commit -m "{}"'.format(commit_msg))
            os.system('git push https://{}:{}@github.com/{}/{}'.format(gh_username, gh_token, gh_username, repo_name))
            os.chdir(self.rc_dir)
        
        if not self.no_gui:
            self.reset_output("success")
            self.show_rc()

    @rc_check
    def git_init(self):
        origin_link = self.preprocess(self.git_init_in.text())
        repo_name = origin_link.split("/")[-1]

        f = open(".reponame", "w")
        f.write(repo_name)
        f.close()

        if os.path.isdir(self.config_dir + "/.git"):
            self.reset_output("err", "репозиторий Git уже существует в рабочей директории.")
            return 1

        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        
        os.chdir(self.config_dir)
        os.system("git init")
        os.system("git remote add origin " + origin_link)
        os.chdir(self.rc_dir)
        
        self.reset_output("success")

    @rc_check
    def schedule(self):
        cronjob_types = {"ежедневно": "@daily", "еженедельно": "@weekly", "ежемесячно": "@monthly"}
        job_type = cronjob_types[self.schedule_choices.currentText()]
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

        if os.path.isdir(self.config_dir + "/.git"):
            gh_username = self.git_creds_username.text()
            gh_token = self.git_creds_token.text()
            conbat_cronjob = f"{job_type} python3 {MAIN_PATH} --auto_backup {self.rc_dir} {gh_username} {gh_token} # conbat job\n"
        else:
            conbat_cronjob = f"{job_type} python3 {MAIN_PATH} --auto_backup {self.rc_dir} # conbat job\n"

        # удаляем старую запись и добавляем новую на её место
        conbat_cronjob_line_id = 0
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

        self.reset_output("success")

if __name__ == "__main__":
    if "--auto_backup" in sys.argv: # если вызывается cron'ом
        manager = ConfigManager(True, sys.argv[2:])
        manager.backup()
    else:
        manager = ConfigManager()
        sys.exit(manager.app.exec_())

