import pathlib
import yaml
import subprocess
import logging

MANIFESTS_PATH = pathlib.Path(__file__).parent / "manifests"
KUSTOMIZATION_PATH = MANIFESTS_PATH / "kustomization.yaml"
_logger = logging.getLogger(__name__)


class ScenarioError(RuntimeError):
    """Custom exception for scenario loading errors."""
    pass


class Scenario():
    def __init__(self, scenario: str | None):
        self.scenario = scenario
    
    def __enter__(self):
        """Enter the scenario context."""
        return self.load_scenario(self.scenario)
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the scenario context."""
        return self.load_scenario(None)

    def _generate_kustomize(self, scenario: str | None = None):
        """Generate a kustomization.yaml file for the given scenario."""
        kustomize = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": ["base"],
            "components": [f"scenarios/{scenario}"] if scenario else [],
        }
        with KUSTOMIZATION_PATH.open("w") as f:
            yaml.dump(kustomize, f)

    def load_scenario(self, scenario: str | None = None):
        """Load the scenario from the kustomization.yaml file."""
        self._generate_kustomize(scenario)
        result = subprocess.run(
            ["kubectl", "apply", "-k", str(MANIFESTS_PATH)],
            capture_output=True,
        )
        _logger.info(
            f"Scenario {scenario} applied: [err={result.returncode}] \n"
            f"{result.stdout.decode()} \n{result.stderr.decode()}"
        )

        if result.returncode != 0:
            raise ScenarioError(f"Failed to apply scenario {scenario}: {result.stderr.decode()}")


def _main():
    """Main function for testing the scenario loading."""
    logging.basicConfig(level=logging.INFO)
    with Scenario("resource-constraint") as s:
        pass


if __name__ == "__main__":
    _main()
    # poetry run python -m llm_ran.k8s_env.scenario
