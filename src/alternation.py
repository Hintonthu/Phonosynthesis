import csv, z3, sys, argparse
import phonosynth, ipa_data, parse_ipa
data = []
alt_forms = []

def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputDirectory',
                    help='Path to the input directory.')
    parser.add_argument('--outputDirectory',
                    help='Path to the output that contains the results.')
    return parser

arg_parser = create_arg_parser()
parsed_args = arg_parser.parse_args(sys.argv[1:])
fname = parsed_args.inputDirectory

with open(fname) as rf:
    reader = csv.reader(rf)
    for row in reader:
        if row[0] != "U":
            data.append(''.join(row))
        elif row[0] == "U":
            alt_forms.append((row[1],row[2]))

def generate_alternating_form(data,source,fst,snd):
    possible_config = []
    def replaceInList(l, original, new):
        return [new if x == original else x
                for x in l ]
    for example in data:
        phonemes = [u"".join(ps) for ps in parse_ipa.group_phones(example)]
        nexample = [u"".join(replaceInList(phonemes,source[i][fst],source[i][snd]))
                    for i in range(len(source)) if source[i][fst] in phonemes]
        if len(nexample) == 0:
            possible_config.append(example)
        if len(nexample) == 1:
            possible_config.append(nexample[0])
        elif len(nexample) >= 2:
            possible_config.append(nexample[-1])
    return possible_config

configA = generate_alternating_form(data,alt_forms,0,1)
configB = generate_alternating_form(data,alt_forms,1,0)
wordsA = list(zip(configA,data))
wordsB = list(zip(configB,data))
print(wordsA)
print(wordsB)

def get_rules(words):
    data = phonosynth.parse(words)
    changes = phonosynth.infer_change(data)
    rules = phonosynth.infer_rule(data, changes)
    return rules

def num_rules(rules):
    return(len(rules))

def num_features(rule):
    num_condition = 0
    num_change = len(rule[0].simplified_change.keys())
    for dictionary in rule[1]:
        count = len(dictionary.keys()) 
        num_condition += count
    total_features = num_change + num_condition
    return(total_features)

def select_rule(r1,r2):
    if not r1:
        return r2
    if None in r1:
        return r2
    elif not r2:
        return r1
    if None in r2:
        return r1
    rA = num_rules(r1)
    rB = num_rules(r2)
    if rA > rB:
        return r2
    elif rA < rB:
        return r1
    elif rA == 1 and rB == 1:
        if num_features(r1[0]) > num_features(r2[0]):
            return r2[0]
        elif num_features(r1[0]) < num_features(r2[0]):
            return r1[0]
        else:
            return r2[0]
    else:
        fA = 0
        fB = 0
        for r in r1:
            fA += num_features(r)
        for r in r2:
            fB += num_features(r)
        if fA > fB:
            return r2
        elif fB > fA:
            return r1


if __name__ == "__main__":
    rules1 = get_rules(wordsA)
    rules2 = get_rules(wordsB)
    rule = select_rule(rules1,rules2)
    if rule and len(rule) > 0 and rule[0]:
        print("Successfully discovered rule:\n", rule)
    else:
        print("Could not discover rule.")


