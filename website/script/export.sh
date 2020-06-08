# $1: markdown(m) or hexo(h)
# $2: source files directory
# $3: destination filename *.zip
cd "$2" || exit 1

if [ "$1" == 'm' ]
then
  zip -q "$3" *.md
elif [ "$1" == "h" ]
then
  zip -q -r "$3" .
else
  exit 1
fi

exit 0
