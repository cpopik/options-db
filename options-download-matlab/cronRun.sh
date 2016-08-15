#!/bin/tcsh

setenv USER cpopik
setenv LOGNAME cpopik
setenv HOME /home/cpopik
setenv PATH ${PATH}:/bin:/usr/bin:/sbin:/usr/local/bin:/usr/local/MATLAB/R2015b/bin
setenv LANG en_US.UTF-8

matlab -nosplash -display :1 -r " run /home/cpopik/options-download/uploadOptions.m"

