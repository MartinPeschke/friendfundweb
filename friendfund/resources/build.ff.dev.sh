set -x


SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"


export BASE_PATH=$DIR/..
export BUILD_PATH=$BASE_PATH/resources/dojo-release-1.6.1-src/util/buildscripts
export BUILD_TARGETDIR=$BASE_PATH/public/js/build
echo 'Using build path $BUILD_PATH'
echo 'Using target path $BUILD_TARGETDIR'


rm -rf $BUILD_TARGETDIR/*
cd $BUILD_PATH

./build.sh profile=ff.full action=release releaseDir=$BUILD_TARGETDIR optimize=shrinksafe layerOptimize=shrinksafe copyTests=false

cp $BUILD_TARGETDIR/dojo/dojo/dojo.js  $BUILD_TARGETDIR/dojo.js
cp $BUILD_TARGETDIR/dojo/dojo/friendfund.js  $BUILD_TARGETDIR/friendfund.js
cp $BUILD_TARGETDIR/dojo/dojo/editor.js  $BUILD_TARGETDIR/editor.js

gzip --best -c $BUILD_TARGETDIR/dojo.js > $BUILD_TARGETDIR/dojo.js.gz
gzip --best -c $BUILD_TARGETDIR/friendfund.js > $BUILD_TARGETDIR/friendfund.js.gz
gzip --best -c $BUILD_TARGETDIR/editor.js > $BUILD_TARGETDIR/editor.js.gz


