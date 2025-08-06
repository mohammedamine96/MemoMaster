# app/models.py

class Flashcard:
    def __init__(self, id, question, answer, last_reviewed, next_review, interval):
        self.id = id
        self.question = question
        self.answer = answer
        self.last_reviewed = last_reviewed
        self.next_review = next_review
        self.interval = interval
