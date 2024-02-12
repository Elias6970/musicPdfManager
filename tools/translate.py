import subprocess,sys

def generate_translation():
    path = "pylupdate5 .\\gui\\about_us_window.py .\\gui\\abstract_windows.py .\\gui\\add_piece_window.py .\\gui\\add_scores_to_existing_piece_window.py .\\gui\\delete_piece_window.py .\\gui\\modify_piece_window.py .\\gui\\preferences_window.py .\\gui\\score_classifier_window.py .\\gui\\main_window.py "
    subprocess.check_output(path + "-ts .\\translate\\es_ES\\spanish.ts",shell=True)
    subprocess.check_output(path + "-ts .\\translate\\ca_VA\\valenciano.ts",shell=True)
    subprocess.check_output(path + "-ts .\\translate\\en_US\\english.ts",shell=True)

def compile_translation():
    path = ".\\tools\\lrelease.exe "
    subprocess.check_output(path + ".\\translate\\ca_VA\\valenciano.ts -qm .\\translate\\ca_VA\\compiled\\ca_VA.qm",shell=True)
    subprocess.check_output(path + ".\\translate\\en_US\\english.ts -qm .\\translate\\en_US\\compiled\\en_US.qm",shell=True)
    subprocess.check_output(path + ".\\translate\\es_ES\\spanish.ts -qm .\\translate\\es_ES\\compiled\\es_ES.qm",shell=True)

if __name__ == "__main__":
    try:
        if(sys.argv[1] == "compile"):
            compile_translation()
        else:
            generate_translation()
    except Exception:
        generate_translation()