from pydantic import BaseModel
from typing import Callable
import random
import string

class CannotEvaluateAsError(ValueError):
    def __init__(self, question: str, base_type: int, evaluate_as: int):
        super().__init__(f"Cannot evaluate question '{question}' type {base_type} as type {evaluate_as}")


class Question(BaseModel):
    id: str
    question: str
    answer: Callable[[], str | int | float]
    wrong_answers: list[str] = []
    derive_wrong_answers: Callable[[str | int | float], list[str]] | None = None

    multiple_choice_correct_answer: str | None = None           # A/B/C/D
    multiple_choice_generated_answers: list[tuple[str, str]] | None = None  

    # Levels: 0, 1, 2
    # 0: One API crawl
    # 1: A collection of API craws
    # 2: Reasoning on top of API crawls
    level: int

    # Types of the question
    # 0: Numerical
    # 1: Multiple Choice
    # 2: Open Ended
    base_type: int

    _cached_answer: str | int | float | None = None

    def get_answer(self) -> str | int | float:
        if self._cached_answer is None:
            self._cached_answer = self.answer()
        return self._cached_answer
    
    def reset(self):
        self._cached_answer = None
    
    @staticmethod
    def get_type(type_: int) -> str:
        if type_ == 0:
            return "numerical"
        elif type_ == 1:
            return "mulchoice"
        elif type_ == 2:
            return "open"

    def can_evaluate_as(self) -> list[int]:
        if self.base_type == 0:
            return [0, 1, 2]
        elif self.base_type == 1:
            return [1, 2]
        elif self.base_type == 2:
            return [2]

    def question_text(self, evaluate_as: int) -> str:
        # Evaluate as type 0, 1, 2
        q = self.question
        t = self.base_type
        if evaluate_as not in self.can_evaluate_as():
            raise CannotEvaluateAsError(q, t, evaluate_as)
        if evaluate_as == 0:
            return f"{q}\nAnswer with a single number"
        if evaluate_as == 1:
            right_answer = self.get_answer()
            if self.derive_wrong_answers is not None:
                self.wrong_answers = self.derive_wrong_answers(right_answer)
            wrong_answers = self.wrong_answers
            
            all_answers = list(set(str(i) for i in [right_answer] + wrong_answers))
            assert len(all_answers) >= 2, "Not enough answers to generate multiple choice question"
            assert len(all_answers) <= 26, "Too many answers to generate multiple choice question"
            random.shuffle(all_answers)
            answers = [(string.ascii_uppercase[i], ans) for i, ans in enumerate(all_answers)]
            correct = next(filter(lambda x: x[1] == str(right_answer), answers))[0]
            # Make these available for evaluation
            self.multiple_choice_correct_answer = correct
            self.multiple_choice_generated_answers = answers

            answers_template = "\n".join(f"{k}: {v}" for k, v in answers)
            return f"Choose the correct answer for this question: {q}\n{answers_template}\nAnswer with a single letter"
        if evaluate_as == 2:
            return f"{q}\nAnswer with a few words or a single sentence."

    def dump(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.get_answer(),
            "wrong_answers": self.wrong_answers,
            "multiple_choice_correct_answer": self.multiple_choice_correct_answer,
            "multiple_choice_generated_answers": self.multiple_choice_generated_answers,
            "level": self.level,
            "base_type": self.base_type,
        }


class TestCase(BaseModel):
    scenario: str | None
    questions: list[Question]

