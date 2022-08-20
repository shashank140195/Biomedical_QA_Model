'''
ERRM
4/8/2022
Made to transform bioasq files into dpr accessable format
'''
import random
#create list of .json files
#files = ['testdata']
files = ['9B5_golden']
#files = ['9B1_golden', '9B2_golden', '9B3_golden', '9B4_golden', '9B5_golden', 'training9b']



#generate negative context list, a list of 100 contexts chosen randomly from the file
def generate_context_list(inpt_n):
    '''
    Parameters: inpt_n, the name of the input file to be read and context collected from
    Returns: negative_context_list, a list of random negative contexts
    Portable: No
    '''
    
    inpt1 = open(inpt_n,"r")
    inpt1.readline() #TRUE first line is just a placeholder
    line = inpt1.readline()
    numEntries = 0
    while line != "" and line != "}":
        numEntries += 1
        #call next_set_function
        q, a, context, h, line, t = read_bioasq(inpt1)
    #close input file
    inpt1.close()

    #Base it on the possible entries, but give it a roof of 1000 to keep lists from being too large
    ncl_size = numEntries
    if ncl_size > 1000:
        ncl_size = 1000

    negative_context_list = [""] * ncl_size

    ncl_selections = [-1] * ncl_size
    for i in range(ncl_size):
        potential = random.randint(1, numEntries)
        #Don't re-use the same indexes
        while potential in ncl_selections:
            potential = random.randint(1, numEntries)
        ncl_selections[i] = potential

    inpt2 = open(inpt_n,"r")
    inpt2.readline() #TRUE first line is just a placeholder
    line = inpt2.readline()
    tracker = 0
    while line != "" and line != "}":
        tracker += 1
        #call next_set_function
        q, a, context, h, line, t = read_bioasq(inpt2)
        if tracker in ncl_selections:
            index = ncl_selections.index(tracker)
            negative_context_list[index] = random.choice(context)
            #NO empty strings allowed
            while len(negative_context_list[index]) == 0:
                negative_context_list[index] = random.choice(context)
    #close input file
    inpt2.close()

    return negative_context_list


def prep_list(line):
    '''
    Params: line, the string to turn into a list
    Return: splist, the list of strings created and formatted from line
    Portable: No. Relies heavily on bioasq only having one entry per line
    '''
    #Remove whitespace on ends
    line = line.strip()
    #Remove first word

    tempspli = line.split(":")

def biasq_line_format(inpt, bracket_count):
    '''
    Purpose: Reads a single line from bioasq in a way to support the bracket-counting method of tracking entries
    Params: inpt, a FILE pointer from pubmedqa, and bracker_count, the number of brackets seen so far
    Returns: line read, and a possibly updated bracket_count
    '''
    line = inpt.readline().strip()
    if line == "{":
        bracket_count +=1
    elif line == "}" or line == "},":
        bracket_count -=1
    return line, bracket_count

def read_bioasq(inpt):
#read_pubmedqa function
    '''
    Params: inpt, a FILE pointer from pubmedqa
    Returns: question, the question
        ansr_list, a list of strings that are collectively the answer categories
        pos_contexts, a list of strings that make up the contexts
        hard_contexts, LATER will be a list of strings that make up the hard negative contexts
        empty list, TEMPORARY replacement for hard_contexts
    '''
    bracket_count = 0
    question = ""
    typeq = ""
    ansr_list = []
    pos_contexts = []

    get_pos_context = False
    get_answers = 0

    #Loop through until we hit the end of this entry
    line, bracket_count = biasq_line_format(inpt, bracket_count)
    #Each condition is exclusive
    while bracket_count > 0:
        #If positive context
        if line == '"snippets": [':
            get_pos_context = True
        #DON'T start reading postive context right off the bat
        elif get_pos_context:
            if line =='],': #Know when to end the line
                get_pos_context = False
            else:
                splist = line.split()
                if splist[0] == '"text":':
                    pos_contexts.append(line[9:-2])
        #question comes next
        elif line.split()[0] == '"body":':
            question = line[9:-2]
        elif line[:9] == '"type": "':
            typeq = line[9:-2]
        elif line == '"exact_answer": [':
            get_answers +=1
        elif get_answers > 0:
            #If we are in the answer finding section
            if line == '[':
                get_answers +=1
            elif line == ']' or line == '],':
                get_answers -=1
            else:
                if line[-1] == ',':
                    line = line[:-1]
                if len(line[1:-1]) > 0:
                    ansr_list.append(line[1:-1])
        #Finally we can find the answers
        line, bracket_count = biasq_line_format(inpt, bracket_count)
    #return the question string, answer list, positive context, and empty list for hard contexts
    return question, ansr_list, pos_contexts, [""], line, typeq

def write_line_list(line_list, outp):
    ''' Params:
        line_list, the list of elements to be added to the list
        outp, file pointer to write to
    Notes: does not print comma or newline, and does not print title for list
    Prints like this:
        ["...", "..."]
    '''
    outp.write('[')
    first = True
    for opt in line_list:
        if first:
            first = False
        else:
            outp.write(', ')
        outp.write('"'+opt+'"')
    outp.write(']')


def next_set(inpt, out, line, negative_context_list, first):
#next_set function
    '''
    Params: inpt, a FILE pointer from pubmedqa,
        out, a string for the name of the output file we open and append
        line, a STRING that is the first line of the next set in inpt
        negative_context_list, a list of random contexts to be use as negative examples
    Returns: The last line read
    '''
    #Get the pubmedqa format into dpr ready format
    question, ansr_list, pos_contexts, hard_contexts, lastline, valueType = read_bioasq(inpt)
    #ONLY build lists of proper type
    if valueType != 'yesno' and  valueType != 'factoid':
        return lastline
    #If no answers, don't give response
    if len(ansr_list) == 0:
        return lastline
    #get a negative context list of three at random
    neg_contexts = []
    for i in range(3):
        #Get a random element
        trial_neg = random.choice(negative_context_list)
        #Keep looking until we find one NOT in our existing context list OR a repeat
        while (trial_neg in pos_contexts) or (trial_neg in neg_contexts):
            trial_neg = random.choice(negative_context_list)
        #When we find one that's a true negative context, add it
        neg_contexts.append(trial_neg)

    #open the output file
    outp = open(out,"a")
    if not first:
        outp.write(",\n")
    #write shit TODO
    outp.write("  {\n")
    outp.write('\t"question": "'+question+'",\n')
    #Answers
    outp.write('\t"answers": ')
    write_line_list(ansr_list, outp)
    outp.write(",\n")

    #positive contexts
    outp.write('\t"positive_ctxs": [')
    first = True
    #for each entry
    #TODO!!! I do not know for certain if this is an acceptable format
    #   It's the closest I could manage to get
    for text in pos_contexts:
        if first:
            outp.write('{\n')
            first = False
        else:
            outp.write(', {\n')
        outp.write('\t\t"title": "'+text+'",\n')    #We use same string for title
        outp.write('\t\t"text": "'+text+'"\n')
        outp.write('\t}')
    outp.write('],\n')

    #Negative contexts
    outp.write('\t"negative_ctxs": ')
    write_line_list(neg_contexts, outp)
    outp.write(",\n")

    #Hard Negative contexts
    outp.write('\t"hard_negative_ctxs": ')
    write_line_list(hard_contexts, outp)
    outp.write("\n")


    #close file
    outp.write('  }')
    outp.close()

    return lastline



#for each input file
for f_name in files:

    #open/create output file name
    outp = f_name+"_dpr.json"
    #Rewrite output file
    overwrite = open(outp, "w")
    overwrite.write("[\n")
    overwrite.close()

    #Create variables, and negative context list
    negative_context_list = generate_context_list(f_name+".json")

    first = True
    #open input file
    inpt = open(f_name+".json","r")
    inpt.readline() #TRUE first line is just a placeholder
    #read first line
    line = inpt.readline()
    while line != "" and line != "}":
        #If not the first entry, write a comma and newline
        #call next_set_function
        line = next_set(inpt, outp, line, negative_context_list, first)
        if first:
            first = False
        #line = inpt.readline()
        #print(line)
    #close input file
    inpt.close()

    #Add final close bracket to output file
    overwrite = open(outp, "a")
    overwrite.write("\n]")
    overwrite.close()
    print("Finished "+f_name)

