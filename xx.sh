echo "Regular Expr ..."
find ./ -path ./third_party -prune -o -type f -name '*.py' -print | xargs grep --mmap -w -n "$1(*" | grep -vE '(def)' | grep -v "self.$1"
