#!/usr/bin/env bash

# http://clontz.org/blog/2014/05/08/git-subtree-push-for-deployment/
git push origin `git subtree split --prefix output src`:master --force