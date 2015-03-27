#!/bin/bash
### Original Author: Andrea Carlo Marini
### Email: andrea.carlo.marini@cern.ch
### Date: 08/01/2013


TMPDIR=/var/tmp
HMARGIN=0pt
VMARGIN=0pt
IMAGE=prova.pdf
FIGURE=""
SIZE=0.1
TEMPLATE=logo-template.tex

args=`getopt h:v:i:t:s: $*` ; errcode=$?; set -- $args

##For now only short options
while test -n ${1}${2} ; do
case ${1} in
	--tmpdir | -a)
		TMPDIR=${2};
		shift 2;
		;;
	--hmargin | -h)
		HMARGIN=${2};
		shift 2;
		;;
	--vmargin | -v)
		VMARGIN=${2};
		shift 2;
		;;
	--image | -i)
		IMAGE=${2};
		shift 2;
		;;
	--size | -s)
		SIZE=${2}
		shift 2;
		;;
	--template | -t)
		TEMPLATE=${2};
		shift 2;
		;;
	--) 
		shift;
		break
		;;
	
esac
done

[ -z "$1" ] && echo "No Figure given" && exit 0

FIGURE=$1

CDIR=${PWD}
mkdir $TMPDIR/aaa
cp $TEMPLATE $TMPDIR/aaa/
cp $FIGURE $TMPDIR/aaa/
cp $IMAGE $TMPDIR/aaa/

cd $TMPDIR/aaa
perl -p -i -e "s/HMARGIN/${HMARGIN}/g;" $TEMPLATE
perl -p -i -e "s/VMARGIN/${VMARGIN}/g;" $TEMPLATE
perl -p -i -e "s/FIGURE/${FIGURE}/g;" $TEMPLATE
perl -p -i -e "s/LABEL/${IMAGE}/g;" $TEMPLATE
perl -p -i -e "s/EXTRABEGIN/\\\\includegraphics[width=${SIZE}\\\\textwidth]{/g;" $TEMPLATE
perl -p -i -e "s/EXTRAEND/}/g;" $TEMPLATE

pdflatex $TEMPLATE

mv ${TEMPLATE%%.tex}.pdf ${FIGURE%%.pdf}-labeled.pdf

cp ${FIGURE%%.pdf}-labeled.pdf ${CDIR}

cd $TMPDIR
rm -r aaa
