#!/usr/bin/python

# regex
import re
# executing commands
import subprocess
# arguments
import argparse
# to exit
import sys
import operator


def setupTrackingForAllRelevantRemoteBranches(lessonNum=None):
    allRemotes = subprocess.check_output(['git', 'branch', '-a'])
    allRemotes = allRemotes.split(' ')

    if lessonNum is None:
        regexForExerciseOrSolutionBranch = r'(S\d\d\.\d\d-(?:Exercise|Solution)-\w*)'
    elif lessonNum > 9:
        regexForExerciseOrSolutionBranch = r'(T1{}.\d\d-(?:Exercise|Solution)-\w*)'.format(str(lessonNum % 10))
    else:
        regexForExerciseOrSolutionBranch = r'(T\d{}\.\d\d-(?:Exercise|Solution)-\w*)'.format(str(lessonNum))

    for remote in allRemotes:
        # replace remotes/origin if it's in the string with ''
        if 'remotes/origin/' in remote:
            remote = remote.replace('remotes/origin/', '').strip()
            if re.match(regexForExerciseOrSolutionBranch, remote):
                subprocess.call(['git', 'checkout', remote])


def gitBranch():
    return subprocess.check_output(['git', 'branch'])


def gitLogOneline():
    log = subprocess.check_output('git log --oneline'.split())
    return log


def gitNewBranch(branch_name):
    subprocess.call('git branch {}'.format(branch_name).split())


def gitDeleteBranch(branch_name):
    subprocess.call('git branch -D {}'.format(branch_name).split())


def gitRenameBranch(old_name, new_name):
    subprocess.call('git branch -m {} {}'.format(old_name, new_name).split())


def gitCheckout(branch_or_sha):
    subprocess.call('git checkout {}'.format(branch_or_sha).split())


commit_creator_description = (
    'Create a clean commit history for Sunshine or a Toy App. If no arguments are specified,'
    'a clean commit history of all lessons in Sunshine will be created. Note, that for this'
    ' program to work, branches in the following form must exist:'
    '(S|T)\d\d\.\d\d-(Exercise|Solution)-\w'
)
parser = argparse.ArgumentParser(description=commit_creator_description)
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--sunshine',
                   action='store_true',
                   help='Use this flag to designate you want to generate step branches '
                        'from Sunshine\'s clean commit history')
group.add_argument('-t', '--toyapp',
                   action='store_true',
                   help='Use this flag to designate you want to generate step branches '
                        'from a Toy App\'s clean commit history (requires a lesson number as well)')
parser.add_argument('-l', '--lesson',
                    help='Which lesson do you want to generate step branches for?',
                    type=int)
args = parser.parse_args()
print args.sunshine
print args.toyapp
print args.lesson

lessonNum = args.lesson

setupTrackingForAllRelevantRemoteBranches()
allBranches = gitBranch()
print allBranches

if lessonNum:
    print 'Do toy app, lesson ' + str(lessonNum)
    print 'T0{}.\d\d-(?:Exercise|Solution)-\w*'.format((str(lessonNum)))
    onSunshine = False
    regex = r'T0{}.\d\d-(?:Exercise|Solution)-\w*'.format((str(lessonNum)))
    clean_branch_name = 't{}-clean-history'.format(str(lessonNum))
else:
    print 'Do all of Sunshine'
    onSunshine = True
    regex = r'S\d\d.\d\d-(?:Exercise|Solution)-\w*'
    clean_branch_name = 'sunshine-clean-history'

gitCheckout(clean_branch_name)

log = gitLogOneline().splitlines()
# print log

commit_dict = {}
for line in log:
    l = re.split('\s', line, maxsplit=1)
    sha = l[0]
    msg = l[1]
    if re.match(regex, msg):
        commit_dict[msg] = sha

sorted_commits = sorted(commit_dict.items(), key=operator.itemgetter(0))

for msg, sha in sorted_commits:
    # If the clean branch already exists, back it up and delete it
    if msg in allBranches:
        backup_name = 'BACKUP-' + msg
        if backup_name in allBranches:
            gitDeleteBranch(backup_name)
        gitRenameBranch(msg, backup_name)
    gitCheckout(sha)
    gitNewBranch(msg)

# After everything is all done, checkout the clean branch again
gitCheckout(clean_branch_name)