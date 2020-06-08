debug=0
cd "$1" || exit
if [ $debug -eq 1 ]
then
  path=$(pwd)
  echo 'current path:' "$path"
fi

res=$(hexo s)
# res=$(hexo g)
# res=$(hexo d)
if [ "$res" -ne 0 ]
then
  exit "$res"
fi

