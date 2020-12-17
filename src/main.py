import configparser
import logging
import sys
import praw

from submission_handler import SubmissionHandler
from comment_handler import CommentHandler

__CONFIG_PATH = 'config.ini'
__MSG_PATH    = 'removal_message.txt'
__CREDENTIALS = 'RedditCredentials'
__SETTINGS    = 'Settings'
__LOGPATH     = 'debug.log'
__LOG_LEVEL   = logging.INFO

# Sets the version for the user agent:
with open('VERSION', 'r') as version:
    __VERSION = version.read()

__THREADS = ['t-1.1', 't-2.1']

config   = None # __load_config() wraps configparser errors
reddit   = None # __login() sets this to a praw.Reddit instance
settings = None # __load_settings() returns a dict of settings
logger   = None # __initialize_logger sets up logfile and stdout logging

# These will be instantiated on their own thread
submission_handler  = None
comment_handler = None


def __setup():
    '''
    Load all the correct global settings to prepare to run!
    '''

    __initialize_logger()
    __login()
    __load_settings()
    __initialize_threads()


def __initialize_logger():
    '''
    Initialize a global logger, this should print everything to stdout as well as a logfile.

    Log path can be configured with the __LOGPATH variable above.

    Logger is passed into individual threads.
    '''

    global logger

    logger         = logging.getLogger()
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler   = logging.FileHandler(__LOGPATH)
    formatter      = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', '%m/%d/%Y %I:%M:%S %p')

    logger.setLevel(__LOG_LEVEL)
    stdout_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    logger.info('TopCommentEnforcer v{} by pawptart! Beginning startup...'.format(__VERSION))


def __load_config():
    '''
    Attempt to parse the credentials from the config file.
    '''

    global config

    try:
        config = configparser.ConfigParser()
        config.read(__CONFIG_PATH)

        logger.info('Config loaded successfully...')
    except configparser.MissingSectionHeaderError as exception:
        logger.error("config.ini is invalid. Please check that Reddit credentials are present before continuing. Error details: {}".format(exception))
        sys.exit(1)


def __login():
    '''
    Obtain a global PRAW Reddit instance using configured credentials.
    '''

    global config
    global reddit

    if not config:
        __load_config()

    try:
        credentials = config[__CREDENTIALS]

        reddit = praw.Reddit(
            username      = credentials['username'],
            password      = credentials['password'],
            client_id     = credentials['clientId'],
            client_secret = credentials['clientSecret'],
            user_agent    = 'TopCommentEnforcer v{} by /u/pawptart'.format(__VERSION)
        )

        logger.info("Logged into Reddit through PRAW as /u/{}...".format(reddit.user.me()))
    except (configparser.NoSectionError, KeyError) as exception:
        logger.error("config.ini is invalid. Please check that Reddit credentials are present before continuing. Error parsing: {}".format(exception))
        sys.exit(1)


def __load_settings():
    '''
    Obtain a global settings object using configured settings.
    '''

    global settings

    if not config:
        __load_config()

    try:
        settings = config[__SETTINGS]

        with open(__MSG_PATH, 'r') as f:
            message_text = f.read()
            logger.info("Message text set to: {}".format(message_text))
            settings.update({ 'removalMessage': message_text })

        logger.info('Loaded settings...')
    except (configparser.NoSectionError, KeyError) as exception:
        logger.error("config.ini is invalid. Please check that settings are present before continuing. Error parsing: {}".format(exception))
        sys.exit(1)

def __initialize_threads():
    '''
    Initialize the stream handler threads to be used to concurrently parse comments and submission streams.
    '''

    global submission_handler, comment_handler

    submission_handler = SubmissionHandler(1, __THREADS[0], 1, reddit, settings, logger)
    logger.info("SubmissionHandler instantiated on thread [{}]...".format(__THREADS[0]))

    comment_handler = CommentHandler(2, __THREADS[1], 2, reddit, settings, logger)
    logger.info("SubmissionHandler instantiated on thread [{}]...".format(__THREADS[1]))

def __run():
    '''
    Calls the submission and comment handlers on their own threads with Reddit and configured settings
    '''

    logger.info('Starting up threads...')
    submission_handler.start()
    comment_handler.start()
    logger.info('Running!')


def __main():
    '''
    Main function -- calls __run to begin bot functions, handles any uncaught exceptions.
    '''

    if __name__ == '__main__':
        try:
            __run()
        except Exception as exception:
            logger.error("Encountered unexpected exception: {}".format(exception))


# Note that these initialization methods are outside the main loop
# This is intended to stop re-initialization of constants
__setup()

# Start excecution!
__main() 