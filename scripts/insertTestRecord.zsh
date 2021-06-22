#!/bin/zsh
if [[ $# -lt 1 ]]; then
    echo "You have to provide a path of sql files to run."
else
    for file in $(ls $1/*.sql); do
        psql -U stefan -d masterthesis -p 5432 -f "$file" 2>&1 | grep -vE "duplicate|already exists"
    done
fi
