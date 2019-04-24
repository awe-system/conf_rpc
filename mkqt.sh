#!/bin/bash

relative_so()
{
   ldd $1 | awk '{print $3}'
}

rm tool.tar -f
post=Release
pre_path=build-generate_tool-Desktop_Qt_5_12_2_GCC_64bit2-
path=$pre_path$post
dest=$path
lddinfo="$(ldd $path/generate_tool)"
if [ $# == 1 ];then
	dest="$1"
fi
cp $path/generate_tool $dest
for so in  $(relative_so $path/generate_tool)
do
	cp $so $dest -f
done

mkdir -p $dest/platforms
cp /opt/Qt/5.12.2/gcc_64/plugins/platforms/* $dest/platforms
for so in  $(relative_so /opt/Qt/5.12.2/gcc_64/plugins/platforms/libqxcb.so)
do
	cp $so $dest -f
done

tar -zcvf tool.tar $dest exit 1
#cp tool.tar /mnt/share/5.staff/高华龙 -f
