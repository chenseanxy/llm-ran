from .base import TestCase, Question
import llm_ran.k8s.direct_impl as impl

TARGET_SERVICE = "productcatalogservice"
TARGET_NAMESPACE = "default"

TEST_CASES = [
    TestCase(
        scenario = None,
        questions=[
            # Question(
            #     id="1-how-many-pods-for-deployment",
            #     question=f"How many pods are in for deployment `{TARGET_SERVICE}`?",
            #     answer=lambda: len(impl.get_deployment_pods(TARGET_SERVICE, TARGET_NAMESPACE)),
            #     derive_wrong_answers=lambda x: [x + 1, x + 3],
            #     level=0,
            #     base_type=0,
            # ),
            # Question(
            #     id="2-how-many-pods-in-namespace",
            #     question=f"How many pods are in the `{TARGET_NAMESPACE}` namespace?",
            #     answer=lambda: len(impl.get_pod_names_in_namespace(TARGET_NAMESPACE)),
            #     derive_wrong_answers=lambda x: [x - 3, x + 1, x + 5],
            #     level=0,
            #     base_type=0,
            # ),
            # Question(
            #     id="3-how-many-services-in-namespace",
            #     question=f"How many services are in the `{TARGET_NAMESPACE}` namespace?",
            #     answer=lambda: len(impl.get_services_in_namespace(TARGET_NAMESPACE)),
            #     derive_wrong_answers=lambda x: [x - 1, x + 1, x + 2],
            #     level=0,
            #     base_type=0,
            # ),
            Question(
                id="4-how-many-nodes",
                question=f"How many nodes are in the cluster?",
                answer=lambda: len(impl.get_nodes()),
                derive_wrong_answers=lambda x: [x - 2, x - 1, x + 3],
                level=0,
                base_type=0,
            ),
        ],
    ),
    # TestCase(
    #     scenario="resource-constraint",
    #     questions=[
    #     ],
    # ),
]