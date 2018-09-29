# coding=utf-8
import asyncio
from random import randint
from time import time
from typing import List, Optional, AsyncGenerator, Dict, Awaitable

from mypy_extensions import TypedDict

TriviaQuestion = TypedDict('TriviaQuestion', {'question': str, 'answer': str})


class TriviaGame:
    def __init__(self, questions: List[TriviaQuestion], wait_time: int) -> None:
        self._questions = questions.copy()
        self._wait_time = wait_time
        self.stopped = False
        self.__active_question: Optional[TriviaQuestion] = None
        self.__answered = False
        self.tried_to_answer = []  # type: List[str]
        self.leaderboard: Dict[str, int] = {}
        self.before_question = []  # type: List[Awaitable]

    async def play(self) -> AsyncGenerator[str, None]:
        while not self.stopped and self._questions:
            wait_new_question = 1
            await asyncio.sleep(wait_new_question)
            self.__answered = False
            self.tried_to_answer = []
            self.__active_question = self._questions.pop(randint(0, len(self._questions) - 1))
            yield self.__active_question['question']
            time_asked = time()
            while not self.__answered and not self.stopped:
                if time_asked + self._wait_time > time():
                    await asyncio.sleep(1)
                else:
                    self.__answered = True
                    yield f"Correct answer was: **{self.__active_question['answer']}**"
                    self._questions.append(self.__active_question)

    def answer_question(self, answer: str, player: str) -> bool:
        if player not in self.tried_to_answer:
            self.tried_to_answer.append(player)
            if answer.lower() == str(self.__active_question['answer']).lower() and not self.__answered:
                self.__answered = True
                if player in self.leaderboard:
                    self.leaderboard[player] += 1
                else:
                    self.leaderboard[player] = 1
                return True
        return False

    def stop(self) -> None:
        self.stopped = True

    def score(self, limit: int=5) -> str:
        top_players = sorted(self.leaderboard.items(), key=lambda x: (x[1], x[0]), reverse=True)
        return'\n '.join([f'{p[0]}: {p[1]}' for p in top_players[:limit]])
