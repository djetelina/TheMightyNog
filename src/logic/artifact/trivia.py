# coding=utf-8
import asyncio
from random import randint
from time import time
from typing import List, Optional, AsyncGenerator

from mypy_extensions import TypedDict

TriviaQuestion = TypedDict('TriviaQuestion', {'question': str, 'answer': str})


class TriviaGame:
    def __init__(self, questions: List[TriviaQuestion], wait_time: int) -> None:
        self._questions = questions.copy()
        self._wait_time = wait_time
        self.stopped = False
        self.__active_question: Optional[TriviaQuestion] = None
        self.__answered = False

    async def play(self) -> AsyncGenerator[str, None]:
        while not self.stopped and self._questions:
            self.__answered = False
            self.__active_question = self._questions.pop(randint(0, len(self._questions) - 1))
            yield self.__active_question['question']
            time_asked = time()
            while not self.__answered and not self.stopped:
                if time_asked + self._wait_time > time():
                    await asyncio.sleep(1)
                else:
                    yield f"Correct answer was: {self.__active_question['answer']}"
                    self.__answered = True

    def answer_question(self, answer):
        if answer.lower() == self.__active_question['answer'].lower():
            self.__answered = True
            return True
        return False

    def stop(self):
        self.stopped = True
