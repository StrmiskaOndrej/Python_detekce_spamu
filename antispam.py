#!/usr/local/bin/python3
# -*- coding: utf-8 -*- 

import sys
from email import policy
from email.parser import BytesParser
import html2text

if (len(sys.argv) != 1):
    with open('spamWords.txt', encoding='utf-8') as f:
        lines = f.readlines()
    spamSlova = [line.rstrip('\n') for line in open('spamWords.txt')]

    with open('spamWords2.txt', encoding='utf-8') as fi:
        lines = fi.readlines()
    spamSlova2 = [line.rstrip('\n') for line in open('spamWords2.txt')]

    with open('spamPhrases.txt', encoding='utf-8') as f:
        lines = f.readlines()
    spamFraze = [line.rstrip('\n') for line in open('spamPhrases.txt')]

    with open('spamAddress.txt', encoding='utf-8') as f:
        lines = f.readlines()
    spamAdresati = [line.rstrip('\n') for line in open('spamAddress.txt')]
else:
    print("Nebyl uveden žádný soubor")
    
argument = 1
while(argument < len(sys.argv)):
    skore = 1
    with open(sys.argv[argument], 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)
    text = ""
    text2= ""
    try:
        try:
            text = msg.get_body(preferencelist=('plain')).get_content() # čistý text
            #print("metoda 1")  
        except:
            if msg.is_multipart():
                for payload in msg.get_payload():
                    #print("metoda 2a")
                    # if payload.is_multipart(): ...
                    text2 = payload.get_payload()
            else:
                text2 = msg.get_payload()
                #print("metoda 2b")
            text = html2text.html2text(text2)          
    except:
        text = ""
    #print(text2)
    text = text.replace('\n',' ')
    #print(text)
    odesilatel = msg['from'] # odesílatel
    prijemce = msg['to'] # příjemce
    predmet = msg['subject'] # předmět
    datum = msg['date'] # datum
    #print ('To: %s' % prijemce) # příjemce
    #print ('From: %s' % odesilatel) # odesílatel
    #print ('Subject: %s' % predmet) # předmět
    #print ('Date: %s' % datum) # datum
    #print(text) # čistý text
    #print(msg) # celý text
    slova = text.split()
    slovaVPredmetu = predmet.split()
    pocetSlovCelkem = len(slova)
    #print(slova)
    #print("počet slov celkem = "+ str(pocetSlovCelkem))

    oduvodneni ="\nzákladní skóre = 1"

    pocetSpamSlovVTextu=0
    pocetSpamSlovVPredmetu=0
    spamSlovaVTextu = ""
    
    for x in spamSlova:
        if(x in slova):
            #print("spam slovo v textu = "+x)
            spamSlovaVTextu = spamSlovaVTextu +" - "+ x
            pocetSpamSlovVTextu=pocetSpamSlovVTextu+1
        if(x in slovaVPredmetu):
            #print("spam slovo v předmětu = "+x)
            skore = skore + 2
            oduvodneni = oduvodneni + "\nskore + 2, za slovo v předmětu: " + x

    for x in spamSlova2:
        for y in slova:
            if(x in y):
                #print("spam slovo v textu = "+x)
                spamSlovaVTextu = spamSlovaVTextu +" - "+ x
                pocetSpamSlovVTextu=pocetSpamSlovVTextu+2.5
        if(x in predmet):
            #print("spam slovo v předmětu = "+x)
            skore = skore + 3.5
            oduvodneni = oduvodneni + "\nskore + 3.5, za slovo v předmětu: " + x

    skores = 0        
    if(pocetSpamSlovVTextu > 2):
        podilSpamSlov = pocetSlovCelkem / pocetSpamSlovVTextu
        if(podilSpamSlov <= 10):
            skores = 6
        elif(podilSpamSlov <= 20):
            skores = 5
        elif(podilSpamSlov <= 35):
            skores = 4
        elif(podilSpamSlov <= 45):
            skores = 3
        elif(podilSpamSlov <= 70):
            skores = 2
        else:
            skores = 1
        skore = skore + skores
        oduvodneni = oduvodneni + "\nskóre + "+ str(skores) + " za spamová slova v textu.\nSeznam spamových slov v textu = " + spamSlovaVTextu
        #print(oduvodneni)   
    elif(pocetSpamSlovVTextu != 0):
        podilSpamSlov = pocetSlovCelkem / pocetSpamSlovVTextu
        if(podilSpamSlov <= 10):
            skores = 3.5
        elif(podilSpamSlov <= 45):
            skores = 2
        else:
            skores = 1
        skore = skore + skores
        oduvodneni = oduvodneni + "\nskóre + "+ str(skores) + " za spamová slova v textu.\nSeznam spamových slov v textu = " + spamSlovaVTextu
        
    pocetSpamFrazi=0
    for x in spamFraze:
        #print(x)
        if(x in text):
            oduvodneni = oduvodneni + "\nskore + 2, za frázi v textu: " + x
            skore = skore + 2
        if(x in predmet):
            skore = skore + 3
            oduvodneni = oduvodneni + "\nskore + 3, za frázi v předmětu: " + x
                        
    for x in spamAdresati:
        if(x in odesilatel):
            skore = skore +2
            oduvodneni = oduvodneni + "\nskore + 2, za odesíláte v spam listu"
            #print("Spam adresát = "+x)
    if(predmet.isupper()):
        #print('Předmět velkýma = srážka')
        skore = skore +2
        oduvodneni = oduvodneni + "\nskore + 2, za předmět velkýma písmenama"
        
    if("?" in predmet or "!" in predmet or "@" in predmet):
        skore = skore +1
        oduvodneni = oduvodneni + "\nskore + 1, za zavináč, otazník, či vykřičník v předmětu"
    if("http" in predmet):
        #print('odkaz v předmětu = srážka')
        skore = skore +1
        oduvodneni = oduvodneni + "\nskore + 1, za odkaz v předmětu"
    pocetMSG = len(msg)
    pocetPismenSHtml = len(text2)
    pocetPismenBezHtml = len(text)
    #print(pocetPismenSHtml)
    #print(pocetPismenBezHtml)

    if(pocetPismenSHtml > (pocetPismenBezHtml)*10):
        #print("příliš moc html")
        skore = skore +1
        oduvodneni = oduvodneni + "\nskore + 1, za příliš mnoho html znaků"
    if("This email must be viewed in HTML mode" in text):
        skore = skore +6
        oduvodneni = oduvodneni + "\nskore + 6, pouze html náhled"
    
    #print("název souboru: "+ sys.argv[argument])
    
    #print("celkové skóre:" + str(skore))
    #print(oduvodneni)
    #oduvodneni = ""
    if(pocetPismenBezHtml == 0):
        print(sys.argv[argument] + ",výsledek = FAIL" + ", email se nepodařilo rozparsovat")
    elif(skore <= 6):
        print(sys.argv[argument] + ",výsledek = OK" + ", email dosáhl skóre: " + str(skore) + oduvodneni)
    else:
        print(sys.argv[argument] + ",výsledek = SPAM" + ", email dosáhl skóre: " + str(skore) + oduvodneni)
    argument = argument + 1
