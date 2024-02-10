import json

data = {
    "firlstNamslje": ["uno","dosj","ree"],
    "selkjlkjcond":["unjo","cinco","cien"]
}
data2 = {
    "firlstNamslje": ["uno","dosj","ree"],
    "selkjlkjcond":["unjo","cinco","cien"]
}

# Writing JSON data
with open('data.json', 'w') as f:
    json.dump(data,f)
    json.dump(data2,f)
    #data1 = json.load(f)

#print(data1["second"])