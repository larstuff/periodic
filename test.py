csvdata = []
delim = ';'
with open('assets/periodesystem_delvis_oversatt2.csv', 'r', encoding="utf8") as file:
    line_nr = 0
    for line in file:
        csvdata.append(line.rstrip('\n').rstrip('\r').split(delim))

for line in csvdata[1:119]:
    print(line[:11])
