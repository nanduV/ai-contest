# compile_anything.py
# Author: Jeff Cameron (jeff@jpcameron.com)
#
# Auto-detects the language of the entry based on the extension,
# attempts to compile it, returning the stdout and stderr.
# The auto-detection works by looking for the "main" code file of
# the available languages. If the number of matching languages is 0 or
# more than 1, it is an error, and an appropriate error message is returned.
#
# To add a new language you must add an entry to the "languages" dictionary in
# the following format:
#   LanguageName : (extension, [NukeGlobs], [(Compile_globs, Compile_class)])
#
# For example the entry for Python is as follows:
#   "Python" : (".py", ["*.pyc"], [("*.py", ChmodCompiler("Python"))]).
# This defines the extension as .py, removes all .pyc files, and runs all the
# found .py files through the ChmodCompiler, which is a pseudo-compiler class
# which only chmods the found files.
#
# If you want to run a real compiler then you need to define a set of flags to
# send it. In this case you would either use TargetCompiler or ExternalCompiler.
# The difference between the two is the TargetCompiler iterates over the found
# files and creates object files from them, whereas the External doesn't.
# If in doubt just stick to the ExternalCompiler.
#
# An example is from the C# Entry:
#   "C#" : (".exe", ["*.exe"],
#           [(["*.cs"], ExternalCompiler(comp_args["C#"][0]))])
#
# To make the dictionary more readable the flags have been split into a
# separate "comp_args" dictionary. C#'s entry looks like so:
#   "C#" : [["gmcs", "-warn:0", "-out:%s.exe" % BOT]]
# At runtime this all boils down to:
#   gmcs -warn:0 -out:MyBot.exe *.cs
# (though the *.cs is actually replaced with the list of files found)

import os
import re
import glob
import subprocess
import errno
import time
import shutil
import MySQLdb
from server_info import server_info

BOT = "MyBot"
SAFEPATH = re.compile('[a-zA-Z0-9_.$-]+$')

def safeglob(pattern):
  safepaths = []
  paths = glob.glob(pattern)
  for path in paths:
    if SAFEPATH.match(path):
      safepaths.append(path)
  return safepaths

def safeglob_multi(patterns):
  safepaths = []
  for pattern in patterns:
    safepaths.extend(safeglob(pattern))
  return safepaths

def nukeglob(pattern):
  paths = glob.glob(pattern)
  for path in paths:
    try:
      if os.path.isdir(path):
        shutil.rmtree(path)
      else:
        os.unlink(path)
    except OSError, e:
      if e.errno != errno.ENOENT:
        raise

def system(args):
  cmd = ' '.join(args) + "\n"
  proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  (out, err) = proc.communicate()
  return cmd + out, err

def check_path(path):
  if not os.path.exists(path):
    return "\nFailure: output file " + str(path) + " was not created.\n"
  else:
    return ""

class Compiler:
  def compile(self, globs):
    raise NotImplementedError

class ChmodCompiler(Compiler):
  def __init__(self, language):
    self.language = language

  def compile(self, globs):
    err = ""
    for f in safeglob_multi(globs):
      try:
        os.chmod(f, 0644)
      except Exception, e:
        err += "Error chmoding %s - %s\n" % (f, e)
    return self.language + " scripts do not need to be compiled.\n", err

class ExternalCompiler(Compiler):
  def __init__(self, args, separate=False):
    self.args = args
    self.separate = separate

  def compile(self, globs):
    out, err = "", ""
    files = safeglob_multi(globs)
    if self.separate:
      for file in files:
        tout, terr = system(self.args + [file])
        out += tout
        err += terr
    else:
      tout, terr = system(self.args + files)
      out += tout
      err += terr
    return out, err

# Compiles each file to its own output, based on the replacements dict.
class TargetCompiler(Compiler):
  def __init__(self, args, replacements, outflag="-o"):
    self.args = args
    self.replacements = replacements
    self.outflag = outflag

  def compile(self, globs):
    sources = safeglob_multi(globs)
    out, err = "", ""
    for source in sources:
      for old_ext, new_ext in self.replacements.iteritems():
        i = source.rfind(old_ext)
        if i >= 0:
          target = source[:i] + new_ext
          break
      else:
        err += "Could not determine target for source file %s.\n" % source
        continue
      tout, terr = system(self.args + [self.outflag, target, source])
      out += tout
      err += terr

comp_args = {
  # lang : ([list of compilation arguments], ...)
  #        If the compilation should output each source file to
  #        its own object file, don't include the -o flags here,
  #        and use the TargetCompiler in the languages dict.
  "C"       : [["gcc", "-O3", "-funroll-loops", "-c"],
               ["gcc", "-O2", "-lm", "-o", BOT]],
  "C#"      : [["gmcs", "-warn:0", "-out:%s.exe" % BOT]],
  "C++"     : [["g++", "-O3", "-funroll-loops", "-c"],
               ["g++", "-O2", "-lm", "-o", BOT]],
  "Go"      : [["/usr/local/bin/6g", "-o", "_go_.6"],
               ["/usr/local/bin/6l", "-o", BOT, "_go_.6"]],
  "Haskell" : [["ghc", "--make", BOT + ".hs", "-O2", "-v0"]],
  "Java"    : [["javac"],
               ["jar", "cfe", BOT + ".jar", BOT]],
  "Lisp"    : [['sbcl', '--end-runtime-options', '--no-sysinit',
                '--no-userinit', '--disable-debugger', '--load',
                BOT + '.lisp', '--eval', "(save-lisp-and-die \"" + BOT
                + "\" :executable t :toplevel #'pwbot::main)"]],
  "OCaml"   : [["ocamlbuild", BOT + ".native"]],
  }

targets = {
  # lang : { old_ext : new_ext, ... }
  "C"   : { ".c" : ".o" },
  "C++" : { ".c" : ".o", ".cpp" : ".o", ".cc" : ".o"},
  }

languages = {
  # lang : (output extension, [nukeglobs], [(source glob, compiler), ...])
  #        The compilers are run in the order given.
  #        If the extension is "" it means the output file is just BOT
  #        If a source glob is "" it means the source is part of the
  #          compiler arguments.
  "C"           : ("",
                   ["*.o", BOT],
                   [(["*.c"], TargetCompiler(comp_args["C"][0], targets["C"])),
                    (["*.o"], ExternalCompiler(comp_args["C"][1]))]),
  "C#"          : (".exe",
                   [BOT + ".exe"],
                   [(["*.cs"], ExternalCompiler(comp_args["C#"][0]))]),
  "C++"         : ("",
                   ["*.o", BOT],
                   [(["*.c", "*.cpp", "*.cc"],
                     TargetCompiler(comp_args["C++"][0], targets["C++"])),
                    (["*.o"], ExternalCompiler(comp_args["C++"][1]))]),
  "Clojure"     : (".clj",
                   [],
                   [(["*.clj"], ChmodCompiler("Clojure"))]),
  "CoffeeScript": (".coffee",
                   [],
                   [(["*.coffee"], ChmodCompiler("CoffeeScript"))]),
  "Go"          : ("",
                   ["*.6", BOT],
                   [(["*.go"], ExternalCompiler(comp_args["Go"][0]))]),
  "Haskell"     : ("",
                   [BOT],
                   [([""], ExternalCompiler(comp_args["Haskell"][0]))]),
  "Java"        : (".jar",
                   ["*.class, *.jar"],
                   [(["*.java"], ExternalCompiler(comp_args["Java"][0])),
                    (["*.class"], ExternalCompiler(comp_args["Java"][1]))]),
  "Javascript"  : (".js",
                   [],
                   [(["*.js"], ChmodCompiler("Javascript"))]),
  "Lisp"        : (".sbcl",
                   [BOT, BOT + ".sbcl"],
                   [([""], ExternalCompiler(comp_args["Lisp"][0]))]),
  "Lua"         : (".lua",
                   [],
                   [(["*.lua"], ChmodCompiler("Lua"))]),
  "OCaml"       : (".native",
                   [BOT + ".native"],
                   [([""], ExternalCompiler(comp_args["OCaml"][0]))]),
  "Perl"        : (".pl",
                   [],
                   [(["*.pl"], ChmodCompiler("Perl"))]),
  "PHP"        : (".php",
                   [],
                   [(["*.php"], ChmodCompiler("PHP"))]),
  "Python"      : (".py",
                   ["*.pyc"],
                   [(["*.py"], ChmodCompiler("Python"))]),
  "Ruby"        : (".rb",
                   [],
                   [(["*.rb"], ChmodCompiler("Ruby"))]),
  "Scheme"      : (".ss",
                   [],
                   [(["*.ss"], ChmodCompiler("Scheme"))]),
  }


def compile_function(language):
  info = languages[language]
  extension = info[0]
  nukeglobs = info[1]
  compilers = info[2]

  out, err = "", ""

  for glob in nukeglobs:
    nukeglob(glob)

  for globs, compiler in compilers:
    tout, terr = compiler.compile(globs)
    out += tout
    err += terr

  err += check_path(BOT + extension)
  return out, err

def get_programming_languages():
  connection = MySQLdb.connect(host = server_info["db_host"],
                               user = server_info["db_username"],
                               passwd = server_info["db_password"],
                               db = server_info["db_name"])
  cursor = connection.cursor(MySQLdb.cursors.DictCursor)
  cursor.execute("SELECT * FROM languages")
  programming_languages = cursor.fetchall()
  cursor.close()
  connection.close()
  return programming_languages

# Autodetects the language of the entry in the current working directory and
# compiles it.
def compile_anything():
  output = ""
  error = ""
  programming_languages = get_programming_languages()
  detected_langs = [
    lang for lang in programming_languages \
      if os.path.exists(lang["main_code_file"])
  ]
  # If no language was detected
  if len(detected_langs) == 0:
    error += "The auto-compile environment could not locate your main code\n"
    error += "file. This is probably because you accidentally changed the\n"
    error += "name of your main code file. You must include exactly one file\n"
    error += "with one of the following names:\n"
    for lang in programming_languages:
      error += "   * " + lang["main_code_file"] + " (" + lang["name"] + ")\n"
    error += "This is to help the auto-compile environment figure out which\n"
    error += "programming language you are using.\n"
    return output, error, "NULL"
  # If more than one language was detected
  if len(detected_langs) > 1:
    error = "The auto-compile environment found more than one main code "
    error += "file:\n"
    for lang in detected_langs:
      error += "   * " + lang["main_code_file"] + " (" + lang["name"] + ")\n"
    error += "You must submit only one of these files so that the "
    error += "auto-compile environment can figure out which programming "
    error += "language you are trying to use.\n"
    return output, error, "NULL"
  # If we get this far, then we have successfully auto-detected the language
  # that this contestant is using.
  main_code_file = detected_langs[0]["main_code_file"]
  detected_lang = detected_langs[0]["name"]
  language_id = detected_langs[0]["language_id"]
  output += "Found " + main_code_file + ". Compiling this entry as " + \
    detected_lang + "\n"
  t1 = time.time()
  out, err = compile_function(detected_lang)
  output += "Completed in %f seconds.\n" % (time.time() - t1)
  output += out
  error += err
  return output, error, language_id
