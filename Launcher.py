import json
import re
import string
import nltk

from ModelRunner import run_model

def sbd_component(doc):
    for i, token in enumerate(doc[:-2]):
        # define sentence start if period + titlecase token
        if token.text == '.' and doc[i+1].is_title:
            doc[i+1].sent_start = True
        if token.text == '-' and doc[i+1].text != '-':
            doc[i+1].sent_start = True
    return doc

def parsetypelist(masterfile, type_list):

    file1 = open(masterfile, 'r')
    lines = file1.readlines()
    linecount = 0
    casemap = dict()
    labelmap = dict()
    for line in lines:
        if linecount > 0:
            line = line.strip()
            sstr = line.split(",")
            part = sstr[24].upper()
            case_id = sstr[0]
            isFound = False

            if len(type_list) > 0:
                for type in type_list:
                    if type.upper() == part:
                        isFound = True
            else:
                isFound = True

            if isFound:
                casemap[case_id] = part
                if part in labelmap:
                    labelmap[part] += 1
                else:
                    labelmap[part] = 1

        linecount += 1

    labelmap = sorted(labelmap.items(), key=lambda x: x[1], reverse=True)
    return casemap, labelmap

def multiNumber(numberList, firstline):

    for number in numberList:
        if firstline.startswith(number):
            return True

    return False

def lm_gross_dump():


    count = 0

    wft = open('path.train.raw', "w")
    wfv = open('path.test.raw', "w")

    json_master_file_path = '/Users/cody/Desktop/copath_data/grossfinal/master.json'

    with open(json_master_file_path) as json_file:
        data = json.load(json_file)
        for case in data:
            gross_strings = case['gross_description']
            if count <= 90000:
                wft.write(gross_strings)
            elif (count > 90000) and (count <= 99486):
                wfv.write(gross_strings)
            count += 1
    wft.close()
    wfv.close()
    print(count)


def gross_parse(casemap, outputfile, partlimit):


    partCountMap = dict()

    type_list = []

    wf = open(outputfile, "w")

    json_master_file_path = '/Users/cody/Desktop/copath_data/grossfinal/master.json'

    single_part = []
    multipart_count = []
    broken = []
    unknown = []

    multiNumberList = ["TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE","TEN"]

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    with open(json_master_file_path) as json_file:
        data = json.load(json_file)

        for case in data:
            case_id = case['case_id']
            if case_id in casemap:
                lines = case['gross_description'].splitlines()
                isSinglePart = False
                isMultiPart = False
                isBroken = False

                # print(lines)
                if len(lines) > 0:
                    firstline = lines[0].upper();

                    # multi
                    if firstline.startswith("A: "):
                        isMultiPart = True
                    elif firstline.startswith("A. "):
                        isMultiPart = True
                    elif firstline.startswith("A."):
                        isMultiPart = True
                    elif firstline.startswith("A; "):
                        isMultiPart = True
                    elif firstline.startswith("A1: "):
                        isMultiPart = True
                    elif firstline.startswith("A) "):
                        isMultiPart = True
                    elif firstline.startswith("PART A "):
                        isMultiPart = True
                    elif firstline.startswith("TOTAL NUMBER OF SPECIMENS"):
                        isMultiPart = True
                    elif firstline.startswith("TOTAL SPECIMEN NUMBER"):
                        isMultiPart = True
                    elif firstline.startswith("SPECIMEN A "):
                        isMultiPart = True
                    elif firstline.startswith("THE SPECIMENS "):
                        isMultiPart = True
                    elif firstline.startswith("SPECIMENS RECEIVED "):
                        isMultiPart = True
                    elif multiNumber(multiNumberList, firstline):
                        isMultiPart = True

                    # broken
                    elif firstline.startswith("{NOT ENTERED}"):
                        isBroken = True

                    # single
                    elif firstline.startswith("THE SPECIMEN "):
                        isSinglePart = True
                    elif firstline.startswith("SPECIMEN IS "):
                        isSinglePart = True
                    elif firstline.startswith("RECEIVED IN "):
                        isSinglePart = True
                    elif firstline.startswith("RECEIVED IS "):
                        isSinglePart = True
                    elif firstline.startswith("RECEIVED FRESH "):
                        isSinglePart = True
                    elif firstline.startswith("THE CASE IS RECEIVED IN ONE PART"):
                        isSinglePart = True
                    elif firstline.startswith("RECEIVED FRESH "):
                        isSinglePart = True
                    elif firstline.startswith("SPECIMEN WAS RECEIVED "):
                        isSinglePart = True
                    elif firstline.startswith("SPECIMEN RECEIVED IN "):
                        isSinglePart = True
                    elif firstline.startswith("ONE SPECIMEN "):
                        isSinglePart = True
                    elif firstline.startswith("ONE PART."):
                        isSinglePart = True
                    elif firstline.startswith("SPECIMEN NUMBER: ONE"):
                        isSinglePart = True
                    elif firstline.startswith("A "):
                        isSinglePart = True

                    # unknown
                    # else:
                    #    print(firstline)


                    type = casemap[case_id]
                    if type not in type_list:
                        type_list.append(type)

                    if isSinglePart:
                        single_part.append(case_id)

                        '''
                        phrases = re.findall('"([^"]*)"', case['gross_description'])
                        if len(phrases) > 0:
                            phrase = phrases[0].lower()
                            phrase = re.sub(r'\d+', '', phrase)
                            #exclude = set(string.punctuation)
                            #phrase = phrase.join(ch for ch in phrase if ch not in exclude)
                            phrase = phrase.replace(" cm ", "")
                            phrase = phrase.replace(" x ", "")

                            if len(phrase) > 5:
                                wf.write(phrase + "\t" + str(type_list.index(type)) + "\n")

                        '''
                        '''
                        sentences = tokenizer.tokenize(case['gross_description'])
                        for s in sentences:

                            #s = case['gross_description']
                            strlen = len(nltk.word_tokenize(s))

                            # if strlen > 425:
                            #    sentences = tokenizer.tokenize(case['gross_description'])
                            #    s = sentences[0]

                            s = s.replace("\"", "")
                            s = s.replace("The specimen is received in formalin labeled ", "")
                            s = s.replace("Specimen is received in formalin labeled ", "")
                            s = s.replace("\t", " ").replace("\n", " ")
                            s = s.replace(" cm ", "")
                            s = s.replace(" x ", "")

                            s = s.replace(".", "")
                            s = s.replace("-", "")

                            exclude = set(string.punctuation)
                            s = ''.join(ch for ch in s if ch not in exclude)

                            s = re.sub(r'\d+', '', s)
                            s = s.lower()

                            if (len(s) > 25):
                                if type in partCountMap:
                                    if not (partCountMap[type] > partlimit):
                                        partCountMap[type] += 1
                                        wf.write(s + "\t" + str(type_list.index(type)) + "\n")
                                else:
                                    partCountMap[type] = 1
                                    wf.write(s + "\t" + str(type_list.index(type)) + "\n")

                        '''

                        s = case['gross_description']


                        strlen = len(nltk.word_tokenize(s))

                        if strlen > 375:
                            sentences = tokenizer.tokenize(case['gross_description'])
                            s = sentences[0]

                        s = s.replace("\"", "")
                        s = s.replace("The specimen is received in formalin labeled ", "")
                        s = s.replace("Specimen is received in formalin labeled ", "")
                        s = s.replace(" cm ", "")
                        s = s.replace(" x ", "")

                        s = s.replace("\t", " ").replace("\n", " ")
                        s = s.replace(".", "")
                        s = s.replace("-", "")

                        exclude = set(string.punctuation)
                        s = ''.join(ch for ch in s if ch not in exclude)

                        s = re.sub(r'\d+', '', s)
                        #s = s.lower()

                        if (len(s) > 25):
                            if type in partCountMap:
                                if not (partCountMap[type] > partlimit):
                                    partCountMap[type] += 1
                                    wf.write(s + "\t" + str(type_list.index(type)) + "\n")
                            else:
                                partCountMap[type] = 1
                                wf.write(s + "\t" + str(type_list.index(type)) + "\n")


                    elif isMultiPart:
                        multipart_count.append(case_id)

                        '''
                        phrases = re.findall('"([^"]*)"', case['gross_description'])
                        if len(phrases) > 0:
                            phrase = phrases[0].lower()
                            phrase = re.sub(r'\d+', '', phrase)
                            #exclude = set(string.punctuation)
                            #phrase = phrase.join(ch for ch in phrase if ch not in exclude)
                            phrase = phrase.replace(" cm ", "")
                            phrase = phrase.replace(" x ", "")

                            if len(phrase) > 5:
                                wf.write(phrase + "\t" + str(type_list.index(type)) + "\n") 
                        '''

                        '''
                        s = case['gross_description']
                        strlen = len(nltk.word_tokenize(s))

                        if strlen > 425:
                            sentences = tokenizer.tokenize(case['gross_description'])
                            s = sentences[0]


                        s = s.replace("\"", "")
                        s = s.replace("The specimen is received in formalin labeled ", "")
                        s = s.replace("Specimen is received in formalin labeled ", "")
                        s = s.replace("\t", " ").replace("\n", " ")
                        s = s.replace(" cm ", "")
                        s = s.replace(" x ", "")

                        s = s.replace(".", "")
                        s = s.replace("-", "")

                        exclude = set(string.punctuation)
                        s = ''.join(ch for ch in s if ch not in exclude)

                        s = re.sub(r'\d+', '', s)
                        s = s.lower()

                        if (len(s) > 25):
                            if type in partCountMap:
                                if not (partCountMap[type] > partlimit):
                                    partCountMap[type] += 1
                                    wf.write(s + "\t" + str(type_list.index(type)) + "\n")
                            else:
                                partCountMap[type] = 1
                                wf.write(s + "\t" + str(type_list.index(type)) + "\n")
                    '''
                    elif isBroken:
                        broken.append(case_id)
                    else:
                        unknown.append(case_id)


    print(type_list)
    total = len(single_part) + len(multipart_count) + len(broken) + len(unknown)
    print("\n")
    print("Total Cases: " + str(total))
    print("Single Part: " + str(len(single_part)) + " " + str(round((len(single_part)/total)*100)) + "%")
    print("Multi Part: " + str(len(multipart_count)) + " " + str(round((len(multipart_count)/total)*100)) + "%")
    print("Broken Gross: " + str(len(broken)) + " " + str(round((len(broken)/total)*100)) + "%")
    print("Unknown Gross: " + str(len(unknown)) + " " + str(round((len(unknown)/total)*100)) + "%")
    wf.close()
    print("type_count: " + str(len(type_list)))

    print(partCountMap)
    return sorted(partCountMap.items(), key=lambda x: x[1], reverse=True)

def main():

    #create gross wordlist
    masterfile = "/Users/cody/Desktop/copath_data/master.csv"
    #type_list = ["ESO", "ESOBX", "STOBX", "COLONBX1","BRES"]

    #lm_gross_dump()

    '''
    type_list = []
    casemap, labelmap = parsetypelist(masterfile, type_list)
    for label in labelmap:
        if label[1] > 1:
            #print(str(label[1]) + "->" + label[0])
            type_list.append(label[0])
    '''

    #exit(0)
    #10 list, 188 labels, 1% , max 460, epoc 4
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'TISDIAG', 'GB', 'APP', 'COLONBX1', 'HEARTTP', 'ESOBX', 'NBB', 'TISNON', 'HERNIA', 'STOBX', 'RECBX1', 'CXBX', 'FALLSTER', 'PLAT', 'ECC1', 'SHAVE1', 'BONE', 'ENDOME', 'TONS', 'LUNGTP', 'LIVNB', 'SDSTY-138', 'VALVE', 'TONSILS', 'FORESK', 'SC', 'DUOBX', 'LN', 'BBT', 'POC', 'AMPEX', 'VAS', 'BOWNT', 'SDSTY-116', 'VULBX', 'BLTUR', 'PLAQUE', 'SKINN', 'CYST', 'BBNON', 'PTH', 'VAGBX', 'THYROIDNT', 'CNOS', 'AMP T', 'LIP', 'SKINTU', 'CUSAT', 'FMHEAD', 'CLOT', 'BRTRES', 'HEART TX', 'VOCBX', 'ANT', 'LUNG TX', 'CAP', 'STOMA', 'KID-BX', 'HEM', 'SDSTY-26', 'TONGBX', 'BONBX', 'FIS', 'DEB', 'LIVTUM', 'SIN BX', 'KID', 'G-CYST', 'BX-LAR', 'CXLP', 'TURB', 'PROSBX', 'UTNON', 'COND', 'MB', 'PLACOTH', 'OMNON', 'KIDNEY', 'PAR', 'AMPU', 'ANUS', 'VUL', 'SKINPLA', 'VES', 'HEMA', 'PILO', 'EYE', 'SPL', 'LIVTX', 'BRES', 'OVBEN', 'STAP', 'COLONTUMO', 'PANC-BX', 'AMP F', 'UTP', 'TONSBX', 'TIS07', 'LIPBX', 'MAR', 'PITT', 'UTNEO', 'SG', 'CHO', 'MLB', 'AN', 'LUNGWNT', 'LNLRG', 'KIDTR', 'SEP', 'SYNCYST', 'OVC', 'ANAS2', 'PROSTUR', 'LEI', 'URBX', 'HEARTNOS', 'PHAR', 'LUNGWG', 'LN DIS', 'DM', 'SYN', 'PLEBX', 'KIDNT', 'HS', 'SCAR', 'BREBX', 'ECTOPC', 'HIDZ', 'TWIN', 'CORN', 'TA BX', 'HEARTENDO', 'GRAN', 'OVAR-B', 'PLEURA', 'AMPTRA', 'OMBX', 'ADR', 'MLG', 'APPY', 'PTY', 'SLN', 'GRT', 'BONF', 'PERBX', 'FHPATH', 'BRMAR', 'DUCTCYST', 'OMTUM', 'COLOS', 'PALATE', 'BONE RES', 'LIVER TX', 'SDSTY-145', 'DENCYS', 'TESOTH', 'STL', 'LIVRES', 'LUNGRESNON', 'OV', 'SNB', 'UREBX', 'BRRES', 'HYD', 'THYI', 'TRA', 'THYOTH', 'STONON', 'DIV', 'SOFTSIM', 'NEU', 'SOFTEXT', 'SD', 'STOTUM', 'LN DISLEV', 'MTR', 'NA', 'FAS', 'SPINC', 'BRT', '"FT', 'NERVE', 'TONR']
    #25 list, 129 labels, 25%, max 460, epoc 4
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'TISDIAG', 'GB', 'APP', 'COLONBX1', 'HEARTTP', 'ESOBX', 'NBB', 'TISNON', 'HERNIA', 'STOBX', 'RECBX1', 'CXBX', 'FALLSTER', 'PLAT', 'ECC1', 'SHAVE1', 'BONE', 'ENDOME', 'TONS', 'LUNGTP', 'LIVNB', 'SDSTY-138', 'VALVE', 'TONSILS', 'FORESK', 'SC', 'DUOBX', 'LN', 'BBT', 'POC', 'AMPEX', 'VAS', 'BOWNT', 'SDSTY-116', 'VULBX', 'BLTUR', 'PLAQUE', 'SKINN', 'CYST', 'BBNON', 'PTH', 'VAGBX', 'THYROIDNT', 'CNOS', 'AMP T', 'LIP', 'SKINTU', 'CUSAT', 'FMHEAD', 'CLOT', 'BRTRES', 'HEART TX', 'VOCBX', 'ANT', 'LUNG TX', 'CAP', 'STOMA', 'KID-BX', 'HEM', 'SDSTY-26', 'TONGBX', 'BONBX', 'FIS', 'DEB', 'LIVTUM', 'SIN BX', 'KID', 'G-CYST', 'BX-LAR', 'CXLP', 'TURB', 'PROSBX', 'UTNON', 'COND', 'MB', 'PLACOTH', 'OMNON', 'KIDNEY', 'PAR', 'AMPU', 'ANUS', 'VUL', 'SKINPLA', 'VES', 'HEMA', 'PILO', 'EYE', 'SPL', 'LIVTX', 'BRES', 'OVBEN', 'STAP', 'COLONTUMO', 'PANC-BX', 'AMP F', 'UTP', 'TONSBX', 'TIS07', 'LIPBX', 'MAR', 'PITT', 'UTNEO', 'SG', 'CHO', 'MLB', 'AN', 'LUNGWNT', 'LNLRG', 'KIDTR', 'SEP', 'SYNCYST', 'OVC', 'ANAS2', 'PROSTUR', 'LEI', 'URBX', 'HEARTNOS', 'PHAR', 'LUNGWG', 'LN DIS', 'DM', 'SYN', 'PLEBX', 'KIDNT', 'HS']
    #50 list,90 labels, 62% ,max 460, epoc 4
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'TISDIAG', 'GB', 'APP', 'COLONBX1', 'HEARTTP', 'ESOBX', 'NBB', 'TISNON', 'HERNIA', 'STOBX', 'RECBX1', 'CXBX', 'FALLSTER', 'PLAT', 'ECC1', 'SHAVE1', 'BONE', 'ENDOME', 'TONS', 'LUNGTP', 'LIVNB', 'SDSTY-138', 'VALVE', 'TONSILS', 'FORESK', 'SC', 'DUOBX', 'LN', 'BBT', 'POC', 'AMPEX', 'VAS', 'BOWNT', 'SDSTY-116', 'VULBX', 'BLTUR', 'PLAQUE', 'SKINN', 'CYST', 'BBNON', 'PTH', 'VAGBX', 'THYROIDNT', 'CNOS', 'AMP T', 'LIP', 'SKINTU', 'CUSAT', 'FMHEAD', 'CLOT', 'BRTRES', 'HEART TX', 'VOCBX', 'ANT', 'LUNG TX', 'CAP', 'STOMA', 'KID-BX', 'HEM', 'SDSTY-26', 'TONGBX', 'BONBX', 'FIS', 'DEB', 'LIVTUM', 'SIN BX', 'KID', 'G-CYST', 'BX-LAR', 'CXLP', 'TURB', 'PROSBX', 'UTNON', 'COND', 'MB', 'PLACOTH', 'OMNON', 'KIDNEY', 'PAR', 'AMPU', 'ANUS', 'VUL', 'SKINPLA', 'VES', 'HEMA', 'PILO']
    # 100-300 list, 71 labels, 94%, epoc 6, biobert 1.1
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'GB', 'APP', 'VALVE', 'TISDIAG', 'LIVNB', 'COLONBX1', 'HEARTTP', 'NBB', 'HERNIA', 'SDSTY-138', 'STOBX', 'TISNON', 'CXBX', 'PLAT', 'SKINN', 'RECBX1', 'LUNGTP', 'FORESK', 'ESOBX', 'ENDOME', 'BONE', 'TONS', 'TONSILS', 'ECC1', 'DUOBX', 'KID-BX', 'AMPEX', 'SHAVE1', 'AMP T', 'POC', 'PLAQUE', 'VULBX', 'FMHEAD', 'BLTUR', 'BOWNT', 'CYST', 'PTH', 'DEB', 'LIP', 'LN', 'VAGBX', 'SDSTY-116', 'HEM', 'CLOT', 'STOMA', 'CUSAT', 'THYROIDNT', 'CNOS', 'ANT', 'MB', 'EYE', 'SKINTU', 'HEART TX', 'FIS', 'SDSTY-26', 'UTNON', 'KID', 'BBNON', 'LUNG TX', 'G-CYST', 'FALLSTER', 'TONGBX', 'BONBX', 'PLACOTH', 'AMPU', 'MLB', 'VOCBX']
    # 100 list, 63 labels, 82%, epoc 4
    #type_list = ['SKIN P', 'SKINBX', 'VAGBX', 'LUNGNON', 'EMB', 'CYST', 'GB', 'APP', 'POC', 'VALVE', 'TISDIAG', 'LIVNB', 'COLONBX1', 'HEARTTP', 'G-CYST', 'NBB', 'LIP', 'HERNIA', 'SDSTY-138', 'AMPEX', 'BLTUR', 'STOBX', 'CLOT', 'KID-BX', 'TISNON', 'THYROIDNT', 'LN', 'CXBX', 'HEM', 'FMHEAD', 'PLAT', 'SKINN', 'CNOS', 'FALLSTER', 'ECC1', 'SHAVE1', 'PLAQUE', 'DEB', 'RECBX1', 'FIS', 'LUNGTP', 'FORESK', 'ESOBX', 'BOWNT', 'LUNG TX', 'ENDOME', 'DUOBX', 'SDSTY-26', 'BONE', 'PTH', 'SKINTU', 'ANT', 'VULBX', 'TONS', 'SDSTY-116', 'HEART TX', 'AMP T', 'CUSAT', 'MB', 'BBNON', 'TONGBX', 'BONBX', 'TONSILS']
    # 100 list, 54 labels, 92%, epoc 4
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'TISDIAG', 'GB', 'APP', 'POC', 'VALVE', 'COLONBX1', 'LIVNB', 'HEARTTP', 'ESOBX', 'NBB', 'TISNON', 'HERNIA', 'SDSTY-138', 'LN', 'SC', 'STOBX', 'RECBX1', 'CXBX', 'FALLSTER', 'PLAT', 'BBT', 'ECC1', 'SHAVE1', 'LUNGTP', 'FORESK', 'BONE', 'ENDOME', 'DUOBX', 'TONS', 'TONSILS', 'AMPEX', 'VAS', 'BOWNT', 'SDSTY-116', 'VULBX', 'BLTUR', 'PLAQUE', 'SKINN', 'CYST', 'BBNON', 'PTH', 'VAGBX', 'THYROIDNT', 'CNOS', 'AMP T', 'LIP', 'SKINTU', 'CUSAT', 'FMHEAD', 'CLOT']
    #150 list 34 labels, 89%, epoc 4
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'TISDIAG', 'GB', 'APP', 'POC', 'VALVE', 'COLONBX1', 'LIVNB', 'HEARTTP', 'ESOBX', 'NBB', 'TISNON', 'HERNIA', 'SDSTY-138', 'LN', 'SC', 'STOBX', 'RECBX1', 'CXBX', 'FALLSTER', 'PLAT', 'BBT', 'ECC1', 'SHAVE1', 'LUNGTP', 'FORESK', 'BONE', 'ENDOME', 'DUOBX', 'TONS', 'TONSILS']
    # 200 list, 38 labels, % epoc, biobert 1.1
    type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'GB', 'APP', 'POC', 'VALVE', 'TISDIAG', 'LIVNB', 'COLONBX1', 'HEARTTP', 'NBB', 'HERNIA', 'SDSTY-138', 'AMPEX', 'BLTUR', 'STOBX', 'KID-BX', 'TISNON', 'CXBX', 'FMHEAD', 'PLAT', 'SKINN', 'ECC1', 'SHAVE1', 'PLAQUE', 'RECBX1', 'LUNGTP', 'FORESK', 'ESOBX', 'ENDOME', 'DUOBX', 'BONE', 'VULBX', 'TONS', 'AMP T', 'TONSILS']
    # 200 list, 31 labels, 94% epoc 4
    # 200 list, 31 labels, 95% epoc 6, lr=1e5, batch=16
    # 200 list, 31 labels, 95% epoc 6, lr=2e5, batch=32 clinical+bio
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'GB', 'APP', 'VALVE', 'TISDIAG', 'LIVNB', 'COLONBX1', 'HEARTTP', 'NBB', 'HERNIA', 'SDSTY-138', 'STOBX', 'TISNON', 'CXBX', 'PLAT', 'SKINN', 'ECC1', 'SHAVE1', 'PLAQUE', 'RECBX1', 'LUNGTP', 'FORESK', 'ESOBX', 'ENDOME', 'DUOBX', 'BONE', 'TONS', 'TONSILS']
    # 200 list, 22 labels, 91% epoc 4
    #type_list = ["SHAVE1","ENDOME","SKINBX","EMB","TISDIAG","COLONBX1","ESOBX","NBB","TISNON","STOBX","RECBX1","CXBX","SKIN","LUNGNON","GB","APP","HEARTTP","HERNIA","FALLSTER","PLAT","ECC1","BONE","TONS"]
    # 250 list,  31 labels,
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'GB', 'APP', 'VALVE', 'TISDIAG', 'LIVNB', 'COLONBX1', 'HEARTTP', 'NBB', 'HERNIA', 'SDSTY-138', 'AMPEX', 'STOBX', 'KID-BX', 'TISNON', 'CXBX', 'PLAT', 'SKINN', 'ECC1', 'RECBX1', 'LUNGTP', 'FORESK', 'ESOBX', 'ENDOME', 'DUOBX', 'BONE', 'TONS', 'TONSILS']
    # 250 list, 20 labels,
    #type_list = ["SKINBX","EMB","TISDIAG","COLONBX1","ESOBX","NBB","TISNON","STOBX","RECBX1","CXBX","SKIN","LUNGNON","GB","APP","HEARTTP","HERNIA","FALLSTER","PLAT","ECC1","BONE","TONS"]
    # 375 list, 19 labels, % epoc
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'GB', 'APP', 'TISDIAG', 'COLONBX1', 'HEARTTP', 'NBB', 'HERNIA', 'STOBX', 'TISNON', 'CXBX', 'PLAT', 'RECBX1', 'ESOBX', 'TONS', 'TONSILS']
    # 375 list, 15 labels, 94% epoc 4
    #type_list = ["SKIN", "SKINBX", "LUNGNON", "EMB", "TISDIAG", "GB", "APP", "COLONBX1", "ESOBX", "NBB", "TISNON","HERNIA", "STOBX", "RECBX1", "ECC1", "TONS"]
    # 500 list, 10 labels, 93% epoc 4
    #type_list = ["SKINBX", "EMB", "TISDIAG", "GB", "COLONBX1", "ESOBX", "NBB", "TISNON", "STOBX", "RECBX1"]

    #parts
    #1000 list, 25 labels
    #type_list = ['SKIN P', 'SKINBX', 'LUNGNON', 'EMB', 'GB', 'APP', 'TISDIAG', 'COLONBX1', 'HEARTTP', 'NBB', 'HERNIA', 'SDSTY-138', 'AMPEX', 'STOBX', 'TISNON', 'PLAT', 'SKINN', 'RECBX1', 'ESOBX', 'BOWNT', 'UTNON', 'TONS', 'SDSTY-116', 'AMP T', 'TONSILS']

    casemap, labelmap = parsetypelist(masterfile, type_list)
    outputfile = "slist.tsv"
    partcountmap = gross_parse(casemap,outputfile, 199)

    somelist = []
    for part in partcountmap:
        print(str(part[1]) + "->" + part[0])
        if part[1] >= 199:
            somelist.append(part[0])

    print(somelist)

    #run_model()

if __name__ == "__main__":
    main()