#!/bin/bash

git add .
git commit -m "${1:-update}"
git push origin main
git subtree push --prefix=writing overleaf main
