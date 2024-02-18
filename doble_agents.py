import os
import yaml
import json
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.code_utils import DEFAULT_MODEL, UNKNOWN, content_str, execute_code, extract_code, infer_lang
from autogen.agentchat.utils import gather_usage_summary
from autogen.agentchat.contrib.capabilities import context_handling

####################### CONFIGURATION #######################
agents_description_name_file = "agents_descriptions.yaml"


#######################  Load Agents Descriptions #######################
path_file_agents_description = os.path.join(os.path.dirname(__file__), agents_description_name_file)
agents_description = yaml.load(open(path_file_agents_description, "r"), Loader=yaml.FullLoader)

#######################  Context Handling - Add super power Transform Chat History to Agents #######################
manage_chat_history = context_handling.TransformChatHistory(max_tokens_per_message=1000, max_messages=10, max_tokens=16000)


#######################  Auxiliary Functions #######################
def get_description(name_agent, type_description):
    agents = agents_description['agents']
    for agent in agents:
        if agent['name_agent'] == name_agent:
            return agent[type_description].strip().replace("\n", " ").replace("\t", " ").replace("  ", " ")
    raise Exception("Agent not found in the description file")

def get_model(model_name):
    with open("oai_config.json") as f:
        config = json.load(f)
        return [config[model_name]]

def is_termination_msg(content) -> bool:
    have_content = content.get("content", None) is not None
    if have_content and "TERMINATE" in content["content"]:
        return True
    return False

def cost_summary(agents: list):
    for agent in agents:
        print(agent.name, ":", agent.get_total_usage())
    total_usage_summary, actual_usage_summary = gather_usage_summary(agents)
    print("Total usage summary for all agents:", total_usage_summary)

#######################  Create Agents #######################
programer = AssistantAgent(
    name="programer", 
    human_input_mode="NEVER",
    llm_config={"config_list": get_model("mixtral-8x7b"), "seed": 69}, 
    code_execution_config={"work_dir": "coding", "use_docker": False},
    max_consecutive_auto_reply=10,
    system_message="A python programer"
)

manager = UserProxyAgent(
    name="manager",
    code_execution_config=False,
    human_input_mode="TERMINATE",
    is_termination_msg=is_termination_msg,
    llm_config={"config_list": get_model("mixtral-8x7b"), "seed": 69}, 
    max_consecutive_auto_reply=5

)
manage_chat_history.add_to_agent(manager)


#######################  Start Chat #######################
manager.initiate_chat(programer, message="Make a python file with script to get a sequence of OHLCV data from a stock cryptocurrency of binance. Use CCTX with a principal library. Use TERMINATE when you finish.")
cost_summary([programer, manager])

