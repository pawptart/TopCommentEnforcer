import threading

from error_handler import ErrorHandler


class SubmissionHandler(threading.Thread):
    def __init__(self, thread_id, name, counter, reddit, settings, logger):
        threading.Thread.__init__(self)

        # Thread subclass attributes
        self.thread_id = thread_id
        self.name      = name
        self.counter   = counter

        # Reddit and settings attributes
        self.reddit   = reddit
        self.settings = settings

        # Logger
        self.logger = logger


    def run(self):
        self.__stream_submissions()


    def __stream_submissions(self):
        try:
            stream = self.reddit.subreddit(self.settings['subreddit']).stream.submissions(skip_existing=True)

            for submission in stream:
                self.logger.info("Parsing submission {}".format(submission.id))
                if self.__should_remove_submission(submission):
                    self.logger.info("Removing submission {} [{}] by /u/{}...".format(submission.id, submission.url, submission.author))
                    self.__handle_removal(submission)

        except Exception as exception:
            ErrorHandler(self, self.logger).handle(exception)
            self.__stream_submissions()


    def __should_remove_submission(self, submission):
        is_link  = not submission.is_self
        is_video = 'youtube' in submission.url

        return is_link and is_video

    
    def __handle_removal(self, submission):
        comment = submission.reply(self.settings['removalMessage'])
        comment.mod.distinguish(how='yes', sticky=True)
        submission.mod.remove()