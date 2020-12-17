import threading

from error_handler import ErrorHandler


class CommentHandler(threading.Thread):
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
        self.__stream_comments()


    def __stream_comments(self):
        try:
            stream = self.reddit.subreddit(self.settings['subreddit']).stream.comments(skip_existing=True)

            for comment in stream:
                self.logger.info("Parsing comment {}".format(comment.id))
                if self.__parent_is_approvable(comment):
                    self.__approve_parent_submission(comment)

        except Exception as exception:
            ErrorHandler(self, self.logger).handle(exception)
            self.__stream_comments()


    def __parent_is_approvable(self, comment):
        submission = comment.submission

        if not comment.parent_id == 't3_' + submission.id:
            return False
        
        if not comment.author == submission.author:
            return False

        minimum_reply_length = int(self.settings['minimumApprovalLength']) or -1
        if len(comment.body) < minimum_reply_length:
            return False

        return True


    def __approve_parent_submission(self, comment):
        submission = comment.submission
        
        self.logger.info("Approving submission {} [{}] by /u/{}...".format(submission.id, submission.url, submission.author))
        submission.mod.approve()
        for reply in submission.comments:
            if reply.author == self.reddit.user.me():
                self.logger.info("Removing bot reply {}...".format(reply.id))
                reply.delete()