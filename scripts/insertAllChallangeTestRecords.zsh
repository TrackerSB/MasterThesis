#!/bin/zsh
SOURCE="${(%):-%N}"
while [ -h "$SOURCE" ]; do
    currentDir="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$currentDir/$SOURCE"
done
currentDir="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

challengeTestDataDir="$currentDir/../data/challengeTests/"

consideredTestDirs=(
    "2019-10-10_1"
    "2019-10-11_1"
    "2019-10-11_2"
    "2019-10-12_1"
    "2019-10-12_2"
    "2019-10-12_3"
    "2019-10-13_1"
    "2019-10-14_1"
    "2019-10-14_2"
    "2019-10-15_1"
    "2019-10-15_2"
    "2019-10-15_3"
    "2019-10-15_4"
    "2019-10-15_5"
    "2019-10-16_1"
    "2019-10-16_2"
    "2019-10-16_3"
    "2019-10-18_1"
)
for dir in $consideredTestDirs; do
    "$currentDir/insertTestRecord.zsh" "$challengeTestDataDir/$dir"
    # Make sure dependant data that the first call skipped is inserted
    "$currentDir/insertTestRecord.zsh" "$challengeTestDataDir/$dir"
done
