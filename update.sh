# update.sh
#
# Archives, downloads, and updates package.
#
# Notes:
# * Don't forget to set executable mode with `chmod +x ./update.sh`.
# * The `-f` and `-q` switch silence outputs to certain degrees.
#

# Make archive directory
if [ ! -d archives ]; then
    echo 'Creating archive directory...'
    mkdir ./archives
    echo '*****'
fi

# Cleanup
echo 'Housekeeping...'
if [ -e ./archives/archive2.tar.gz ]; then
	echo '  Deleting old archives...'
	rm ./archives/archive*.tar.gz
	echo '  *****'
	sleep 2
fi

if [ -e ./archives/master.zip.1 ]; then
	echo '  Deleting old source downloads...'
	rm ./archives/master.zip.*
	echo '  *****'
	sleep 2
fi

if [ -d ./archives/clashcallerbot-reddit-master ]; then
    echo '  Deleting old source files...'
    rm -r ./archives/clashcallerbot-reddit-master
    echo '  *****'
    sleep 2
fi

# Archive
echo 'Archiving...'
if [ -e ./archives/archive.tar.gz ]; then
    echo '  Archiving archive...'
    mv -f ./archives/archive.tar.gz ./archives/archive2.tar.gz
    echo '  *****'
    sleep 2
fi

echo '  Archiving folder...'
tar --warning=no-file-changed -zcf ./archives/archive.tar.gz ./
echo '  *****'
sleep 2

# Download
echo 'Downloading...'
wget -q -Parchives https://github.com/JoseALermaIII/clashcallerbot-reddit/archive/master.zip
echo '*****'
sleep 2

# Extract
echo 'Updating files...'
unzip -uoq ./archives/master -d ./archives
echo '*****'
sleep 2

# Copy
echo 'Copying files...'
cp -fur -t ./ ./archives/clashcallerbot-reddit-master/*
echo '*****'
sleep 2
echo 'done'
