import subprocess,sys,os

def generate_translation():
    all_files = []
    for root, dirs, files in os.walk(os.path.join(".","frontend_pyqt")):
        for file in files:
            if file.endswith(".py"):
                all_files.append(os.path.abspath(os.path.join(root, file)))

    if not all_files:
        print("No Python files found for translation.")
        return

    base_cmd = ["pylupdate6"] + all_files
    
    es_ts = os.path.join("frontend_pyqt", "translate", "es_ES", "spanish.ts")
    ca_ts = os.path.join("frontend_pyqt", "translate", "ca_VA", "valenciano.ts")
    en_ts = os.path.join("frontend_pyqt", "translate", "en_US", "english.ts")

    try:
        subprocess.check_call(base_cmd + ["-ts", es_ts])
        subprocess.check_call(base_cmd + ["-ts", ca_ts])
        subprocess.check_call(base_cmd + ["-ts", en_ts])
        print("Translations generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating translations: {e}")

def compile_translation(lrelease_path:str|None = None):
    if lrelease_path is None:
        lrelease_path = "lrelease" if os.name != 'nt' else "lrelease.exe"
    
    es_ts = os.path.join("frontend_pyqt", "translate", "es_ES", "spanish.ts")
    es_qm = os.path.join("frontend_pyqt", "translate", "es_ES", "compiled", "es_ES.qm")
    
    ca_ts = os.path.join("frontend_pyqt", "translate", "ca_VA", "valenciano.ts")
    ca_qm = os.path.join("frontend_pyqt", "translate", "ca_VA", "compiled", "ca_VA.qm")
    
    en_ts = os.path.join("frontend_pyqt", "translate", "en_US", "english.ts")
    en_qm = os.path.join("frontend_pyqt", "translate", "en_US", "compiled", "en_US.qm")

    try:
        subprocess.check_call([lrelease_path, ca_ts, "-qm", ca_qm])
        subprocess.check_call([lrelease_path, en_ts, "-qm", en_qm])
        subprocess.check_call([lrelease_path, es_ts, "-qm", es_qm])
        print("Translations compiled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling translations: {e}")
    except FileNotFoundError:
        print(f"Error: {lrelease_path} not found. Please ensure it is installed and in your PATH.")

def print_usage():
    print("Usage:")
    print("  python translate.py generate")
    print("  python translate.py compile [lrelease_path]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "compile":
        lrelease_path = sys.argv[2] if len(sys.argv) > 2 else None
        compile_translation(lrelease_path)
    elif command == "generate":
        generate_translation()
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)