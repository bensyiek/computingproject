from PIL import Image
e = 'lose'
E = 'battleEnd'
u = ''
blackFile = Image.open(E+'/'+e+'.png').convert('RGBA')
data = list(blackFile.getdata())
blackAlpha=250
print(blackFile.getpixel((0, 0)))
count = 0
while blackAlpha != 0:
    data = list(data)
    for i, x in enumerate(data):
        x = list(x)
        if x[3] == 0:
            continue
        else:
            x[3] = blackAlpha
            data[i] = tuple(x)
    #print(blackFile.getpixel((0,0)))
    data = tuple(data)
    blackFile.putdata(data)
    blackFile.save(E+'/'+e+str(24-count)+'.png')
    blackAlpha -= 10
    count += 1
