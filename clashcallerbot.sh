# clashcallerbot.sh
# Script to check for and start clashcallerbot scripts as background processes
# Notes:
# * Remember to set executable mode with `chmod +x ./clashcallerbot.sh`
# * Script assumes files are in same directory and is run as crontab in no-root setup
#   * How often to run as a crontab depends on how long you want the bot to be down/broken
#   * If you have access to root, check the Wiki for info on setting up systemd instead
# * Logfile can be removed if not necessary (remove variable and `>> $logfile`)
# * `python` can be replaced with relevant python version
# * The function in `kill` returns all script PIDs, so it must be restarted.
#   * If you have access to `pidof`, you can avoid killing all script instances
#

logfile="./clashcallerbotlog.txt"

case "$(ps -ef | grep '[p]ython clashcallerbot_reply.py' | wc -l)" in

0) echo "Restarting clashcallerbot_reply.py: $(date)" >> $logfile
   nohup python clashcallerbot_reply.py > /dev/null 2>&1 &
   ;;
1) # Normal
   ;;
*) echo "Remove duplicate clashcallerbot_reply.py: $(date)" >> $logfile
   kill $(ps aux | grep '[p]ython clashcallerbot_reply.py' | awk '{print $2}')
   nohup python clashcallerbot_reply.py > /dev/null 2>&1 &
   ;;
esac

case "$(ps -ef | grep '[p]ython clashcallerbot_search.py' | wc -l)" in

0) echo "Restarting clashcallerbot_search.py: $(date)" >> $logfile
   nohup python clashcallerbot_search.py > /dev/null 2>&1 &
   ;;
1) # Normal
   ;;
*) echo "Remove duplicate clashcallerbot_search.py: $(date)" >> $logfile
   kill $(ps aux | grep '[p]ython clashcallerbot_search.py' | awk '{print $2}')
   nohup python clashcallerbot_search.py > /dev/null 2>&1 &
   ;;
esac
