from .base import TestCase, Question
import llm_ran.k8s.direct_impl as impl
from .helpers import parse_cpu_mi, parse_mem_mi

TARGET_SERVICE = "productcatalogservice"
TARGET_NAMESPACE = "default"
# Problematic: this changes when cases are applied and pods are rebuilt
TARGET_POD = impl.get_deployment_pods(TARGET_SERVICE, TARGET_NAMESPACE)[0]
BROKEN_POD = (
    [
        pod
        for pod in impl.get_deployment_pods(TARGET_SERVICE, TARGET_NAMESPACE)
        if impl.get_pod_status(pod, TARGET_NAMESPACE).phase != "Running"
    ] or [ None ]
)[0]

print(TARGET_POD, BROKEN_POD)

TEST_CASES = [
    TestCase(
        scenario = None,
        questions=[
            # Quantifying answers - One API crawl
            Question(
                id="how-many-pods-for-deployment",
                question=f"How many pods are in for deployment `{TARGET_SERVICE}`?",
                answer=lambda: len(impl.get_deployment_pods(TARGET_SERVICE, TARGET_NAMESPACE)),
                derive_wrong_answers=lambda x: [x + 1, x + 3],
                level=0,
                base_type=0,
            ),
            Question(
                id="how-many-pods-in-namespace",
                question=f"How many pods are in the `{TARGET_NAMESPACE}` namespace?",
                answer=lambda: len(impl.get_pod_names_in_namespace(TARGET_NAMESPACE)),
                derive_wrong_answers=lambda x: [x - 3, x + 1, x + 5],
                level=0,
                base_type=0,
            ),
            Question(
                id="how-many-services-in-namespace",
                question=f"How many services are in the `{TARGET_NAMESPACE}` namespace?",
                answer=lambda: len(impl.get_services_in_namespace(TARGET_NAMESPACE)),
                derive_wrong_answers=lambda x: [x - 1, x + 1, x + 2],
                level=0,
                base_type=0,
            ),
            Question(
                id="how-many-nodes",
                question=f"How many nodes are in the cluster?",
                answer=lambda: len(impl.get_nodes()),
                derive_wrong_answers=lambda x: [x - 2, x - 1, x + 3],
                level=0,
                base_type=0,
            ),
            Question(
                id="how-much-cpu-for-deployment-per-pod",
                question=(
                    f"What is the per-pod CPU request for the deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: impl.get_deployment_per_pod_resource_requests(
                    TARGET_SERVICE, TARGET_NAMESPACE
                )["cpu"],
                derive_wrong_answers=lambda x: ["10m", "50m", "100m", "200m", "500m"],
                level=0,
                base_type=0,
                output_unit="cpu_m",
            ),
            Question(
                id="how-much-memory-for-deployment-per-pod",
                question=(
                    f"What is the per-pod memory request for the deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: impl.get_deployment_per_pod_resource_requests(
                    TARGET_SERVICE, TARGET_NAMESPACE
                )["memory"],
                derive_wrong_answers=lambda x: ["128Mi", "256Mi", "512Mi", "1Gi", "2Gi"],
                level=0,
                base_type=0,
                output_unit="mem_mi",
            ),
            # Quantifying answers - Multiple API crawls
            Question(
                id="how-many-pods-for-service",
                question=f"How many pods are declared for service `{TARGET_SERVICE}`?",
                answer=lambda: len(
                    impl.get_deployment_pods(impl.get_service_deployment(
                        TARGET_SERVICE, TARGET_NAMESPACE
                    ), TARGET_NAMESPACE)
                ),
                derive_wrong_answers=lambda x: [x + 1, x + 3],
                level=1,
                base_type=0,
            ),
            Question(
                id="how-many-pods-on-same-node",
                question=(
                    f"How many pods from namespace `{TARGET_NAMESPACE}` "
                    f"are running on the same node as `{TARGET_POD}`? "
                    f"Including `{TARGET_POD}` itself."
                ),
                answer=lambda: len(impl.get_pods_on_node_in_namespace(
                    impl.get_pod_node(TARGET_POD, TARGET_NAMESPACE), TARGET_NAMESPACE
                )),
                derive_wrong_answers=lambda x: [x - 1, x + 1],
                level=1,
                base_type=0,
            ),
            Question(
                id="how-many-pods-on-same-node-excluding",
                question=(
                    f"How many pods from namespace `{TARGET_NAMESPACE}` "
                    f"are running on the same node as `{TARGET_POD}`? "
                    f"Excluding `{TARGET_POD}` itself."
                ),
                answer=lambda: len(impl.get_pods_on_node_in_namespace(
                    impl.get_pod_node(TARGET_POD, TARGET_NAMESPACE), TARGET_NAMESPACE
                )) - 1,
                derive_wrong_answers=lambda x: [x - 1, x + 1],
                level=1,
                base_type=0,
            ),
            Question(
                id="how-many-nodes-does-a-deployment-use",
                question=(
                    f"How many nodes are used by the deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: len(set(
                    impl.get_pod_node(pod, TARGET_NAMESPACE)
                    for pod in impl.get_deployment_pods(TARGET_SERVICE, TARGET_NAMESPACE)
                )),
                derive_wrong_answers=lambda x: [x - 1, x + 1],
                level=1,
                base_type=0,
            ),
            Question(
                id="how-much-cpu-for-deployment-total",
                question=(
                    f"What is the total CPU request for all pods in the deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: str(
                    parse_cpu_mi(impl.get_deployment_per_pod_resource_requests(
                        TARGET_SERVICE, TARGET_NAMESPACE
                    )["cpu"]) * len(impl.get_deployment_pods(TARGET_SERVICE, TARGET_NAMESPACE))
                ) + "m",
                derive_wrong_answers=lambda x: ["100m", "200m", "500m", "1000m", "2000m"],
                level=1,
                base_type=0,
                output_unit="cpu_m",
            ),
            Question(
                id="how-much-memory-for-deployment-total",
                question=(
                    f"What is the total memory request all pods in the deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: str(
                    parse_mem_mi(impl.get_deployment_per_pod_resource_requests(
                        TARGET_SERVICE, TARGET_NAMESPACE
                    )["memory"]) * len(impl.get_deployment_pods(TARGET_SERVICE, TARGET_NAMESPACE))
                ) + "Mi",
                derive_wrong_answers=lambda x: ["128Mi", "256Mi", "512Mi", "1024Mi", "2048Mi"],
                level=1,
                base_type=0,
                output_unit="mem_mi",
            ),
        ],
    ),
    TestCase(
        scenario="resource-constraint",
        questions=[
            Question(
                id="how-many-pods-for-deployment-pending",
                question=(
                    f"How many pods are pending for deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: sum(
                    impl.get_pod_status(pod, TARGET_NAMESPACE).phase == "Pending"
                    for pod in
                    impl.get_deployment_pods(
                        TARGET_SERVICE, TARGET_NAMESPACE, 
                    )
                ),
                derive_wrong_answers=lambda x: [0, 1, 2, 3],
                level=1,
                base_type=0,
            ),
            Question(
                id="how-much-memory-for-pod-requested",
                question=(
                    f"What is the total memory requested by pod `{BROKEN_POD}`?"
                ),
                answer=lambda: str(
                    parse_mem_mi(impl.get_pod_resource_requests(BROKEN_POD, TARGET_NAMESPACE)["memory"])
                ) + "Mi",
                derive_wrong_answers=lambda x: ["1024Mi", "4096Mi", "16384Mi", "32768Mi"],
                level=0,
                base_type=0,
                output_unit="mem_mi",
            ),
            Question(
                id="which-pod-is-pending",
                question=(
                    f"Which pod is pending for deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: BROKEN_POD,
                derive_wrong_answers=lambda x: impl.get_deployment_pods(
                    TARGET_SERVICE, TARGET_NAMESPACE
                ),
                level=0,
                base_type=1,
            ),
            Question(
                id="how-much-memory-for-pending-pod",
                question=(
                    f"What is the total memory requested by pending pods in deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: str(
                    parse_mem_mi(impl.get_pod_resource_requests(BROKEN_POD, TARGET_NAMESPACE)["memory"])
                ) + "Mi",
                derive_wrong_answers=lambda x: ["1024Mi", "4096Mi", "16384Mi", "32768Mi"],
                level=1,
                base_type=0,
                output_unit="mem_mi",
            ),
            Question(
                id="why-is-pod-pending",
                question=(
                    f"Why is pod `{BROKEN_POD}` pending?"
                ),
                answer=lambda: "Insufficient memory",
                derive_wrong_answers=lambda x: [
                    "Insufficient CPU",
                    "Insufficient storage",
                    "Insufficient GPU",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-failing",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Insufficient memory",
                derive_wrong_answers=lambda x: [
                    "Insufficient CPU",
                    "Insufficient storage",
                    "Insufficient GPU",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-not-rolling-out",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` not rolling out?"
                ),
                answer=lambda: "Insufficient memory",
                derive_wrong_answers=lambda x: [
                    "Insufficient CPU",
                    "Insufficient storage",
                    "Insufficient GPU",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-pod-pending",
                question=(
                    f"How to fix pod `{BROKEN_POD}` being pending?"
                ),
                answer=lambda: "Reduce memory requests",
                derive_wrong_answers=lambda x: [
                    "Reduce CPU requests",
                    "Reduce storage requests",
                    "Reduce GPU requests",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-deployment-failing",
                question=(
                    f"How to fix deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Reduce memory requests",
                derive_wrong_answers=lambda x: [
                    "Reduce CPU requests",
                    "Reduce storage requests",
                    "Reduce GPU requests",
                ],
                level=2,
                base_type=1,
            ),
        ],
    ),
    TestCase(
        scenario="image-not-found",
        questions=[
            Question(
                id="how-many-pods-for-deployment-unhealthy",
                question=(
                    f"How many pods in deployment `{TARGET_SERVICE}` are unhealthy?"
                ),
                answer=lambda: sum(
                    impl.get_pod_status(pod, TARGET_NAMESPACE).phase != "Running"
                    for pod in
                    impl.get_deployment_pods(
                        TARGET_SERVICE, TARGET_NAMESPACE, 
                    )
                ),
                derive_wrong_answers=lambda x: [0, 1, 2, 3],
                level=1,
                base_type=0,
            ),
            Question(
                id="which-container-is-unhealthy",
                question=(
                    f"Which container in pod `{BROKEN_POD}` is unhealthy?"
                ),
                answer=lambda: impl.get_pod_details(BROKEN_POD, TARGET_NAMESPACE)["containers"][0]["name"],
                derive_wrong_answers=lambda x: [
                    "nginx",
                    "redis",
                    "mysql",
                ], 
                level=0,
                base_type=1,
            ),
            Question(
                id="which-pod-is-unhealthy",
                question=(
                    f"Which pod in deployment `{TARGET_SERVICE}` is unhealthy?"
                ),
                answer=lambda: BROKEN_POD,
                derive_wrong_answers=lambda x: impl.get_deployment_pods(
                    TARGET_SERVICE, TARGET_NAMESPACE
                ),
                level=0,
                base_type=1,
            ),
            Question(
                id="why-is-pod-unhealthy",
                question=(
                    f"Why is pod `{BROKEN_POD}` unhealthy?"
                ),
                answer=lambda: "Image not found",
                derive_wrong_answers=lambda x: [
                    "Not passing health checks",
                    "Node tolerations not met",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-failing",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Image not found",
                derive_wrong_answers=lambda x: [
                    "Not passing health checks",
                    "Node tolerations not met",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-not-rolling-out",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` not rolling out?"
                ),
                answer=lambda: "Image not found",
                derive_wrong_answers=lambda x: [
                    "Not passing health checks",
                    "Node tolerations not met",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-pod-unhealthy",
                question=(
                    f"How to fix pod `{BROKEN_POD}` being unhealthy?"
                ),
                answer=lambda: "Check image name",
                derive_wrong_answers=lambda x: [
                    "Check health checks",
                    "Check node tolerations",
                    "Increase CPU limit",
                    "Increase memory limit",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-deployment-failing",
                question=(
                    f"How to fix deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Check image name",
                derive_wrong_answers=lambda x: [
                    "Check health checks",
                    "Check node tolerations",
                    "Increase CPU limit",
                    "Increase memory limit",
                ],
                level=2,
                base_type=1,
            ),
        ],
    ),
    TestCase(
        scenario="liveness-probe",
        questions=[
            Question(
                id="how-many-pods-for-deployment-unhealthy",
                question=(
                    f"How many pods in deployment `{TARGET_SERVICE}` are unhealthy?"
                ),
                answer=lambda: sum(
                    impl.get_pod_status(pod, TARGET_NAMESPACE).phase != "Running"
                    for pod in
                    impl.get_deployment_pods(
                        TARGET_SERVICE, TARGET_NAMESPACE, 
                    )
                ),
                derive_wrong_answers=lambda x: [0, 1, 2, 3],
                level=1,
                base_type=0,
            ),
            Question(
                id="which-container-is-unhealthy",
                question=(
                    f"Which container in pod `{BROKEN_POD}` is unhealthy?"
                ),
                answer=lambda: impl.get_pod_details(BROKEN_POD, TARGET_NAMESPACE)["containers"][0]["name"],
                derive_wrong_answers=lambda x: [
                    "nginx",
                    "redis",
                    "mysql",
                ], 
                level=0,
                base_type=1,
            ),
            Question(
                id="which-pod-is-unhealthy",
                question=(
                    f"Which pod in deployment `{TARGET_SERVICE}` is unhealthy?"
                ),
                answer=lambda: BROKEN_POD,
                derive_wrong_answers=lambda x: impl.get_deployment_pods(
                    TARGET_SERVICE, TARGET_NAMESPACE
                ),
                level=0,
                base_type=1,
            ),
            Question(
                id="why-is-pod-unhealthy",
                question=(
                    f"Why is pod `{BROKEN_POD}` unhealthy?"
                ),
                answer=lambda: "Not passing health checks",
                derive_wrong_answers=lambda x: [
                    "Image not found",
                    "Node tolerations not met",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-failing",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Not passing health checks",
                derive_wrong_answers=lambda x: [
                    "Image not found",
                    "Node tolerations not met",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-not-rolling-out",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` not rolling out?"
                ),
                answer=lambda: "Not passing health checks",
                derive_wrong_answers=lambda x: [
                    "Image not found",
                    "Node tolerations not met",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-pod-unhealthy",
                question=(
                    f"How to fix pod `{BROKEN_POD}` being unhealthy?"
                ),
                answer=lambda: "Check readiness probe and health checks",
                derive_wrong_answers=lambda x: [
                    "Check image name",
                    "Check node tolerations",
                    "Increase CPU limit",
                    "Increase memory limit",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-deployment-failing",
                question=(
                    f"How to fix deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Check readiness probe and health checks",
                derive_wrong_answers=lambda x: [
                    "Check image name",
                    "Check node tolerations",
                    "Increase CPU limit",
                    "Increase memory limit",
                ],
                level=2,
                base_type=1,
            ),
        ],
    ),
    TestCase(
        scenario="node-affinity",
        questions=[
            Question(
                id="how-many-pods-for-deployment-pending",
                question=(
                    f"How many pods are pending for deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: sum(
                    impl.get_pod_status(pod, TARGET_NAMESPACE).phase == "Pending"
                    for pod in
                    impl.get_deployment_pods(
                        TARGET_SERVICE, TARGET_NAMESPACE, 
                    )
                ),
                derive_wrong_answers=lambda x: [0, 1, 2, 3],
                level=1,
                base_type=0,
            ),
            Question(
                id="which-pod-is-pending",
                question=(
                    f"Which pod is pending for deployment `{TARGET_SERVICE}`?"
                ),
                answer=lambda: BROKEN_POD,
                derive_wrong_answers=lambda x: impl.get_deployment_pods(
                    TARGET_SERVICE, TARGET_NAMESPACE
                ),
                level=0,
                base_type=1,
            ),
            Question(
                id="why-is-pod-pending",
                question=(
                    f"Why is pod `{BROKEN_POD}` pending?"
                ),
                answer=lambda: "Node tolerations not met",
                derive_wrong_answers=lambda x: [
                    "Image not found",
                    "Not passing health checks",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-failing",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Node tolerations not met",
                derive_wrong_answers=lambda x: [
                    "Image not found",
                    "Not passing health checks",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="why-is-deployment-not-rolling-out",
                question=(
                    f"Why is deployment `{TARGET_SERVICE}` not rolling out?"
                ),
                answer=lambda: "Node tolerations not met",
                derive_wrong_answers=lambda x: [
                    "Image not found",
                    "Not passing health checks",
                    "Insufficient CPU",
                    "Insufficient memory",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-pod-pending",
                question=(
                    f"How to fix pod `{BROKEN_POD}` being pending?"
                ),
                answer=lambda: "Add nodes that meet tolerations",
                derive_wrong_answers=lambda x: [
                    "Reduce CPU requests",
                    "Reduce memory requests",
                    "Reduce GPU requests",
                ],
                level=2,
                base_type=1,
            ),
            Question(
                id="how-to-fix-deployment-failing",
                question=(
                    f"How to fix deployment `{TARGET_SERVICE}` failing?"
                ),
                answer=lambda: "Add nodes that meet tolerations",
                derive_wrong_answers=lambda x: [
                    "Reduce CPU requests",
                    "Reduce memory requests",
                    "Reduce GPU requests",
                ],
                level=2,
                base_type=1,
            ),
        ],
    ),
]