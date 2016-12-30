# redownload.sh
# Archives, redownloads, and sets executable mode bit of main scripts.
# Notes:
# * Don't forget to set executable mode with `chmod +x ./redownload.sh`
# * Script assumes files are all in same directory and that it is run in a no-root setup
# * The `-f` switch and `> /dev/null 2>&1` silence outputs to certain degrees
#

# Archive
mv -f ./clashcallerbot_reply.py ./clashcallerbot_reply.py.bak
mv -f ./clashcallerbot_search.py ./clashcallerbot_search.py.bak
chmod -f -x ./clashcallerbot_reply.py.bak
chmod -f -x ./clashcallerbot_search.py.bak
echo "*****"
ping 127.0.0.1 -c 2 > /dev/null 2>&1

# Redownload
wget https://github.com/JoseALermaIII/clashcallerbot-reddit/raw/master/clashcallerbot_reply.py > /dev/null 2>&1
echo "*****"
ping 127.0.0.1 -c 3 > /dev/null 2>&1
wget https://github.com/JoseALermaIII/clashcallerbot-reddit/raw/master/clashcallerbot_search.py > /dev/null 2>&1
echo "*****"
ping 127.0.0.1 -c 3 > /dev/null 2>&1

# Set Executable
chmod -f +x ./clashcallerbot_reply.py
chmod -f +x ./clashcallerbot_search.py
echo "done"
