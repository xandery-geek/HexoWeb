function deploy_error() {
    content=""
    printf "Username:"
    read -r content
    printf "Password:"
    read -r content
    exit "$1"
}

debug=1
res=0

cd "$1" || exit
if [ $debug -eq 1 ]
then
  path=$(pwd)
  echo 'current path:' "$path"
fi

res=$(hexo g)
if [ "$res" -ne 0 ]
then
  deploy_error "$res"
fi

res=$(hexo d)
if [ "$res" -ne 0 ]
then
  echo "quit"
  deploy_error "$res"
fi
