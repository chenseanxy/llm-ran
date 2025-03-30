import logging
import pathlib
from datetime import datetime

from langgraph.graph.graph import CompiledGraph

from llm_ran.yaml import yaml
from llm_ran.graph import run_graph
from llm_ran.k8s_env.scenario import Scenario
from .base import TestCase, Question

_logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_PATH = pathlib.Path(__file__).parent.parent.parent / "data" / "snapshots"


def run_test_cases(
        graph: CompiledGraph,
        test_cases: list[TestCase],
        *,
        trials: int = 1,
        context: dict[str, str] = None,
        snapshot_path: str | pathlib.Path = DEFAULT_OUTPUT_PATH,
        result_logger: logging.Logger = None,
    ):
    results = []
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    for test_case in test_cases:
        _logger.info("Loading scenario: %s", test_case.scenario)
        with Scenario(test_case.scenario):
            for q in test_case.questions:
                this_path = pathlib.Path(snapshot_path) / (test_case.scenario or 'base') / q.id
                if not pathlib.Path(this_path).exists():
                    pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)

                for evaluate_as in q.can_evaluate_as():
                    for trial in range(trials):
                        _logger.info(
                            "Running test case: %s, question: %s, evaluate_as: %s",
                            test_case.scenario,
                            q.question,
                            evaluate_as,
                        )
                        question = q.question_text(evaluate_as)
                        _logger.info("Question: %s", question)
                        result = run_graph(graph, question)
                        _logger.info("Result: %s", result["messages"][-1].content)
                        identifier = f"{now}_{q.get_type(evaluate_as)}_{trial}"
                        with open(f"{this_path}/{identifier}.yaml", "w") as f:
                            yaml.dump({"question": q.dump(), "result": result}, f)

                        expected = q.get_answer()
                        if evaluate_as == 2:
                            expected = q.multiple_choice_correct_answer

                        this_result = {
                            "scenario": test_case.scenario,
                            "question": q.question,
                            "evaluate_as": evaluate_as,
                            "result": result["messages"][-1].content,
                            "expected": expected,
                            **context,
                        }
                        (result_logger or _logger).info(this_result)

                        results.append(this_result)
    return results

def _main():
    from llm_ran.logging import setup_logging
    from llm_ran.k8s.direct import kubernetes_direct_chain
    from llm_ran.llm import get_model, models
    from .questions import TEST_CASES
    setup_logging()
    run_test_cases(
        graph=kubernetes_direct_chain(get_model(models.QWEN_25_14B)),
        test_cases=TEST_CASES,
        context={"test": "test"},
        trials=2,
    )

if __name__ == "__main__":
    # poetry run python -m llm_ran.benchmark.run
    _main()
