import datetime
from math import ceil, floor
import hashlib


LIST_OF_ALGORITHMS =[(1,"md5"),(2,"sha1"),(3,"sha224"),(4,"sha3_224"),(5,"sha256"),(6,"sha3_256"),(7,"sha384")]

testing_date = datetime.datetime(2024,5,3,2,2,5)




#function pour determiner la list initial avant de passage a function de g
def base_list_date(list0, date):
    permutation_index =date.month % len(list0)
    list1 = list0[permutation_index:] + list0[:permutation_index]
    return list1

def base_list_time(list0, date):
    permutation_index =date.hour % len(list0)
    list1 = list0[permutation_index:] + list0[:permutation_index]
    return list1

def function_de_cryptage_date(list0,date):
    nombre_iteration = date.day % len(list0)

    list1 = list0
    if nombre_iteration==0:
        return list0
    
    for i in range(1,nombre_iteration+1):
        if i <= ceil(len(list0)/2):
            nb_permutation = floor(len(list0)/2) #3
        else:
            nb_permutation = len(list0)-(i+1)

        if nb_permutation == 0:
            return list1
        j=0
        last_index = 0 #index de le dernier element permuté
        index_permutation = last_index + i #index d'element avec le quel le dernier element est permuté
        list_aux=[] #liste des index des elements permutés (concernant last_index et index_permutation)
        while(j<nb_permutation):
            if(index_permutation < len(list0) and last_index not in list_aux):
                aux = list1[last_index]
                list1[last_index] = list1[index_permutation]
                list1[index_permutation] = aux
                list_aux.append(index_permutation)
                list_aux.append(last_index)
                j+=1
                last_index+=1
                index_permutation= last_index + i
            else:
                last_index+=1
                index_permutation= last_index + i
    return list1


def function_de_cryptage_time(list0,date):
    nombre_iteration = date.minute % len(list0)
   
    list1 = list0
    if nombre_iteration==0:
        return list0
    
    for i in range(1,nombre_iteration+1):
       
        if i <= ceil(len(list0)/2):
            nb_permutation = floor(len(list0)/2) #3
        
        else:
            nb_permutation = len(list0)-(i+1)
          

        if nb_permutation == 0:
            return list1
        j=0
        last_index = 0 #index du dernier element permuté
        index_permutation = last_index + i #index d'element avec le quel le dernier element est permuté
        list_aux=[] #liste des index des elements permutés (concernant last_index et index_permutation)
       
        while(j<nb_permutation or last_index==len(list0)): #last_index==len(list0) pour empecher la déclenchement de exception.outofbounds et j<nb_permutation  c'est le nombre de permutation de cette itétration
            if(index_permutation < len(list0) and last_index not in list_aux):#if last_index is not in list_aux then index_permutation  is not in list_aux so no need to write "index_permutation not in list_aux" et(index_permutation < len(list0) empeche le declenchement de exception.ourofbounds  
                aux = list1[last_index]
                list1[last_index] = list1[index_permutation]
                list1[index_permutation] = aux
                list_aux.append(last_index)
                list_aux.append(index_permutation)
                j+=1
                last_index+=1
                index_permutation= last_index + i
            else:
                last_index+=1
                index_permutation= last_index + i
    return list1

def fonction_gdate(list0, date):
    list1 = base_list_date(list0,date)
    list1 = function_de_cryptage_date(list1,date)
    return list1

def fonction_gtime(list0, date):
    list1 = base_list_time(list0,date)
    list1 = function_de_cryptage_time(list1,date)
    return list1

#print(fonction_gdate(LIST_OF_ALGORITHMS,testing_date))

def determiner_medthode_de_cryptage(liste,hash):
    list_aux = []
    for c in hash:
        if c.isnumeric():
            list_aux.append(int(c))
    
    s=0
    for i in list_aux:
        s+=i

    index = s % len(liste)

    return liste[index][1]

testing_hash = "79dfcc5d737194467d52245cfbbba951839"



#print(determiner_medthode_de_cryptage(LIST_OF_ALGORITHMS,testing_hash))
def extract_numbers(input_string):
    # Use a list comprehension to filter out the digits and join them into a single string
    numbers = ''.join([char for char in input_string if char.isdigit()])
    return numbers


def create_empreinte(username,hash,date,liste_algo=LIST_OF_ALGORITHMS):
    assert isinstance(date,datetime.datetime)
    liste = fonction_gdate(liste_algo, date)
    liste = fonction_gtime(liste,date)
    methode_cryptage = determiner_medthode_de_cryptage(liste,hash)
    h = hashlib.new(methode_cryptage)
    hash_numbers = extract_numbers(hash)
    passed_hash = username+hash_numbers
    h.update(passed_hash.encode('utf-8'))
    return h.hexdigest()



if __name__ == "__main__":
    password = '123456'

    print(create_empreinte("mohamed",testing_hash,testing_date))

