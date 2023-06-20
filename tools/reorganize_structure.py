import os,sys


def move_files(root,dir,files):
    for i in files:
        print(root)
        if "partituras" not in root and ".pdf" in i:
            os.rename(root+"/"+i,root+"/partituras/"+i)
        elif "extras" not in root and ".pdf" not in i:
            os.rename(root+"/"+i,root+"/extras/"+i)
    
#Error eliminando los dirs
def delete_extra_dirs(root,dirs,files):
    print("HELLO")
    if "extras" in root:
        try:
            os.removedirs(root+"/partituras")
            os.removedirs(root+"/compress")
        except FileNotFoundError:
            print("NOOOO")
    if "compress" in root:
        try:
            os.removedirs(root+"/partituras")
            os.removedirs(root+"/extras")
        except FileNotFoundError:
            print("NOOOO")         
    if "partituras" in root:
        try:
            os.removedirs(root+"/compress")
            os.removedirs(root+"/extras")
        except FileNotFoundError:
            print("NOOOO")    


#Create the empty dirs for the basic structure
def create_dirs():
    directories = os.listdir()
    r = 0
    for actual_dir in directories:
        actual_walk = os.walk(actual_dir)
        for root,dirs,files in actual_walk:
            #Create dirs
            if "partituras" not in dirs and "partituras" not in root and "compress" not in root and "extras" not in root:
                os.makedirs(root+"/partituras",exist_ok=True)
            
            if "extras" not in dirs and "extras" not in root and "compress" not in root and "partituras" not in root:
                os.makedirs(root+"/extras",exist_ok=True)
        
            if "compress" not in dirs and "compress" not in root and "partituras" not in root and "extras" not in root:
                os.makedirs(root+"/compress",exist_ok=True)
            
            move_files(root,dirs,files)
            delete_extra_dirs(root,dirs,files)
            r+=1
            if r > 3:
                exit()


def main():
    #Get initial path
    os.chdir(sys.argv[1])

    create_dirs()


if __name__ == "__main__":
    main()





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
