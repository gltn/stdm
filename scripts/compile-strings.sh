#!/bin/bash
LRELEASE=$1
LOCALES=$2


for LOCALE in ${LOCALES}
do
    echo "Processing: stdm_${LOCALE}.ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    $LRELEASE stdm/i18n/stdm_${LOCALE}.ts
done
