#!/bin/zsh
SOURCE="${(%):-%N}"
while [ -h "$SOURCE" ]; do
    currentDir="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$currentDir/$SOURCE"
done
currentDir="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

scalabilityTestDataDir="$currentDir/../data/scalabilityTest_laptop/"

consideredTestDirs=(
    "2019-11-01_2"
    "2019-11-01_3"
    "2019-11-01_4"
    "2019-11-01_5"
    "2019-11-01_6"
    "2019-11-01_7"
    "2019-11-01_8"
    "2019-11-01_9"
    "2019-11-01_10"
    "2019-11-01_11"
)
for dir in $consideredTestDirs; do
    "$currentDir/insertTestRecord.zsh" "$scalabilityTestDataDir/$dir"
    # Make sure dependant data that the first call skipped is inserted
    "$currentDir/insertTestRecord.zsh" "$scalabilityTestDataDir/$dir"
done
