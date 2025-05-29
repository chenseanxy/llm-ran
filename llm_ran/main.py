'''
Runs streamlit frontend
'''

from llm_ran.logging import setup_logging
setup_logging()

# from llm_ran.k8s.direct_impl import get_nodes
# print(get_nodes())

from llm_ran.llm import get_model, models
# from llm_ran.k8s.codegen import kubernetes_codegen_chain as chain
from llm_ran.k8s.direct import kubernetes_direct_chain as chain
from llm_ran.frontend import stream_lit

model = get_model(models.QWEN_25_14B)
stream_lit.main(chain(model))
# poetry run python -m streamlit run llm_ran/main.py
