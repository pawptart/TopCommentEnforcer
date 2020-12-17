import threading

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
        stream = self.reddit.subreddit(self.settings['subreddit']).stream.comments()

        for comment in stream:
            print(comment.body)
