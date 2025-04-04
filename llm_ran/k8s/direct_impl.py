from kubernetes import client


def get_pod_names_in_namespace(namespace: str) -> list[str]:
    """Get all the pod names in the given namespace"""
    pods = client.CoreV1Api().list_namespaced_pod(namespace)
    return [pod.metadata.name for pod in pods.items]


def get_services_in_namespace(namespace: str) -> dict[str, list[int]]:
    """Get the names and ports of the services in the given namespace"""
    services = client.CoreV1Api().list_namespaced_service(namespace)
    return {service.metadata.name: [port.port for port in service.spec.ports] for service in services.items}


def get_nodes() -> list[str]:
    """Get all the node names in the cluster"""
    nodes = client.CoreV1Api().list_node()
    return [node.metadata.name for node in nodes.items]


def get_pods_on_node_in_namespace(node_name: str, namespace: str) -> list[str]:
    """Get the names of the pods running on the given node in the given namespace"""
    pods = client.CoreV1Api().list_namespaced_pod(namespace)
    return [pod.metadata.name for pod in pods.items if pod.spec.node_name == node_name]


def get_pod_node(pod_name: str, namespace: str) -> str:
    """Get the node name for the given pod in the given namespace"""
    pod = client.CoreV1Api().read_namespaced_pod(pod_name, namespace)
    return pod.spec.node_name

def get_deployment_status(deployment_name: str, namespace: str) -> str:
    """Get the status of the given deployment in the given namespace"""
    deployment = client.AppsV1Api().read_namespaced_deployment(deployment_name, namespace)
    return deployment.status

def get_deployment_pods(deployment_name: str, namespace: str) -> list[str]:
    """Get the names of the pods for the given deployment in the given namespace"""
    deployment = client.AppsV1Api().read_namespaced_deployment(deployment_name, namespace)
    deployment_selector = deployment.spec.selector.match_labels
    label_selector = ",".join([f"{k}={v}" for k, v in deployment_selector.items()])
    pods = client.CoreV1Api().list_namespaced_pod(namespace, label_selector=label_selector)
    return [pod for pod in pods.items]

def get_pod_status(pod_name: str, namespace: str) -> str:
    """Get the status of the given pod in the given namespace"""
    pod = client.CoreV1Api().read_namespaced_pod(pod_name, namespace)
    return pod.status
