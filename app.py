import streamlit as st
import json

from openai_assistants import client, create_assistant, initialise_review_thread, first_run, receive_json_response
from chunking import chunk_essay_text

def transform_to_dict(json_list):
    all_comments_dict = {}
    for i in json_list:
        for key, value in i.items():
            key = f"Comment {str(len(all_comments_dict) + 1)}"
            all_comments_dict.update({key: value})
    return all_comments_dict

def main():
    st.set_page_config(page_title="Essay Review App", page_icon="📝")
    st.title("Essay Review App")

    essay_question = st.text_area("Enter essay question: ", key="input_question")
    essay_text = st.text_area("Enter essay text: ", key="input_text", height=500)
    
    single_reviewer_system_prompt = f"""
    You need to perform tasks that involve reviewing a student's essay based on the question they were given. 
    The question is: {essay_question}
    The purpose of the essay is to answer the question most coherently.
    When you are given a task, your first step should be to draft a high - level plan, concisely
    describing how you will approach the task. Then execute that plan.
    """
    
    review_task_prompt = """
    Task: Write a list of feedback comments, similar to the suggestions a reviewer might make.
    The main focus of your feedback should be on clarity of the article. The arguments, and key concepts of the paper need to be clearly communicated to the reader. 
    The text needs to provide enough context and background information on the company.
    You need to leave feedback if the text is missing any key information and is not clear and concise.
    You need to leave feedback if the article uses redundant phrases or sentences.
    Be specific in your suggestions, including details
    about method and any particular
    steps the authors should follow. However, don 't
    suggest things that have already been included or
    addressed in the paper.
    Your review comments should have a clear purpose;
    obviously, it is always possible to simply say the
    authors should include more details, explanations, and logical chains, 
    but in practice the authors have
    limited wordcount and limited time to work, so
    each comment needs to have a clear purpose. Do not write comments on references.
    Do not write comments about using more words or transitional phrases, because usually the wordcount is strict.
    Avoid writing comments about providing more explanations for something, 
    as there may be an explanation further in the essay, but not in the chunk given to you.
    Return your comments in JSON format like this:
    {
        "Comment 1": "Comment",
        "Comment 2": "Comment",
        "Comment 3": "Comment",
    }
    Do not write anything else apart from the JSON object.
    """

    if st.button("Send"):
        with st.spinner("Processing text..."):
            # Step 1: chunk the essay text
            full_sentence_windows = chunk_essay_text(essay_text)

            # Step 2: create the assistant
            assistant = create_assistant(client=client, name="Clarity Reviewer", instructions=single_reviewer_system_prompt, model="gpt-4o", temperature=0)

            # Step 3: initialise the review thread
            review_thread = initialise_review_thread(client=client)

        with st.spinner("Processing initial review..."):
            # Step 4: loop over the chunks
            merged_jsons_of_initial_comments = []
            for i in range(len(full_sentence_windows)):
                try:
                    is_ready = first_run(client=client, thread=review_thread, assistant=assistant, i=i, full_sentence_windows=full_sentence_windows)
                    if is_ready == "Ready":
                        initial_review_comments = receive_json_response(client=client, thread=review_thread, prompt=review_task_prompt, assistant=assistant)
                        try:
                            initial_review_comments = json.loads(initial_review_comments)
                            merged_jsons_of_initial_comments.append(initial_review_comments)
                        except Exception as e:
                            print(f"Failed to decode JSON for window {i}: {e}")
                            continue
                except Exception as e:
                    print(f"Error processing window {i}: {e}")
                    continue

            all_initial_comments_dict = transform_to_dict(merged_jsons_of_initial_comments)
        
        refine_prompt = f"""
        You are given a list of comments for the philosophical essay that answers this question: {essay_question}, 
        each group of comments was written for a chunk. You have previously reviewed the essay and provided feedback on clarity.
        Because of the way the comments were generated, if something was commented on in one chunk, 
        may have been explained in another chunk.
        Have a look and remove redundant or unclear comments that do not add value to the feedback.
        At the same time, do not delete comments that are important and have a significant impact on the article's clarity.
        Do not delete too many comments, as you want to preserve detailed feedback.
        The goal is for the comment to be detailed and helpful. 
        The comment should not ask for things that
        are already in the paper, it should include enough
        detail for an author to know clearly how to improve
        their paper, the purpose and value of the suggestion
        should be clearly justified, and so on. Remove the
        comment if it is bad (i.e., if it fails to meet
        those criteria, if it is redundant and unclear). 
        Do not suggest to provide a brief summary or examples to improve clarity, 
        as there is likely no space due to tight wordcount.
        Be concise and sensible about the comments that you output after refinement.
        You should focus on "major" comments that
        are important and have a significant impact on the
        article's clarity, as opposed to minor comments about
        things like writing style or grammar. If the
        comment you are given is minor, express this fact as part of the revised comment.

        Here is a list of chunks:
        {full_sentence_windows}
        Here is a list of comments (comments are respective for each chunk in the list above):
        {all_initial_comments_dict}
        """

        with st.spinner("Refining comments..."):
            # Step 5: refine the comments
            refined_comments = receive_json_response(client=client, thread=review_thread, prompt=refine_prompt, assistant=assistant)
            refined_comments = json.loads(refined_comments)
        
        # Display initial comments
        st.subheader("Initial Comments")
        for key, value in all_initial_comments_dict.items():
            st.write(f"{key}: {value}")
        
        # Display the refined comments
        st.subheader("Refined Comments")
        for key, value in refined_comments.items():
            st.write(f"{key}: {value}")

if __name__ == "__main__":
    main()
    