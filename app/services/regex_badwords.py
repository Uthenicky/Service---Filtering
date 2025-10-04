BADWORDS_REGEX = {
    "anjing": r"a+n+j+i+ng+",
    "anjg": r"a+n+j+g+",
    "anjir": r"a+n+j+i+r+",
    "anjay": r"a+n+j+a+y+",
    "anjrit": r"a+n+j+r+i+t+",
    "anjrot": r"a+n+j+r+o+t+",
    "asu": r"a+s+u+",
    "bangsat": r"b+a+n+g+s+a+t+",
    "bajingan": r"b+a+j+i+n+g+a+n+",
    "brengsek": r"b+r+e+n+g+s+e+k+",
    "kampret": r"k+a+m+p+r+e+t+",
    "kontol": r"k+[0o]+n+t+[0o]+l+",
    "kntl": r"k+n+t+l+",
    "memek": r"m+e+m+e+k+",
    "pepek": r"p+e+p+e+k+",
    "meki": r"m+e+k+i+",
    "peler": r"p+e+l+e+r+",
    "pler": r"p+l+e+r+",
    "jembut": r"j+e+m+b+u+t+",
    "tetek": r"t+e+t+e+k+",
    "titit": r"t+i+t+i+t+",
    "ngentot": r"n+g+e+n+t+[0o]+t+",
    "ngentd": r"n+g+e+n+t+d+",
    "ngewe": r"n+g+e+w+e+",
    "sange": r"s+a+n+g+e+",
    "sangean": r"s+a+n+g+e+a+n+",
    "coli": r"c+o+l+i+",
    "colmek": r"c+o+l+m+e+k+",
    "ngocok": r"n+g+o+c+o+k+",
    "bokep": r"b+o+k+e+p+",
    "porno": r"p+[0o]+r+n+[0o]+",
    "lonte": r"l+[0o]+n+t+e+",
    "jablay": r"j+a+b+l+a+y+",
    "perek": r"p+e+r+e+k+",
    "pelacur": r"p+e+l+a+c+u+r+",
    "sundal": r"s+u+n+d+a+l+",
    "fuck": r"f+u+c+k+",
    "fck": r"f+c+k+",
    "bitch": r"b+i+t+c+h+",
    "asshole": r"a+s+s+h+[0o]+l+e+",
    "dick": r"d+i+c+k+",
    "pussy": r"p+u+s+s+y+",
    "motherfucker": r"m+o+t+h+e+r+f+u+c+k+e+r+",
    "cunt": r"c+u+n+t+",
    "tai": r"t+a+i+",
    "taik": r"t+a+i+k+",
    "telek": r"t+e+l+e+k+",
    "tae": r"t+a+e+",
    "pantek": r"p+a+n+t+e+k+",
    "kehed": r"k+e+h+e+d+",
    "monyet": r"m+[0o]+n+y+e+t+",
    "goblok": r"g+[0o]+b+l+[0o]+k+",
    "tolol": r"t+[0o]+l+[0o]+l+",
    "idiot": r"i+d+i+[0o]+t+",
    "bego": r"b+e+g+[0o]+",
    "dongo": r"d+o+n+g+[0o]+"
}


import re

def contains_badword(text: str) -> list:
    found = []
    for word, pattern in BADWORDS_REGEX.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(word)
    return found