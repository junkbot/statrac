import re
import getpass
import urllib, urllib2, cookielib

# get login details
username = raw_input('Username: ').strip()
password = getpass.unix_getpass('Password: ')

# get HTML data
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'login_username' : username, 'login_password' : password, 'login_submit' : 'Log in'})
opener.open('http://orac.amt.edu.au/jaz/cgi-bin/train/index.pl', login_data)
resp = opener.open('http://orac.amt.edu.au/jaz/cgi-bin/train/hub.pl?expand=all&setshowdone=1')
html_data = resp.read()

# get dictionary of sets

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
    probName = m[2]
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
        completed_probs.append(p)

completed_sets = []
for s in setNames:
    if setNames[s][1]:
        completed_sets.append(s)

percent_completed = float(len(completed_probs)) / float(num_probs) * 100.0

print "You have completed %d of the %d sets you have access to." % (len(completed_sets), num_sets)
print "You have completed %d of the %d problems you have access to. (%.2lf%%)" % (len(completed_probs), num_probs, percent_completed)
print "You still have %d problems left in %d sets." % (num_probs-len(completed_probs), num_sets - len(completed_sets))
