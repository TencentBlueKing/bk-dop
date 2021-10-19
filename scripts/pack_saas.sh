#!/bin/bash

APP_DIR=$1

echo "enter app dir: $1"
cd $APP_DIR || exit 1

parse_yaml() {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

[[ -f ./app.yml ]] || exit 1
echo "start parse app.yml"
eval $(parse_yaml ./app.yml "config_")

APP_CODE=$config_app_code
VERSION=$config_version
echo "parse app.yml success, app_code=$config_app_code, version=$config_version"

echo "clear old files of $APP_CODE"
rm -rf $APP_CODE
find . -name "*.pyc" -delete

echo "create app dir: $APP_CODE/src, $APP_CODE/pkgs"
mkdir -p $APP_CODE/src $APP_CODE/pkgs || exit 1

echo "rsync src"
rsync -av --exclude="$APP_CODE" \
--exclude=".*" \
--exclude="*.tar.gz" \
--exclude="frontend/" \
--exclude="scripts/" \
./ $APP_CODE/src/ || exit 1

echo "create app.yml:\n"
cp app.yml $APP_CODE/ || exit 1
echo "libraries:" >> $APP_CODE/app.yml
grep -e "^[^#].*$" requirements.txt | awk '{split($1,b,"==");printf "- name: "b[1]"\n  version: "b[2]"\n"}' >> $APP_CODE/app.yml
cat $APP_CODE/app.yml

echo "create settings_saas.py:"
cp scripts/settings_saas.py $APP_CODE/src/config/settings_saas.py || exit 1

echo "download req files to pkgs"
pip download -d $APP_CODE/pkgs/ -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com || exit 1

echo "create package"
# tar -zcvf "$APP_CODE-V$VERSION.tar.gz" $APP_CODE
# mac version
gtar -zcvf "$APP_CODE-V$VERSION.tar.gz" $APP_CODE
rm -rf $APP_CODE

echo "create saas package $APP_CODE-$VERSION.tar.gz successfully"
