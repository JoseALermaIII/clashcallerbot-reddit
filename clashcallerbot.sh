# clashcallerbot.sh
#
# Script to check for and start clashcallerbot scripts as background processes.
#
# Notes:
# * Remember to set executable mode with `chmod +x ./clashcallerbot.sh`
# * Script assumes files are in the `clashcallerbotreddit` directory and is run as crontab in no-root setup
#   * How often to run as a crontab depends on how long you want the bot to be down/broken
#   * If you have access to root, check the Docs for info on setting up systemd instead
# * Logfile can be removed if not necessary (remove variable and `>> $logfile`)
# * `python` can be replaced with relevant python version
# * The function in `kill` returns all script PIDs, so it must be restarted.
#   * If you have access to `pidof`, you can avoid killing all script instances
#

logfile="./clashcallerbotlog.txt"

case "$(ps -ef | grep '[p]ython -m clashcallerbotreddit.reply' | wc -l)" in

0) echo "Starting reply.py: $(date)" >> $logfile
   nohup python -m clashcallerbotreddit.reply > /dev/null 2>&1 &
   ;;
1) # Normal
   ;;
*) echo "Removing duplicate reply.py: $(date)" >> $logfile
   kill $(ps aux | grep '[p]ython -m clashcallerbotreddit.reply' | awk '{print $2}')
   nohup python -m clashcallerbotreddit.reply > /dev/null 2>&1 &
   ;;
esac

case "$(ps -ef | grep '[p]ython -m clashcallerbotreddit.search' | wc -l)" in

0) echo "Starting search.py: $(date)" >> $logfile
   nohup python -m clashcallerbotreddit.search > /dev/null 2>&1 &
   ;;
1) # Normal
   ;;
*) echo "Removing duplicate search.py: $(date)" >> $logfile
   kill $(ps aux | grep '[p]ython -m clashcallerbotreddit.search' | awk '{print $2}')
   nohup python -m clashcallerbotreddit.search > /dev/null 2>&1 &
   ;;
esac
