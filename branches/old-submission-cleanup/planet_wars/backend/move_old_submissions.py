#!/usr/bin/python

# This is a script that will move 'old' submissions to another directory to
# keep the main submissions directory from reaching filesystem directory entry 
# limits.
# It keeps all submissions that haven't been compiled yet and every user's
# three most recent submissions in the main submissions directory all other
# submissions are considered old and available to move. If there are
# more than MIN_OLD old submissions then a directory named with the current
# date and time is created under OLD_DIR and all old submissions are moved
# to that directory.

import MySQLdb
import os
import os.path
import sys
import time
from collections import defaultdict

from server_info import server_info

MIN_OLD = 100
SUBMISSION_DIR = "/home/contest/ai-contest/planet_wars/submissions/"
OLD_DIR = "/home/contest/ai-contest/planet_wars/old_submissions/"

connection = MySQLdb.connect(host = server_info["db_host"],
                             user = server_info["db_username"],
                             passwd = server_info["db_password"],
                             db = server_info["db_name"])
cursor = connection.cursor(MySQLdb.cursors.DictCursor)
# select all submissions that have already been processed by the compile_daemon
cursor.execute("""
  SELECT
    s.submission_id,
    s.user_id,
    s.timestamp
  FROM submissions s
  WHERE s.status != 20
  """)
# Split the submissions up by user
users = defaultdict(list)
while True:
  row = cursor.fetchone()
  if row is None:
    break
  users[row["user_id"]].append((row["timestamp"], str(row["submission_id"])))
submission_lists = [sl for sl in users.values() if len(sl) > 3]
old_submissions = []
cur_submissions = set(os.listdir(SUBMISSION_DIR))
for submissions in submission_lists:
  submissions.sort()
  # keep all but the users 3 most recent submissions that are still in the
  # current submissions directory
  old_submissions += [s for t, s in submissions[:-3] if s in cur_submissions]
if len(old_submissions) < MIN_OLD:
  print "Not enough old submissions to move."
  sys.exit(0)

dest_dir = os.path.join(OLD_DIR,
    time.strftime("%Y-%m-%d-%H%M",time.localtime()))
print "Creating old submissions directory %s" % (dest_dir,)
os.makedirs(dest_dir)
for submission in old_submissions:
  print "Moving submission %s to old submissions directory" % (submission,)
  os.rename(os.path.join(SUBMISSION_DIR, submission),
    os.path.join(dest_dir, submission))

