import semantic_kernel as sk
import semantic_kernel.connectors.ai.open_ai as sk_oai
from semantic_kernel.prompt_template.input_variable import InputVariable
from models import AIModel
from set_log import setup_logger
import asyncio
import os
import sys
import json
from prompts.abst_sum import ABST_SUM
from prompts.abst_sum_final import ABST_SUM_FINAL
from dotenv import load_dotenv

load_dotenv()

MAX_API_TIMEOUT = 120

def initialize_kernel(
        api_key,
        api_key_type="openai",
        ai_model_id="gpt-3.5-turbo",
        org_id=None,
):
    kernel = sk.Kernel()
    if api_key_type == "openai":
        kernel.add_service(
            sk_oai.OpenAIChatCompletion(
                ai_model_id=ai_model_id,
                api_key=api_key,
                org_id=org_id,
            ),
        )
    return kernel

def create_ai_model(
    kernel,
    model_name,
    prompt,
    max_tokens=1500,
    temperature=0.5,
    top_p=0.5,
    frequency_penalty=0.0,
    presence_penalty=0.0,
):
    if not prompt:
        raise ValueError("Prompt cannot be empty")
    execution_settings = sk_oai.OpenAIChatPromptExecutionSettings(
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    prompt_template_config = sk.PromptTemplateConfig(
        template=prompt,
        name=model_name,
        template_format="semantic-kernel",
        input_variables=[
            InputVariable(
                name="language", description="The response language", is_required=True
            ),
            InputVariable(
                name="abstract", description="The abstract", is_required=False
            ),
            InputVariable(
                name="abstract_list", description="The list of abstracts", is_required=False
            ),
        ],
        execution_settings=execution_settings,
    )

    model = AIModel(
        model_name,
        kernel.create_function_from_prompt(
            function_name="chat",
            plugin_name="chatPlugin",
            prompt_template_config=prompt_template_config,
        ),
        kernel,
    )
    return model


async def run_semantic_function(model, context_variables=None):

    response = await asyncio.wait_for(
        model.invoke(context_variables=context_variables),
        timeout=MAX_API_TIMEOUT,
    )
    return response


logger = setup_logger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

kernel = initialize_kernel(api_key=OPENAI_API_KEY)

try:
    logger.info("Starting LLM modeules...")
    abst_sum_model = create_ai_model(
        kernel=kernel,
        model_name="abst_sum",
        prompt=ABST_SUM,
    )
    abst_sum_final_model = create_ai_model(
        kernel=kernel,
        model_name="abst_sum_final",
        prompt=ABST_SUM_FINAL,
    )
except Exception as e:
    logger.error("Error", e)

async def get_module_response(module_name, context_variables):
    if module_name == "abst_sum":
        model = abst_sum_model
    elif module_name == "abst_sum_final":
        model = abst_sum_final_model
    if model is None:
        raise ValueError(f'Invalid module name: {module_name}')
    response = asyncio.run(run_semantic_function(model, context_variables))
    return response


if __name__ == "__main__":
    context_variables = {
        "language": "en",
        "abstract": "Neutrophil chemotaxis plays a vital role in human immune system. Compared with traditional cell migration assays, the emergence of microfluidics provides a new research platform of cell chemotaxis study due to the advantages of visualization, precise control of chemical gradient, and small consumption of reagents. ",
    }
    response = get_module_response("abst_sum", context_variables=context_variables)
    print(response)
    json_response = json.loads(response)
    print(json_response["summary"])
    # context_variables = {
    #     "language": "en",
    #     "abstract_list": "This is a test abstract list.",
    # }
    # response = get_module_response("abst_sum_final", context_variables=context_variables)
    # print(response)
