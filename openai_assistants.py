import backoff
import time
from openai import OpenAI
from chunking import loop_over_chunks

# Create the AOAI client to use for the proxy agent.
client = OpenAI(api_key="")

def create_assistant(client, name, instructions, model, temperature):
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        temperature=temperature
    )
    return assistant

def initialise_review_thread(client):
    thread = client.beta.threads.create()
    return thread

@backoff.on_exception(backoff.constant, Exception, max_tries=5, interval=60, jitter=None)
def create_and_poll_review_run(client, thread, assistant, response_format):
    review_run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        response_format= { "type": response_format }
    )
    return review_run

def handle_review_response(client, thread, review_run):
    try:
        if review_run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id,
            )
            return messages.data[0].content[0].text.value
        else:
            raise Exception(f"Review run not completed. Status: {review_run.status}")
    except Exception as e:
        print(e)
        return review_run.status

@backoff.on_exception(backoff.constant, Exception, max_tries=5, interval=60, jitter=None)
def first_run(client, thread, assistant, i: int, full_sentence_windows):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=loop_over_chunks(i, full_sentence_windows)
    )
    review_run = create_and_poll_review_run(client, thread, assistant, response_format="text")
    return handle_review_response(client, thread, review_run)

@backoff.on_exception(backoff.constant, Exception, max_tries=5, interval=60, jitter=None)
def receive_json_response(client, thread, prompt, assistant):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )
    time.sleep(30)
    review_run = create_and_poll_review_run(client, thread, assistant, response_format="json_object")
    return handle_review_response(client, thread, review_run)