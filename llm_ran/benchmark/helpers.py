
def parse_cpu_mi(cpu_mi: str) -> int:
    """
    Parses a CPU value in millicores (m) or cores (no suffix) to an integer value in millicores.
    """
    if cpu_mi.endswith("m"):
        return int(cpu_mi[:-1])
    elif cpu_mi.endswith("c"):
        return int(cpu_mi[:-1]) * 1000
    else:
        raise ValueError(f"Unknown CPU format: {cpu_mi}")

def parse_mem_mi(mem_mi: str) -> int:
    """
    Parses a memory value in MiB (Mi) or GiB (Gi) to an integer value in MiB.
    """
    if mem_mi.endswith("Mi"):
        return int(mem_mi[:-2])
    elif mem_mi.endswith("Gi"):
        return int(mem_mi[:-2]) * 1024
    else:
        raise ValueError(f"Unknown memory format: {mem_mi}")
