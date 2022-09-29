import sys
import os
import json

def help(*args):
    print("help_info")

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
            print("WARNING: " + i + " is not an existing file/dir. Skipping...")
   
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
        # TODO: сохранить структуру каталогов
        os.system("cp -r --parents " + i + " configs")
        #os.system("rsync -az -f\"+ */\" " + i + " configs")

def schedule(*args):
    pass # TODO

def main():
    args = sys.argv
    if len(args) > 1: # Если указана функция для запуска...
        globals()[args[1]]() # ...запускаем только её
        return 0

    function_map = {
            "help": help,
            "cache": cache,
            "backup": backup,
            "schedule": schedule,
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
