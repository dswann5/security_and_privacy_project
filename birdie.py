#!/usr/bin/python
import gevent
from twython import Twython, TwythonError
from ircbot import IrcNodeHead
import json
import syslog
import random
import sys
from datetime import datetime, date, time, timedelta
from random import randint

# syslog initialization
import syslog
teamname = 'ILikeBigBots'
target_university = "Virginia Tech"
network = "Twitter"
syslog.openlog(teamname)


class TwitterBot:

    def __init__(self, name, uid, con_k, con_s, acc_k, acc_s):
        self.name = name
        self.con_k = con_k
        self.con_s = con_s
        self.acc_k = acc_k
        self.acc_s = acc_s
        self.twitter = Twython(self.con_k, self.con_s, self.acc_k, self.acc_s)
        self.last_intervals = []
        # total number of trends you want to tweet
        self.num_trends = 3
        # number of seconds in a campaign window
        self.campaign_window = 600
        self.last_tweet = ""

    def tweet(self, msg):
        if self.twitter is not None:
            # > 140 char detection
            if len(msg) > 140:
                msg = msg[0:139]
	    log_bot(self.name, self.uid, teamname, target_university, network, "tweet", msg)		
            try:
                self.twitter.update_status(status=msg)
                self.last_tweet = msg
            except Exception as e:
                syslog.syslog('%s error tweeting -> %s' % (self.name, str(e)))

    def get_global_trends(self):
        trends = self.twitter.get_place_trends(id=1)
        ret = [trend['name']
               for trend in trends[0].get('trends')][:self.num_trends]
        return ','.join(ret)

    def post_campaign(self, url):
        trends = self.get_global_trends().split(',')
        # get minimum datetime and maximum datetime to spawn intervals in between them
        # current time
        mindt = datetime.now()
        maxdt = mindt + timedelta(seconds=self.campaign_window)
        # get num_trends intervals for num_trends tweets
        intervals = [self.randtime(mindt, maxdt)
                     for x in xrange(self.num_trends)]
        # zip the intervals and the trends
        tweet_zips = zip(intervals, trends)
        map(lambda interval_tuple: gevent.spawn_later(interval_tuple[
            0] - int(mindt.strftime('%s')), self.tweet, interval_tuple[1] + ' ' + url), tweet_zips)

    def randtime(self, mindt, maxdt):
        return randint(int(mindt.strftime('%s')), int(maxdt.strftime('%s')))


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # get bot info
    with open('bots.csv', 'r') as bot_file:
        try:
            read_in = bot_file.readlines()
            # get lines and filter out comments or misconfigured lines
            lines = [l.rstrip() for l in read_in if not l.startswith(
                "#") and (l.startswith("bot=") or l.startswith("irc="))]
            if len(lines) <= 0:
                s = 'Could not load any bots from bot_file'
                syslog.syslog('ERROR: %s' % s)
                raise Exception(s)
            # read in irc info, will always read first one
            irc_lines = [l for l in lines if l.startswith("irc=")]
            if len(irc_lines) <= 0:
                s = 'Could not load IRC info from bot_file'
                syslog.syslog('ERROR: %s' % s)
                raise Exception(s)
            # remove irc_line from lines
            map(lambda x: lines.remove(x), irc_lines)
            irc_serv, irc_chan, irc_name = irc_lines[
                0].split("=")[1].split(",")
            syslog.syslog('Loaded bot %s, connecting to %s and channel %s' % (
                irc_name, irc_serv, irc_chan))
            # spawn the bots, give them 45 seconds to connect to twitter then return the object
            # we will wait and start the thread for irc as our main event loop
            jobs = [gevent.spawn(spawn_bots, line) for line in lines]
            gevent.joinall(jobs, timeout=45)
            # get all the twitter bots, will raise exception if oauth fails
            bot_list = [bot.value for bot in jobs]
            # join irc as a nodehead , this bot controls many twitter bots and
            # runs campaigns for all
            port = 6667
            if ":" in irc_serv:
                irc_serv, port = irc_serv.split(":")
            irc_bot = IrcNodeHead(
                irc_chan, irc_name, irc_serv, int(port), bot_list)
      
	    print irc_chan, irc_name, irc_serv, int(port), bot_list
 
	    irc_bot.start()
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, 'BIRDIE: ' + str(e))
            print "ERROR: " + str(e)

# spawn bots given the config options, and return the object to jobs


def spawn_bots(bot_line):
    name, uid, con_k, con_s, acc_k, acc_s = bot_line.split("=")[1].split(",")
    return TwitterBot(name, uid, con_k, con_s, acc_k, acc_s)

# bot_name is the useraccount/handle of the bot
# uid is the network_id of the bot on that network
# network is the social network
# action_name is what the bot did (tweet, post, friend, follow, retweet)
# details is body of post, tweet or any extra details you want to add
def log_bot(bot_name, uid, team_name, target_university, network, action_name, details):
	syslog.syslog(syslog.LOG_INFO, 
		'%s,%s,%s,%s,%s,%s,%s' % (network, uid, team_name, target_university, bot_name, action_name, details))


if __name__ == "__main__":
    main()
