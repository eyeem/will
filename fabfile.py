import os
import tempfile
from fabric.api import *

SITE_DIR = "site"
WHITELIST_DIRS = [".git",]
WHITELIST_FILES = [ ".gitignore", ]

SANITY_CHECK_PROJECT_FILES = ["fabfile.py", "setup.py", "mkdocs.yml"]
SANITY_CHECK_BUILD_FILES = ["index.html", "js", "css"]

def _splitpath(path):
    path = os.path.normpath(path)
    return path.split(os.sep)

def deploy_docs():
    # Sanity check dir.
    root_dir = os.getcwd()
    assert all([os.path.exists(os.path.join(root_dir,f)) for f in SANITY_CHECK_PROJECT_FILES])

    local("rm -rf %s" % SITE_DIR)
    local("mkdocs build")
    tempdir = tempfile.mkdtemp()

    local("mv %s/* %s" % (SITE_DIR, tempdir))
    
    current_branch = local("git rev-parse --abbrev-ref HEAD", capture=True)
    last_commit = local("git log -1 --pretty=\%B", capture=True)

    # Add the new site to build
    local("git checkout gh-pages")
    
    # Sanity check dir.
    root_dir = os.getcwd()
    assert all([os.path.exists(os.path.join(root_dir,f)) for f in SANITY_CHECK_BUILD_FILES])


    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in files:
            if not name in WHITELIST_FILES and not any([r in WHITELIST_DIRS for r in _splitpath(root)]):
                # print "removing %s" % (os.path.join(root, name))
                os.remove(os.path.join(root, name))
        for name in dirs:
            if not name in WHITELIST_DIRS and not any([r in WHITELIST_DIRS for r in _splitpath(root)]):
                # print "removing %s" % (os.path.join(root, name))
                os.rmdir(os.path.join(root, name))
    
    local("cp -rv %s/* ." % tempdir)
    local("git add -A .")
    local("git commit -m 'Auto-update of docs: %s'" % last_commit)
    local("git push")
    local("git checkout %s" % current_branch)