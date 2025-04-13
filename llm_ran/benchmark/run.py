import logging
import pathlib
from datetime import datetime
from time import time

from langchain_core.messages import AIMessage
from langgraph.graph.graph import CompiledGraph

from llm_ran.yaml import yaml
from llm_ran.graph import run_graph
from llm_ran.k8s_env.scenario import Scenario
from .base import TestCase, Question

_logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_PATH = pathlib.Path(__file__).parent.parent.parent / "data"
DEFAULT_SNAPSHOT_PATH = DEFAULT_OUTPUT_PATH / "snapshots"


def _sum_message_costs(messages: list[dict]) -> dict[str, int]:
    """Calculate the cost of messages."""
    total_cost = {
        "eval_count": 0,
        "prompt_eval_count": 0,
        "eval_duration": 0,
        "prompt_eval_duration": 0,
        "load_duration": 0,
        "total_duration": 0,
    }
    max_cost = {
        "eval_count": 0,
        "prompt_eval_count": 0,
        "eval_duration": 0,
        "prompt_eval_duration": 0,
        "load_duration": 0,
        "total_duration": 0,
    }
    for message in messages:
        if isinstance(message, AIMessage):
            meta = message.response_metadata
        elif isinstance(message, dict):
            meta = message.get("response_metadata")
        else:
            continue
        if not meta:
            continue
        for field in total_cost.keys():
            if field in meta:
                total_cost[field] += meta.get(field, 0)
                max_cost[field] = max(max_cost[field], meta.get(field, 0))
    total_cost["total_tokens"] = total_cost["eval_count"] + total_cost["prompt_eval_count"]
    for field in max_cost.keys():
        total_cost[f"max_{field}"] = max_cost[field]
    return total_cost


def run_one_trial(
    graph: CompiledGraph,
    q: Question,
    test_case: TestCase,
    this_path: str | pathlib.Path,
    run_id: str,
    trial_id: int,
    evaluate_as: int,
    *,
    context: dict[str, str] = None,
    result_logger: logging.Logger = None,
    identifier_prefix: str = "",
):
    _logger.info(
        "Running test case: %s, question: %s, evaluate_as: %s",
        test_case.scenario or 'base',
        q.question,
        evaluate_as,
    )
    question = q.question_text(evaluate_as)
    _logger.info("Question: %s", question)

    _time_before = time()
    result, error = run_graph(graph, question, propagate_errors=False)
    execution_time = time() - _time_before

    if not result or not result["messages"]:
        text_result = None
    elif result["messages"][-1].type != "ai":
        text_result = None
    else:
        text_result = result["messages"][-1].content

    _logger.info("Result: %s", text_result)
    identifier = f"{run_id}_{identifier_prefix}_{q.get_type(evaluate_as)}_{trial_id}"
    snapshot_path = f"{this_path}/{identifier}.yaml"
    with open(snapshot_path, "w") as f:
        yaml.dump({"question": q.dump(), "result": result, "error": error}, f)

    expected = q.get_answer()
    if evaluate_as == 1:
        expected = q.multiple_choice_correct_answer

    this_result = {
        "scenario": test_case.scenario or 'base',
        "question": q.id,
        "trial": trial_id,
        "run_id": run_id,
        "level": q.level,
        "evaluate_as": evaluate_as,
        "expected": expected,
        "num_messages": len(result["messages"]),
        "execution_time": execution_time,
        **_sum_message_costs(result["messages"]),
        **context,
        "result": text_result,
        "error": error.__class__.__name__ if error else None,
    }
    (result_logger or _logger).info(this_result)
    return this_result


def run_one_case(
    graph: CompiledGraph,
    q: Question,
    test_case: TestCase,
    this_path: str | pathlib.Path,
    run_id: str,
    *,
    trials: int = 1,
    context: dict[str, str] = None,
    result_logger: logging.Logger = None,
    identifier_prefix: str = "",
):
    results = []
    for evaluate_as in q.can_evaluate_as():
        for trial in range(trials):
            try:
                this_result = run_one_trial(
                    graph=graph,
                    q=q,
                    test_case=test_case,
                    this_path=this_path,
                    run_id=run_id,
                    trial_id=trial,
                    evaluate_as=evaluate_as,
                    context=context,
                    result_logger=result_logger,
                    identifier_prefix=identifier_prefix,
                )
                results.append(this_result)
            except Exception as e:
                _logger.error("Error running test case: %s", e)
                this_result = {
                    "scenario": test_case.scenario or 'base',
                    "question": q.id,
                    "trial": trial,
                    "run_id": run_id,
                    "level": q.level,
                    "evaluate_as": evaluate_as,
                    **context,
                    "error": e.__class__.__name__,
                }
                results.append(this_result)
    return results


def run_test_cases(
    graph: CompiledGraph,
    test_cases: list[TestCase],
    *,
    trials: int = 1,
    context: dict[str, str] | None = None,
    snapshot_path: str | pathlib.Path = DEFAULT_SNAPSHOT_PATH,
    result_logger: logging.Logger = None,
    progress_logger: logging.Logger = None,
    prefix: str = "",
    run_id: str | None = None,
    manage_scenarios: bool = True,
    select_scenarios: list[str] | None = None,
):
    results = []
    run_id = run_id or datetime.now().strftime("%m%d%H%M%S")
    start_time = time()
    for test_case in test_cases:
        scenario_text = test_case.scenario or 'base'
        if select_scenarios and scenario_text not in select_scenarios:
            _logger.info("Skipping scenario: %s", test_case.scenario)
            continue
        if manage_scenarios:
            _logger.info("Loading scenario: %s", test_case.scenario)
        with Scenario(test_case.scenario, load=manage_scenarios):
            for qi, q in enumerate(test_case.questions):
                if progress_logger:
                    try:
                        elapsed_time = time() - start_time
                        expected_time = elapsed_time / (qi) * len(test_case.questions) if qi > 0 else 0
                        remaining_time = expected_time - elapsed_time
                        progress_logger.info(
                            "Scenario %s ctx=%s Progress: %d/%d, elapsed: %.2fs, total: %.2fs, remaining: %.2fs",
                            scenario_text,
                            context,
                            qi + 1,
                            len(test_case.questions),
                            elapsed_time,
                            expected_time,
                            remaining_time,
                        )
                    except Exception:
                        pass

                this_path = pathlib.Path(snapshot_path) / scenario_text / q.id
                if not pathlib.Path(this_path).exists():
                    pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
                this_result = run_one_case(
                    graph=graph,
                    q=q,
                    test_case=test_case,
                    this_path=this_path,
                    run_id=run_id,
                    trials=trials,
                    context=context,
                    result_logger=result_logger,
                    identifier_prefix=prefix,
                )
                results.extend(this_result)
    return results


def _main():
    import pandas as pd
    from llm_ran.logging import setup_logging
    from llm_ran.k8s.direct import kubernetes_direct_chain
    # from llm_ran.k8s.codegen import kubernetes_codegen_chain
    from llm_ran.llm import get_model, models
    from .questions import TEST_CASES
    setup_logging()
    exp_logger = logging.getLogger("experiment")
    res = run_test_cases(
        graph=kubernetes_direct_chain(get_model(models.SKY_T1_32B)),
        test_cases=TEST_CASES,
        context={"test": "test"},
        trials=2,
        result_logger=exp_logger,
        prefix="direct",
    )
    df = pd.DataFrame(res)
    print(df)
    df.to_csv(DEFAULT_OUTPUT_PATH / "direct.csv", index=False)
    # res_codegen = run_test_cases(
    #     graph=kubernetes_codegen_chain(get_model(models.QWEN_25_7B)),
    #     test_cases=TEST_CASES,
    #     context={"test": "test"},
    #     trials=2,
    #     result_logger=exp_logger,
    #     prefix="codegen",
    # )
    # print(pd.DataFrame(res_codegen))


if __name__ == "__main__":
    # poetry run python -m llm_ran.benchmark.run
    _main()
