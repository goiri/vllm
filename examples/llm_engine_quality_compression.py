import argparse
import os
from datetime import datetime

from vllm import EngineArgs, LLMEngine, SamplingParams


def main(args: argparse.Namespace):
    # Parse the CLI argument and initialize the engine.
    engine_args = EngineArgs.from_cli_args(args)
    engine = LLMEngine.from_engine_args(engine_args)

    # Test prompts from files.
    test_prompts = []
    folder_name = "/home/azureuser/prompts_qa"
    for file_name in os.listdir(folder_name):
        with open(folder_name + "/" + file_name, "r", encoding="utf-8") as input_prompt_file:
            prompt = input_prompt_file.read()
            test_prompts.append((prompt, SamplingParams(n=2, best_of=5, temperature=0.8, top_p=0.95, frequency_penalty=0.1)))

    # Run the engine by calling `engine.step()` manually.
    request_id = 0
    step_id = 0
    while True:
        # To test continuous batching, we add one request at each step.
        if test_prompts:
            prompt, sampling_params = test_prompts.pop(0)
            engine.add_request(str(request_id), prompt, sampling_params)
            request_id += 1

        request_outputs = engine.step()
        step_id += 1
        print(f"[{datetime.now()}] STEP {step_id}\n")
        for request_output in request_outputs:
            if request_output.finished:
                print(f"[{datetime.now()}] Request: {request_output.request_id}")
                print(f"[{datetime.now()}] Prompt: {request_output.prompt}")
                print(f"[{datetime.now()}] Output: {request_output.outputs[0].text}")
                print()
                # TODO measure quality with BARTSCore

        if not (engine.has_unfinished_requests() or test_prompts):
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Demo on using the LLMEngine class directly')
    parser = EngineArgs.add_cli_args(parser)
    args = parser.parse_args()
    main(args)