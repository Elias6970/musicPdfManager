import subprocess,sys,os

def generate_translation():
    all_files = []
    for root, dirs, files in os.walk(os.path.join(".","gui")):
        for file in files:
            if file.endswith(".py"):
                all_files.append(os.path.abspath(os.path.join(root, file)))

    path = "pylupdate6 " + " ".join(all_files)
    subprocess.check_output(path + " -ts .\\translate\\es_ES\\spanish.ts",shell=True)
    subprocess.check_output(path + " -ts .\\translate\\ca_VA\\valenciano.ts",shell=True)
    subprocess.check_output(path + " -ts .\\translate\\en_US\\english.ts",shell=True)

def compile_translation(lrelease_path:str|None = None):
    try:
        if lrelease_path is None:
            lrelease_path = os.path.join("lrelease.exe ")
        lrelease_path += " "
        subprocess.check_output(lrelease_path + ".\\translate\\ca_VA\\valenciano.ts -qm .\\translate\\ca_VA\\compiled\\ca_VA.qm",shell=True)
        subprocess.check_output(lrelease_path + ".\\translate\\en_US\\english.ts -qm .\\translate\\en_US\\compiled\\en_US.qm",shell=True)
        subprocess.check_output(lrelease_path + ".\\translate\\es_ES\\spanish.ts -qm .\\translate\\es_ES\\compiled\\es_ES.qm",shell=True)
    except Exception as e:
        print("Error compiling")

if __name__ == "__main__":
    try:
        if(sys.argv[1] == "compile"):
            if len(sys.argv) > 2:
                compile_translation(sys.argv[2])
            else:
                compile_translation()
        else:
            generate_translation()
    except Exception:
        generate_translation()