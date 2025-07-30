def to_binaire(number):
    binaire = 0
    i = 1
    while number > 0:
        binaire += (number % 2) * i
        number //= 2
        i *= 10
    return binaire

def compte_mots(mots):
    occurence = {}
    for mot in mots:
        if mot in occurence:
            occurence[mot] += 1
        else:
            occurence[mot] = 1
    return occurence

def compte_mots_position(mots):
    mot_unique = []
    position = []
    for mot in mots:
        if mot not in mot_unique:
            mot_unique.append(mot)
    for mot in mot_unique:
        for i, mot2 in enumerate(mots):
            if mot2 == mot:
                position.append(i)
    return  mot_unique,position

def is_secure_mdp_1(mot_de_passe):
    score_maj = 0
    score_min = 0
    score_num = 0
    score_spec = 0
    for i,c in enumerate(mot_de_passe):
        if ord(c) >= ord("A") and ord(c) <= ord("Z"):
            score_maj += 1
        if ord(c) >= ord("a") and ord(c) <= ord("z"):
            score_min += 1
        if ord(c) >= ord("0") and ord(c) <= ord("9"):
            score_num += 1
        if 47 >= ord(c) and ord(c) <= 33:
            score_spec += 1
    if score_maj >= 1 and score_min >= 1 and score_num >= 1 and score_spec >= 1:
        return True
    return False, score_maj , score_min , score_num , score_spec

def is_secure_mdp_2(mot_de_passe):
    list_spec_charactere = ["!","@","#","$","%","^","&","*","(",")","_","+",".",",",";","?","/","#","="]
    if len(mot_de_passe) < 8:
        return False
    if not any(c.isupper() for c in mot_de_passe):
        return False
    if not any(c.islower() for c in mot_de_passe):
        return False
    if not any(c.isdigit() for c in mot_de_passe):
        return False
    if not any(c in list_spec_charactere for c in mot_de_passe):
        return False
    return True

def is_palindrome(mot):
    mot = mot.lower()
    mot = mot.replace(" ","")
    if mot == mot[::-1]:
        return True
    return False

def read_file(file_name):
    with open (file_name , "r", encoding="utf-8") as filout :
        while filout.readline() != "" :
            note = filout.readline()
            print(note)

def make_graphe(dataset , nb_col = 1, nb_ligne = 1, width = 10, height = 10):
    plt.figure(figsize=(width,height))
    ligne = 1
    col = 1
    for i in range(len(dataset)):
        # print(ligne , "--" , col, "--" , i+1)
        plt.subplot(nb_ligne, nb_col, i+1)
        plt.title(i+1)
        plt.plot(dataset[i])
        col += 1
        if col > nb_col:
            col = 1
            ligne += 1
    plt.show()
