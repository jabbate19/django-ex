import json
import sys

def get_json(manual):
    try:
        return json.load(open("/opt/app-root/src/project/"+manual+'.json'))
    except:
        return None

def table( data ):
    file = ''
    man = get_json( data[0] )
    if not man:
        return "Invalid Manual!"
    if len(data)-1:
        args_split = data[1].split('.')
        size = len(args_split)
        if size != 2:
            return "Invalid Section Notation!"
        section=[]
        try:
            section = [int(num) for num in args_split]
        except ValueError:
            return "Invalid Section Notation!"
        if section[1]:
            return specific_item(man['content'][section[0]-1]['subsections'][section[1]-1],data[1])
        return specific_item(man['content'][section[0]-1],data[1])
    else:
        return items(man['content'])
            

def items(section, pre = '', start_tab=''):
    string = ''
    for sn in range(len(section)):
        loc = ''
        if pre:
            pre_split = pre.split('.')
            if int(pre_split[1]):
                loc = pre+"."+str(sn+1)
            else:
                loc = pre_split[0]+'.'+str(sn+1)
        else:
            loc = str(sn+1)+".0"
        string += start_tab + loc + ' ' + section[sn]['title'] + "\n"
        #print(string)
        if has_subsections(section[sn]):
            string += items( section[sn]['subsections'], loc, start_tab+'\t')
    return string

def specific_item(section, pre):
    string = ''
    string += pre + ' ' + section['title'] + "\n"
    if has_subsections(section):
            string += items( section['subsections'], pre, '\t' )
    return string

def has_subsections(section):
    try:
        return len(section['subsections'])
    except KeyError:
        return False

def read(data):
    manual = data[0]
    manual_json = get_json(manual)
    if not manual_json:
        return "Invalid Manual!"
    section_num = data[1]
    num_split = [ int(x) for x in section_num.split('.') ]
    if validate_section( manual, section_num ):
        out = ''
        if len(num_split) == 2:
            if num_split[1]:
                section = manual_json['content'][num_split[0]-1]['subsections'][num_split[1]-1]
                out += '__**'+section['title']+'**__'+"\n\n"
                for line in section['content']:
                    out += line + "\n"
                for sub in section['subsections']:
                    out += "\t" + "__**" + sub['title'] +'**__'+ "\n\n"
                    for line in sub['content']:
                        out += "\t" + line + "\n"
            else:
                section = manual_json['content'][num_split[0]-1]
                out += '__**' + section['title'] + '**__' + "\n\n"
                for line in section['content']:
                    out += line + "\n"
                for sub in section['subsections']:
                    out += "\t" + '__**' + sub['title'] + '**__' + "\n\n"
                    for line in sub['content']:
                        out += "\t" + line + "\n"
                    for subsub in sub['subsections']:
                        out += "\t\t" + '__**' + subsub['title'] + '**__'  + "\n\n"
                        for line in subsub['content']:
                            out += "\t\t" + line + "\n"
        else:
            subsub = manual_json['content'][num_split[0]-1]['subsections'][num_split[1]-1]['subsections'][num_split[2]-1]
            out += '__**' + subsub['title'] + '**__' + "\n\n"
            for line in subsub['content']:
                out += line + "\n"
        return out
    return "Invalid Section!"

def validate_section(manual, section):
    man = get_json(manual)
    try:
        num_split = [ int(x) for x in section.split('.') ]
    except ValueError:
        return False
    size = len(num_split)
    try:
        if size >= 2 and size <= 3:
            if not num_split[1]:
                s = man['content'][num_split[0]-1]
                return size == 2
            s = man['content'][num_split[0]-1]['subsections'][num_split[1]-1]
            if size == 3:
                s2 = s['subsections'][num_split[2]-1]
                return True
            return True
    except Exception as e:
        return False

def help(args):
    with open("/opt/app-root/src/project/"+'help.json') as f:
        h = json.load(f)
        out = ''
        if args:
            try:
                section = h[args[0]]
                out += '__**'+section['header']+'**__'+'\n'
                out += section['syntax']+'\n'
                for line in section['info']:
                    out += line + '\n'
            except:
                out = "Command " + args[0] + " not found!"
        else:
            cmds = list(h.keys())
            cmds.sort()
            for cmd in cmds:
                out += help([cmd])+'\n'
    return out

def rule( data ):
    rules = get_json("rules")
    out = ''
    rule_to_section={
        "C":"Competition",
        "RG":"General Robot",
        "RM":"Robot Mechanical",
        "RE":"Robot Electrical",
        "DS":"Driver Station",
        "RS":"Robot Software",
        "TE":"Team Scoring Element",
        "I":"Inspection",
        "S":"Safety",
        "G":"General Game",
        "GS":"Game Specific"
    }
    if data:
        if containsNumber(data[0]):
            rule_type = ''
            try:
                test = int(data[0][1])
                rule_type = data[0][0]
            except:
                rule_type = data[0][:2]
            try:
                #print(rule_type)
                rule_type = rule_to_section[rule_type]
                #print(rule_type)
                out += '**' + data[0] + '**' + '\n'
                #print(rules[rule_type])
                for line in rules[rule_type][data[0]]:
                    out += line + '\n'
            except:
                out = "Invalid Rule!"
        else:
            try:
                rule_type=rule_to_section[data[0]]
                out += '__**' + rule_type + '**__' + '\n\n'
                for rule in list(rules[rule_type].keys()):
                    out += '**' + rule + '**' + '\n'
                    for line in rules[rule_type][rule]:
                        out += line + '\n'

            except:
                out = "Invalid Rule Section!"
    else:
        for section in list(rules.keys()):
            out += "__**" + section + "**__" + '\n'
            nums = list(rules[section].keys())
            for r in range(len(nums)):
                out += nums[r]
                if r != len(list(rules[section].keys()))-1:
                    out += ', '
            out += "\n\n"
    return out

def containsNumber(value):
    for character in value:
        if character.isdigit():
            return True
    return False

def cmd( data ):
    global active
    args = data[1:].split(' ')
    main_arg = args.pop(0)
    if main_arg == "table":
        return table(args)
    elif main_arg == "read":
        return read(args)
    elif main_arg == "rule":
        return rule(args)
    elif main_arg == "help":
        return help(args)
    elif main_arg == "ping":
        return "Pong!"
    elif main_arg == "exit" and __name__ == "__main__":
        active = False
        return 'Exiting...'
    return "Invalid Command!"

if __name__ == "__main__":
    active = True
    while active:
        i = input("> ")
        print(len(cmd(i)))
#print("Final:", table('gm1 3.0'), sep='\n')
