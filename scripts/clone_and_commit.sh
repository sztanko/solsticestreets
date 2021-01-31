#!/bin/bash
set -e

source=`realpath $1`
destination=`realpath $2`

project="solsticestreets"
project_host="sztanko"
project_main_branch="master"
# repo="git@github.com:$project_host/$project.git"
repo="https://$GIT_TOKEN@github.com/$project_host/$project.git"
file_location="site/cities"
reviewer="sztanko"
parent_destination="$(dirname "$destination")"
COMMIT_BRANCH="auto_osm_`date +%Y_%m_%d__%H_%M_%S`"
COMMIT_MESSAGE="[$COMMIT_BRANCH] Automatic OSM street update from `date +'%Y-%m-%d %H:%M:%S (%A)'`"

git_name="Auto commit bot"
git_email="sztanko@gmail.com"

echo "Going to clone a repo in $parent_destination, as $destination, then copy all json data from $source, then commit it to $repo, branch $COMMIT_BRANCH"



git config --global user.email "$git_name"
git config --global user.name "$git_email"
rm -rf $destination
mkdir -p $parent_destination
echo "Authenticating with git"
echo $GIT_TOKEN | gh auth login --with-token
gh repo clone $repo $destination
cd $destination
mkdir -p $file_location
rm -f $file_location/*.*json
git checkout -b $COMMIT_BRANCH
cp -r $source/*json $file_location
git add -u $file_location/
git add $file_location/*
git commit -m "$COMMIT_MESSAGE"
git push -u origin HEAD
gh pr create --title "$COMMIT_MESSAGE" --body "This is an automated commit. See clone_and_commit.sh" -f -B master -R $project_host/$project --head $project_host:$COMMIT_BRANCH --reviewer $reviewer
