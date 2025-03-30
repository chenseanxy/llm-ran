from typing import Callable

from .direct_impl import (
    get_services_in_namespace,
    get_pod_names_in_namespace,
    get_nodes,
    get_pods_on_node_in_namespace,
    get_pod_node,
)


QUERIES_ANSWERS: list[tuple[str, Callable]] = [
    (
        "What are the names and ports of the services in the 'monitoring' namespace? "
        "Return name as keys and ports in a list as values, example {'service1': [80, 443], 'service2': [8080]}",
        lambda: get_services_in_namespace("monitoring")
    ),
    (
        "List all the pod names in the 'monitoring' namespace. Return as a list of pod names. "
        "Example ['pod1', 'pod2']",
        lambda: get_pod_names_in_namespace("monitoring")
    ),
    (
        "List all the nodes. Return as a list of node names. Example ['node1', 'node2']",
        lambda: get_nodes()
    ),
    (
        "Show all the pods in the 'monitoring' namespace that are running on node 'k3d-oran-agent-1'."
        "Return as a list of pod names. Example ['pod1', 'pod2']",
        lambda: get_pods_on_node_in_namespace("k3d-oran-agent-1", "monitoring")
    ),
    (
        "Given a pod name 'prometheus-monitoring-kube-prometheus-prometheus-0' "
        "in the 'monitoring' namespace, get the pod's node name."
        "Example 'node1'",
        lambda: get_pod_node("prometheus-monitoring-kube-prometheus-prometheus-0", "monitoring")
    ),
    # Cutoff: anything below this ended up being too complicated for one code gen, results are less consistent
    (
        "In namespace 'monitoring', list all the pods that are running on same kubernetes node "
        "as pod 'prometheus-monitoring-kube-prometheus-prometheus-0' (including this one). Return as a list. "
        "Example ['pod1', 'pod2']",
        lambda: get_pods_on_node_in_namespace(
            get_pod_node("prometheus-monitoring-kube-prometheus-prometheus-0", "monitoring"),
            "monitoring"
        )
    ),
    (
        "In namespace 'monitoring', find out the node where pod 'prometheus-monitoring-kube-prometheus-prometheus-0' "
        "is deployed on, then use that find all the pods that are running on the same node. Return the names of the pods. "
        "Example ['pod1', 'pod2']",
        lambda: get_pods_on_node_in_namespace(
            get_pod_node("prometheus-monitoring-kube-prometheus-prometheus-0", "monitoring"),
            "monitoring"
        )
    ),
]
