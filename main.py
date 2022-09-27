import sys
import os
import json

def help():
    print("help_info") # TODO

def cache(arg):
    filenames = arg
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

def backup():
    # Если папка configs есть, удаляем и создаём заново.
    file_list = json.load(open(".conbatrc", "r"))
    if os.path.isdir("configs"):
        os.system("rm -r configs")
    os.mkdir("configs")

    for i in file_list.keys(): 
        # TODO: сохранить структуру каталогов
        os.system("rsync -az -f\"+ */\" " + i + " configs")

def main():
    while True:
        command = input("> ").split(" ")
        
        if command[0] == "help":
            help() 
        elif command[0] == "init":
            init()
        elif command[0] == "cache":
            cache(command[1:])
        elif command[0] == "backup":
            backup()
        elif command[0] == "quit":
            exit()

if __name__ == "__main__":
    main()
