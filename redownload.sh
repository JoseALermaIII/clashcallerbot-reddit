# redownload.sh
# Archives, redownloads, and sets executable mode bit of main scripts.
# Notes:
# * Don't forget to set executable mode with `chmod +x ./redownload.sh`
# * Script assumes files are all in same directory and that it is run in a no-root setup
# * The `-f` and `-q` switch silence outputs to certain degrees
#

# Archive
mv -f ./clashcallerbotreddit/reply.py ./clashcallerbotreddit/reply.py.bak
mv -f ./clashcallerbotreddit/search.py ./clashcallerbotreddit/search.py.bak
chmod -f -x ./clashcallerbotreddit/reply.py.bak
chmod -f -x ./clashcallerbotreddit/search.py.bak
echo "*****"
sleep 2

# Redownload
wget -q -Pclashcallerbotreddit https://github.com/JoseALermaIII/clashcallerbot-reddit/raw/master/clashcallerbotreddit/reply.py
echo "*****"
sleep 2
wget -q -Pclashcallerbotreddit https://github.com/JoseALermaIII/clashcallerbot-reddit/raw/master/clashcallerbotreddit/search.py
echo "*****"
sleep 2

# Set Executable
chmod -f +x ./clashcallerbotreddit/reply.py
chmod -f +x ./clashcallerbotreddit/search.py
echo "done"
