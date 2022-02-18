import Launch
import logging

logging.basicConfig(level=logging.INFO)

# launch the desired bot with the parameters defined in the Configuration file
bot = Launch.bot()
logging.info(bot)
