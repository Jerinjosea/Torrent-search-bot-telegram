from __future__ import with_statement

from telegram import Update,MessageEntity,constants,ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.utils import helpers

import yts
import kickass
import piratebay

import logging
import os                                                          
  
import contextlib 
  
try: 
    from urllib.parse import urlencode           
  
except ImportError: 
    from urllib import urlencode 
try: 
    from urllib.request import urlopen 
  
except ImportError: 
    from urllib2 import urlopen 
  
import sys 
  
  
def make_tiny(url): 
    request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))     
    with contextlib.closing(urlopen(request_url)) as response:                       
        return response.read().decode('utf-8 ') 

yy = yts.yts()
kick = kickass.kickass_torrent()
pbay = piratebay.piratebay()

state = None
USING_ENTITIES = "https://www.google.com/"

PORT = int(os.environ.get('PORT', 5000))
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
#TOKEN = place your token here
def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')
    update.message.reply_text(f'Commands \n /help to view commands\n /search to search for a torrent \n\nplease read our disclaimer. By using our bot you agree with our t&c. type /disclaimer to view disclaimer and t&c')

def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'oops! an error occured')
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Commands \n /search to search for a torrent\n /disclaimer to view disclaimer and t&c\n /help to view commands \n\n ➡ You have to install any torrrent client(I recommend Flud https://play.google.com/store/apps/details?id=com.delphicoder.flud) \n\n ➡ click on magnet link which will redirect you to torrent client\n\n ➡ click + button to add torrent\n\n ➡ If bot is not responding Please wait for a few minutes\n\n\n',disable_web_page_preview=True)

def disclaimer(update: Update, context: CallbackContext) -> None:
    disclaimer = f'We are doing our best to prepare the content of this site. However, @torrentsearchenginebot cannot warranty the expressions and suggestions of the contents, as well as its accuracy. In addition, to the extent permitted by the law, @torrentsearchenginebot shall not be responsible for any losses and/or damages due to the usage of the information on our website. \nThe links contained on our bot - @torrentsearchenginebot - may lead to external sites, which are provided for convenience only. Any information or statements that appeared in these sites are not sponsored, endorsed, or otherwise approved by @torrentsearchenginebot. For these external sites, @torrentsearchenginebot cannot be held liable for the availability of, or the content located on or through it. Plus, any losses or damages occurred from using these contents or the internet generally'
    tc = f'Terms and Conditions of Use \n\nBy accessing this Search Engine, you are agreeing to be bound by these web site Terms and Conditions of Use , all applicable laws and regulations, and agree that you are responsible for compliance with any applicable local laws. These Terms apply to all visitors, users and others who access or use the Service. If you do not agree with any of these terms, you are prohibited from using or accessing this bot \n\n1. You may not use the service to violate copyrights or to break other forms of intellectual property law.\n2. You may not use the service for any illegal purposes. This includes but is not limited to the transmission or receipt of illegal material.\n3. We have no intention of recording your username or search history But your username and search keyword may be logged in case of any error.\n4. We dont collect any details nor share them with third-parties.\n5.We do not provide any kind of warranty or insurance.'
    update.message.reply_text(disclaimer)
    update.message.reply_text(tc)

def search_tittile_get(update: Update, context: CallbackContext) -> None:
    global state
    #y = yts_am()
    tittle = str(update.message.text)
    if state == 'SEARCH':
        #update.message.reply_text(f'we will search for {tittle}')
        tittle = tittle.replace(" ","%20")
        '''
        tordata = yy.search(tittle)
        for i in tordata:
            update.message.reply_text(f'{i}')
        '''
        update.message.reply_text(f'searching... please wait')
        tordata = []
        tordata.clear()
        try:
          tordata = yy.search(tittle)
          pass
        except :
          logger.warning('Update "%s" caused nothing found in yts', update)
        try:
          tordata = tordata + kick.search(tittle)
          pass
        except:
          logger.warning('Update "%s" caused nothing found in kickass', update)
          pass
        try:
          tordata = tordata + pbay.search(tittle)
          pass
        except:
          logger.warning('Update "%s" caused nothing found in kickass', update)

        print(len(tordata))
        for i in range(len(tordata)):
          if tordata[i][1] != 'N/A':
            tordata[i][1]=int(tordata[i][1])
        
        tordata = [x for x in tordata if not isinstance(x[1], str)]
        
        print(len(tordata))  
          
        tordata.sort(key=lambda x:x[1],reverse=True)

        if not tordata:
          update.message.reply_text(f'Nothing found')

        for i,j in zip(tordata,range(20)):
          bot = context.bot
          url = make_tiny(i[4])
          text = f"name:{i[0]} \nseeds:{i[1]} leechs:{i[2]} size:{i[3]} link:\n [🧲 magnet link]({url})."
          update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

        update.message.reply_text(f'Thanks for using @torrentsearchenginebot\nplease consider sharing https://t.me/torrentsearchenginebot\n type /search to search for a file')
        #'''
    state = None

def search_command(update: Update, context: CallbackContext) -> None:
    global state
    update.message.reply_text(f'Enter the name of file to search for')
    state='SEARCH'

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('hello', hello))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('search', search_command))
    dp.add_handler(CommandHandler('disclaimer', disclaimer))
    dp.add_handler(MessageHandler(Filters.text,search_tittile_get))
    dp.add_error_handler(error)

    #'''
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://torrent-search-engine-telegram.herokuapp.com/' + TOKEN)
    '''
    updater.start_polling()
    #'''
    updater.idle()

if __name__ == '__main__':
    main()
