from llm_ran.logging import setup_logging
setup_logging()

# from llm_ran.k8s.direct_impl import get_nodes
# print(get_nodes())

from llm_ran.llm import get_model, models
from llm_ran.k8s.codegen import kubernetes_codegen_chain
from llm_ran.frontend.stream_lit import main

model = get_model(models.QWEN_25_14B)
chain = kubernetes_codegen_chain(model)
main(chain)
# poetry run python -m streamlit run llm_ran/main.py
