class FetchedEmail:
    def __init__(self, uid, message, envelop, date):
        self.uid = uid
        self.message = message
        self.envelop = envelop
        self.date = date
        self.metadata = None
