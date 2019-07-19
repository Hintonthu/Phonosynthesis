import csv, z3, sys, argparse
import phonosynth, ipa_data

def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputDirectory',
                    help='Path to the input directory.')
    parser.add_argument('--outputDirectory',
                    help='Path to the output that contains the results.')
    parser.add_argument('--cc0',
                        default=False, action='store_true',
                        help='Constrain one of the column costs to always be 0.')
    parser.add_argument('--minimum', default=4, type=int)
    parser.add_argument('--maximum', default=19, type=int)
    return parser

arg_parser = create_arg_parser()
parsed_args = arg_parser.parse_args(sys.argv[1:])
fname = parsed_args.inputDirectory

data=[]

m = {'ø':'A', 'ʃ':'B', 'ɯ':'C', 'ʤ':'D', 'ʧ': 'E', 'ː':'F', 'ɛ':'G', 'ə':'H', 'ɑ': 'I', 'œ':'J', 'ŋ': 'K', 'ʋ':'L', 'ʌ':'M', 'ʊ':'N', 'ʦ':'P', 'æ':'Q', 'ʣ':'R', 'ʈ':'S', 'ɖ':'T', 'ʒ':'U', 'ɱ':'V', 'ɩ':'W', 'ɲ': 'Y', 'ɡ': 'g'}
diacritics = ipa_data.get_diacritics()

def convert_ipa(ipa_string,dictionary):
    nipa_string = []
    # ipa_string = ipa_string.replace('kʻ','1')
    # ipa_string = ipa_string.replace('pʰ','2')
    # ipa_string = ipa_string.replace('tʰ','3')

    lowercase_letters = {chr(lc) for lc in range(ord('a'),ord('z') + 1)}
    
    for ipa in ipa_string:
        if ipa in diacritics:
            new_key = get_key(dictionary, nipa_string[-1]) + ipa
            if new_key in dictionary:
                nipa_string[-1] = dictionary[new_key]
            else:
                dictionary[new_key] = get_unused_symbol(dictionary)
                nipa_string[-1] = dictionary[new_key]
        elif ipa in dictionary.keys():
            nipa_string.append(dictionary[ipa])
        elif ipa in lowercase_letters: # ASCII & decoded as itself
            nipa_string.append(ipa)
        else:
            dictionary[ipa] = get_unused_symbol(dictionary)
            nipa_string.append(dictionary[ipa])
    print(ipa_string," > ",nipa_string,dictionary)
    return ''.join(map(str, nipa_string))

def get_unused_symbol(d):
    possibilities = [chr(n) for n in range(ord('A'),ord('Z')+1)] + [str(n) for n in range(1,10) ] + ["!","@","$","#","^","(",")","&","%","*",";"]
    for p in possibilities:
        if p not in d.values(): return p
    assert False, "dictionary could not be made bigger"

def convert_str(string,dictionary):
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    nstring = []
    # string = string.replace('1','kʻ')
    # string = string.replace('2','pʰ')
    # string = string.replace('3','tʰ')

    for s in string:
        key = get_key(dictionary,s)
        nstring.append(key)
    return ''.join(nstring)

def get_key(dictionary,s):
    for key, value in dictionary.items():
        if s == value:
            return key
    return s

with open(fname) as rf:
    reader = csv.reader(rf)
    for row in reader:
        data.append(row)
print(data)

def generate_constraints(data):
    I = len(data[0]) # number of inflections
    
    count = 0
    cost_constraint = 0
    column_cost = [0]*I
    length_c = 0
    constraints = []
    for example in data:
        suffixes = [z3.String('suf' + chr(ord('A') + i))
                    for i in range(I) ]
        prefixes = [z3.String('pre' + chr(ord('A') + i))
                    for i in range(I) ]
        # preA = z3.String('preA')
        # preB = z3.String('preB')
        # sufA = z3.String('sufA')
        # sufB = z3.String('sufB')
        stem = z3.String('stem' + str(count))

        # 1 is associated with the prefix
        unch1 = [z3.String('unch1' + str(count) + chr(ord('A') + i))
                 for i in range(I) ]
        # 2 is associated with the suffix
        unch2 = [z3.String('unch2' + str(count) + chr(ord('A') + i))
                 for i in range(I) ]

        # unchA1 = z3.String('unch' + str(count) + 'A') 
        # unchA2 = z3.String('unch' + str(count) + 'B')

        # unchB1 = z3.String('unch' + str(count) + 'C')
        # unchB2 = z3.String('unch' + str(count) + 'D')

        ch = [z3.String('ch' + str(count) + chr(ord('A') + i))
              for i in range(I) ]

        var = [z3.String('var' + str(count) + chr(ord('A') + i))
              for i in range(I) ]
        # varA = z3.String('var' + str(count) + 'A')
        # varB = z3.String('var' + str(count) + 'B')

        # scA = z3.Int('sc'+str(count)+'A')
        # scB = z3.Int('sc'+str(count)+'B')
        sc = [z3.Int('sc' + str(count) + chr(ord('A') + i))
              for i in range(I) ]
        
        lc = z3.Int('l'+str(count))
        for v in var:
            constraints.append(z3.Length(v) <= 1)
        # constraints.append(z3.Length(varA) <= 1)
        # constraints.append(z3.Length(varB) <= 1)
        for i in range(I):
            constraints.append(z3.Concat(prefixes[i],stem,suffixes[i]) == z3.Concat(unch1[i],ch[i],unch2[i]))
        # constraints.append(z3.Concat(preA,stem,sufA) == z3.Concat(unchA1,chA,unchA2))
        # constraints.append(z3.Concat(preB,stem,sufB) == z3.Concat(unchB1,chB,unchB2))
        for i in range(I):
            if len(example[i]) == 0: continue
            constraints.append(z3.StringVal(convert_ipa(example[i],m)) == z3.Concat(unch1[i],var[i],unch2[i]))
            
        # constraints.append(z3.StringVal(convert_ipa(example[0],m)) == z3.Concat(unchA1,varA,unchA2))
        # constraints.append(z3.StringVal(convert_ipa(example[1],m)) == z3.Concat(unchB1,varB,unchB2))
        
        constraints.append(z3.Length(stem) == lc)

        for i in range(I):
            constraints.append(z3.If(ch[i] == var[i],0,1) == sc[i])
            
        #constraints.append(z3.If(chB == varB,0,1) == scB)
        
        length_c = length_c + lc

        for i in range(I):
            constraints.append(sc[i] <= 1)
        # constraints.append(scA <= 1)
        # constraints.append(scB <= 1)
        cost_constraint = cost_constraint + sum(sc)
        for i in range(I):
            column_cost[i] = column_cost[i] + sc[i]
        # column_costb = column_costb + scB 
        count += 1
    return constraints, cost_constraint, column_cost

def get_models(constraint_formula):
    model = []
    s = z3.Solver()
    s.add(constraint_formula)
    print(s.sexpr())
    if s.check() == z3.sat:
        m = s.model()
        model.append(m)
    return model

def add_cost_constraint(constraints,cost_bound,cost_constraint,column_cost):
    constraints.append(cost_constraint == cost_bound)
    if column_cost is not None:
        constraints.append(column_cost == 0) 
    models = get_models(constraints)
    constraints.remove(cost_constraint == cost_bound)
    if column_cost is not None:
        constraints.remove(column_cost == 0)
    return models

def get_rules(words):
    data = phonosynth.parse(words)
    changes = phonosynth.infer_change(data)
    rules = phonosynth.infer_rule(data, changes)
    return rules

def insert_or_delete(u,s,letter):
    nu = ""
    changed_index = [i for i in range(len(u)) if s[i] != u[i]]
    if len(changed_index) == 0:
        nu = u + letter
    else:
        i = 0
        while (i != changed_index[0] and i < len(u)):
            nu += u[i]
            print(nu)
            i = i + 1
        nu += letter
        print(nu)
        for i in range(changed_index[0],len(u)):
            nu += u[i]
            print(nu)
    return nu

def create_word(data,model):
    input_data = []
    output_data = []
    I = len(data[0])
    for count in range(len(data)):
        surface = [convert_str(str(model[z3.String('unch1' + str(count) + chr(ord('A') + i))]),m) + \
                   convert_str(str(model[z3.String('var' + str(count) + chr(ord('A') + i))]),m) + \
                   convert_str(str(model[z3.String('unch2' + str(count) + chr(ord('A') + i))]),m)
                   for i in range(I) ]
        underlying = [convert_str(str(model[z3.String('unch1' + str(count) + chr(ord('A') + i))]),m) + \
                      convert_str(str(model[z3.String('ch' + str(count) + chr(ord('A') + i))]),m) + \
                      convert_str(str(model[z3.String('unch2' + str(count) + chr(ord('A') + i))]),m)
                      for i in range(I) ]
        
        # nurA = ""
        # nurB = ""
        # nsA = ""
        # nsB = ""
        nur = [""]*I
        ns = [""]*I
        for i in range(I):
            if len(surface[i]) < len(underlying[i]) and not(any(elem in diacritics for elem in surface[i])) and not(any(elem in diacritics for elem in underlying[i])):
                ns[i] = insert_or_delete(surface[i],underlying[i],'∅')
            
        # if len(sA) < len(urA) and not(any(elem in diacritics for elem in sA)) and not(any(elem in diacritics for elem in urA)):
        #     nsA = insert_or_delete(sA,urA,'∅')
        # if len(sB) < len(urB) and not(any(elem in diacritics for elem in sB)) and not(any(elem in diacritics for elem in urB)):
        #     nsB = insert_or_delete(sB,urB,'∅')

        for i in range(I):
            if len(surface[i]) > len(underlying[i]) and not(any(elem in diacritics for elem in surface[i])) and not(any(elem in diacritics for elem in underlying[i])):
                nur[i] = insert_or_delete(underlying[i],surface[i],'∅')
        # if len(sA) > len(urA) and not(any(elem in diacritics for elem in sA)) and not(any(elem in diacritics for elem in urA)):
        #     nurA = insert_or_delete(urA,sA,'∅')
        # if len(sB) > len(urB) and not(any(elem in diacritics for elem in sB)) and not(any(elem in diacritics for elem in urB)):
        #     nurB = insert_or_delete(urB,sB,'∅')

        for i in range(I):
            if ns[i] != "":
                output_data.append(ns[i])
            else:
                output_data.append(surface[i])

        # if nsA != "":
        #     output_data.append(nsA)
        # else:
        #     output_data.append(sA)

        # if nsB != "":
        #     output_data.append(nsB)
        # else:
        #     output_data.append(sB)

        for i in range(I):
            if nur[i] != "":
                input_data.append(nur[i])
            else:
                input_data.append(underlying[i])

        # if nurA != "":
        #     input_data.append(nurA)
        # else:
        #     input_data.append(urA)

        # if nurB != "":
        #     input_data.append(nurB)
        # else:
        #     input_data.append(urB)
    words = list(zip(input_data,output_data))
    return words

def print_rule(models):
    for model in models:
        try:
            words = create_word(data,model)
            print(words)
            rules = get_rules(words)   
            if(None in rules):
                continue
            else:
                print(rules)
                return rules
        except LookupError:
            print("WARNING: z3str returned invalid symbols")
            continue


if __name__ == "__main__":
    # Make sure that we can parse the data using the phoneme inventory
    try:
        phonosynth.parse([ (x,x)
                           for xs in data
                           for x in xs ])
    except Exception as e:
        print("Parsing problem:",e)
        sys.exit(0)
    
    z3_constraints = generate_constraints(data)
    constraints = z3_constraints[0]
    cost_constraints = z3_constraints[1]
    column_cost = z3_constraints[2]
    assert len(column_cost) == len(data[0])
    for i in range(parsed_args.minimum,parsed_args.maximum + 1):
        # add the column cost constraint (when there are 2 inflections???)
        if parsed_args.cc0: ccs = column_cost
        else: ccs = [None]
        for cc in ccs:
            model = add_cost_constraint(constraints,i,cost_constraints,cc)
            
            rule = print_rule(model)
            if rule:
                print("Successful synthesis! Here is the rule:")
            print(rule)
            if rule:
                sys.exit(0)
