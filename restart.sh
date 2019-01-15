# restart.sh
#
# Script to check restart clashcallerbot scripts.
#
# Notes:
# * Remember to set executable mode with ``chmod +x ./restart.sh``
# * Script assumes files are in the `clashcallerbotreddit` directory.
#   * If you have access to root, check the Docs for info on setting up systemd instead
# * Logfile can be removed if not necessary (remove variable and ``>> $logfile``)
# * ``python3`` can be replaced with relevant python version
# * The function in ``kill` returns all script PIDs, so it must be restarted.
#   * If you have access to ``pidof``, you can avoid killing all script instances
#

python3='./env/bin/python3'

logfile='./logs/clashcallerbotlog.txt'

echo "Restarting reply.py: $(date)" >> $logfile
kill $(ps aux | grep '[p]ython3 -m clashcallerbotreddit.reply' | awk '{print $2}')
sleep 3
nohup $python3 -m clashcallerbotreddit.reply > /dev/null 2>&1 &


echo "Restarting search.py: $(date)" >> $logfile
kill $(ps aux | grep '[p]ython3 -m clashcallerbotreddit.search' | awk '{print $2}')
sleep 3
nohup $python3 -m clashcallerbotreddit.search > /dev/null 2>&1 &
