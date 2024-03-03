l = input(str(""))
l = l.split()
l = list(map(lambda x: type(eval(x)), l))
print(l)