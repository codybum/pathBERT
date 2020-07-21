import json

import nltk

from ModelRunner import run_model

def parsetypelist(masterfile, type_list):

    file1 = open(masterfile, 'r')
    lines = file1.readlines()
    linecount = 0
    casemap = dict()
    for line in lines:
        if linecount > 0:
            line = line.strip()
            sstr = line.split(",")
            part = sstr[24].upper()
            case_id = sstr[0]
            isFound = False
            lasttype = ""
            if len(type_list) > 0:
                for type in type_list:
                    if type.upper() in part:
                        isFound = True
                        lasttype = type
            else:
                isFound = True
            if isFound:
                casemap[case_id] = part
        linecount += 1

    return casemap

def multiNumber(numberList, firstline):

    for number in numberList:
        if firstline.startswith(number):
            return True

    return False

def gross_parse(casemap, outputfile):

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

                        #sentences = tokenizer.tokenize(case['gross_description'])
                        #s = sentences[0]
                        #s = s.replace("\"","")
                        s = case['gross_description']
                        s = s.replace("The specimen is received in formalin labeled ","")
                        s = s.replace("Specimen is received in formalin labeled ","")
                        s = s.replace("\t", " ").replace("\n", " ")
                        s = s.lower()

                        if len(s) > 25:
                            wf.write(s + "\t" + str(type_list.index(type)) + "\n")


                    elif isMultiPart:
                        multipart_count.append(case_id)

                        #sentences = tokenizer.tokenize(case['gross_description'])
                        #s = sentences[0]
                        s = case['gross_description']
                        s = s.replace("\"", "")
                        s = s.replace("The specimen is received in formalin labeled ", "")
                        s = s.replace("Specimen is received in formalin labeled ", "")
                        s = s.replace("\t", " ").replace("\n", " ")
                        s = s.replace("A: ", "")
                        s = s.lower()

                        if len(s) > 25:
                            wf.write(s + "\t" + str(type_list.index(type)) + "\n")

                        #print("[" + sentences[0] + "]")

                    elif isBroken:
                        broken.append(case_id)
                    else:
                        unknown.append(case_id)


    total = len(single_part) + len(multipart_count) + len(broken) + len(unknown)
    print("\n")
    print("Total Cases: " + str(total))
    print("Single Part: " + str(len(single_part)) + " " + str(round((len(single_part)/total)*100)) + "%")
    print("Multi Part: " + str(len(multipart_count)) + " " + str(round((len(multipart_count)/total)*100)) + "%")
    print("Broken Gross: " + str(len(broken)) + " " + str(round((len(broken)/total)*100)) + "%")
    print("Unknown Gross: " + str(len(unknown)) + " " + str(round((len(unknown)/total)*100)) + "%")
    wf.close()
    print("type_count: " + str(len(type_list)))

def main():

    #create gross wordlist
    '''
    masterfile = "/Users/cody/Desktop/copath_data/master.csv"
    type_list = ["ESO", "ESOBX", "STOBX", "COLONBX1"]
    #type_list = []
    casemap = parsetypelist(masterfile, type_list)
    outputfile = "slist.tsv"
    gross_parse(casemap,outputfile)
    '''

    run_model()



if __name__ == "__main__":
    main()