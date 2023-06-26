import os,sys,shutil

PARTITURAS = "partituras"
EXTRAS = "extras"
COMPRESS = "compress"


def move_files(root,files):
    for i in files:
        if PARTITURAS not in root and ".pdf" in i:
            os.rename(root+"/"+i,root+"/"+PARTITURAS+"/"+i)
        elif COMPRESS not in root and (".zip" in i or ".rar" in i):
            os.rename(root+"/"+i,root+"/"+COMPRESS+"/"+i) 
        elif EXTRAS not in root and ".pdf" not in i:
            os.rename(root+"/"+i,root+"/"+EXTRAS+"/"+i)


#Elimina directorios creados sin querer
def delete_extra_dirs(root):
    if EXTRAS in root:
        try:
            shutil.rmtree(root+"/"+PARTITURAS)
            shutil.rmtree(root+"/"+COMPRESS)
        except FileNotFoundError:
            pass
    if COMPRESS in root:
        try:
            shutil.rmtree(root+"/"+PARTITURAS)
            shutil.rmtree(root+"/"+EXTRAS)
        except FileNotFoundError:
            pass         
    if PARTITURAS in root:
        try:
            shutil.rmtree(root+"/"+COMPRESS)
            shutil.rmtree(root+"/"+EXTRAS)
        except FileNotFoundError:
            pass 


#Create the empty dirs for the basic structure
def create_dirs(root,dirs:list):
    #Create dirs
    print(root)
    if PARTITURAS not in dirs and PARTITURAS not in root and COMPRESS not in root and EXTRAS not in root:
        os.makedirs(root+"/"+PARTITURAS,exist_ok=True)

    if EXTRAS not in dirs and EXTRAS not in root and COMPRESS not in root and PARTITURAS not in root:
        os.makedirs(root+"/"+EXTRAS,exist_ok=True)

    if COMPRESS not in dirs and COMPRESS not in root and PARTITURAS not in root and EXTRAS not in root:
        os.makedirs(root+"/"+COMPRESS,exist_ok=True)


def other_names(dirs):
    for i in dirs:
        if PARTITURAS != i and EXTRAS != i and COMPRESS != i:
            pass

def reorganize():
    #Get initial path
    os.chdir(sys.argv[1])
    directories = os.listdir()



    for actual_dir in directories:
        actual_walk = os.walk(actual_dir)
        for root,dirs,files in actual_walk:
            #print(actual_dir)
            #other_names(dirs)
            create_dirs(root,dirs)
            break
    
    #delete_extra_dirs(root)
    #create_dirs()


if __name__ == "__main__":
    reorganize()





"""
for a in directories:
    for root,sub_dirs,files in os.walk(a):
        print("|-",root)

        for i in files:
            print("|   |-",i)
        
        if(len(sub_dirs) != 0):
            for i in sub_dirs:
                print("|   |-",i)
                for j in os.listdir(root+i): #error aquí
                    print("|      |-",j)

            #print(root,sub_dirs)
    print("|")
    
#        print(sub_dirs)
"""
