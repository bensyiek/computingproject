from PIL import Image

Image.open('Cynthia.gif').resize((18*4+1,18*4+1)).save('Cynthia3.png')

##downsize resolution stays good when, for a number abcdefghi... where a->etc. are
##prime numbers, we downsize to n1 * n2 * n3 ... * nk + 1 where n1->nk are prime
##factors of abcdefghi...
##idk if this is right, this is just a guess idk
