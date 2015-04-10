file = open('ids')
file_content = file.readlines()
x = 0
y = []
for lines in file_content[0:]:
    y.append(lines)

print(y[50035])