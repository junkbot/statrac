# stat[O]rac by Junkbot
# 6 Oct 12
# requires texttable

import re
import getpass
import urllib, urllib2, cookielib
import sys
from texttable import Texttable

# for reverse sorting purposes (ceebs writing cmp)
BIG_NUMBER = 1000000

def print_all_stats(stats):
    print "General Stats:"
    table = Texttable()
    table.add_row(["Username", "Problems Completed", "Sets Completed", "Problems Remaining", "Sets Remaining"])
    for s in sorted(stats, key=lambda x:x[6])[::-1]:
        table.add_row([s[0],
                       "%d / %d (%.2lf%%)" % (s[4], s[5], s[6]),
                       "%d / %d (%.2lf%%)" % (s[1], s[2], s[3]),
                       s[7],
                       s[8]])
    print table.draw()
    print

def print_undone(undone):
    print "Uncompleted problems you have access to that others have completed:"
    table = Texttable()
    table.add_row(["Problem", "Users Completed"])
    undone_list = [[u, sorted(undone[u])] for u in undone.keys()]
    for u in sorted(undone_list, key=lambda x:(BIG_NUMBER-len(x[1]), x[1], x[0])):
        table.add_row([u[0], ' '.join(u[1])])
    print table.draw()
    print 

def get_probs_stats(html_data):
# maps id to (name, status)
    setNames = {}
    sets = {}

    setPattern = re.compile('class="expfirst"><a name="(.*?)">(.*?)</a>')
    setResults = setPattern.findall(html_data)
    for m in setResults:
        setNames[m[0]] = [m[1], True]
        sets[m[0]] = []

# get all problems
    probPattern = re.compile('problem.pl\?set=(.*?)\&problemid=(.*?)">(.*?)</a></td><td class="exp">(.*?)</td>')
    probResults = probPattern.findall(html_data)

# maps id to (name, status)
    problems = {}

    for m in probResults:
        setid = m[0]
        probid = int(m[1])
        probName = m[2].replace('&#39;',"'")
        status = m[3]

        problems[probid] = [probName, status]
        sets[setid].append(probid)
        if "Finished" not in status:
            setNames[setid][1] = False

# analysis
    num_sets = len(sets)
    num_probs = len(problems)
    completed_probs = []

    for p in problems:
        if "Finished" in problems[p][1]:
            completed_probs.append(problems[p][0])

    completed_sets = []
    for s in setNames:
        if setNames[s][1]:
            completed_sets.append(s)

    percent_sets_completed = float(len(completed_sets)) / float(num_sets) * 100.0
    percent_probs_completed = float(len(completed_probs)) / float(num_probs) * 100.0

    data = [len(completed_sets), num_sets, percent_sets_completed, len(completed_probs), num_probs, percent_probs_completed, num_probs-len(completed_probs), num_sets - len(completed_sets)]
    return (problems, data)

def main():
# outputs what others have done that you haven't
    if len(sys.argv) > 1:
        access = set()
        done = set()
        undone = {}

        usernameRe = re.compile('^(.*?)\..*$')

        all_stats = []

        for i in xrange(1, len(sys.argv)):
            user = usernameRe.match(sys.argv[i]).group(1)
            f = open(sys.argv[i], "r")
            html_data = f.read()
            f.close()
            
            probs, stats = get_probs_stats(html_data)
            stats = [user] + stats
            all_stats.append(stats)

            if i == 1:
                probNames = dict(probs)
                for p in probs:
                    access.add(p)
                    if "Finished" in probs[p][1]:
                        done.add(p)
            else:
                for p in probs:
                    if "Finished" in probs[p][1] and p in access and p not in done:
                        if p not in undone:
                            undone[p] = []
                        undone[p].append(user)

        print_all_stats(all_stats)

        undone_list = map(lambda x: (probNames[x][0], x), undone.keys())
        undone_list.sort()
        named_undone = {}

        for u in undone_list:
            named_undone[u[0]] = tuple(undone[u[1]])
        
        print_undone(named_undone)
    else:
# get login details
        sys.stderr.write('Username: ')
        username = raw_input().strip()
        password = getpass.getpass('Password: ')

# get HTML data
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_data = urllib.urlencode({'login_username' : username, 'login_password' : password, 'login_submit' : 'Log in'})
        opener.open('http://orac.amt.edu.au/jaz/cgi-bin/train/index.pl', login_data)
        resp = opener.open('http://orac.amt.edu.au/jaz/cgi-bin/train/hub.pl?expand=all&setshowdone=1')
        html_data = resp.read()
        print html_data

        probs, your_stats = get_probs_stats(html_data)
        print_stats(your_stats)

if __name__ == "__main__":
    main()
