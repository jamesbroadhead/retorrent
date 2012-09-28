#!/bin/bash

git checkout master
git fetch
git remote prune origin
# remove all local branches merged into master
git branch --merged master | grep -v 'master$' | xargs git branch -d
