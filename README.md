# Essay Review Streamlit App by AI Agents
#### To run: 
1. clone repository locally
2. run in terminal 'pip -r requirements.txt'
3. provide your OpenAI API key in openai_assistants.py
4. run in terminal 'streamlit run app.py'

The objective of this app is to provide comments for the philosophy essay on the dimension of Clarity. I have tested the output for essays of 1000-2500 word count.
The specificity of the philosophy essay questions is reflected in the review prompts.
For example, review_task_prompt explicitly addresses the thesis of the essay and how the arguments should refer back to the thesis, as well as that the essay has to be understood by a reader who has knowledge in philosophy.
In refine_prompt I also explicitly address comments for a 'philosophy essay'.

You need to provide essay question and the text of the essay in the input of the app.
#### Step-by-step process of how the app runs:
1. The text of the essay is split into same-size sentence windows, currently set at 8 sentences
2. Each chunk of text is shown to the assistant and the assistant has to respond "Ready" if it has understood the assignment and is ready to execute tasks
3. Each chunk receives comments on Clarity, usually 3-4 comments per chunk
4. Once the comments for all chunks are received, the JSON object is stored in the session for all comments merged (not a separate JSON object per chunk)
5. The JSON object with all comments is used for refining initial comments, thereafter the assistant picks the comments that it deems to be best, also keeping their original number and original text from the merged JSON (even though I have noticed that sometimes it rewrites the comments if the temperature parameter on the assistant is 1)
6. When the output is ready you will first see 'Initial Comments' and 'Refined Comments' below

This approach has been inspired by this paper:
Hope, T., Birnbaum, L., & Downey, D. (2024). MARG: Multi-Agent Review Generation for Scientific Papers. ArXiv. https://arxiv.org/abs/2401.04259

The paper focuses on Multi-Agent review generation, also experimenting with Single-Agent reviews. I have picked the dimension of Clarity that the paper has presented. I have also chosen the approach of a Single Reviewer with improved prompts and detailed tasks, as I thought that implementing multiple AI agents for a small-scale task like mine could be redundant.

The stage of refining comments can use a lot of improvement, as sometimes just reducing the number of comments without providing more context and improving them is not very helpful. The text of the comment staying the same is not expected behaviour, but it changes with the temperature parameter of the assistant, as I have mentioned above.

#### Example output for the essay on Kant's Categorical Imperative
<img width="876" alt="Screenshot 2024-11-26 at 23 49 32" src="https://github.com/user-attachments/assets/b33b5a74-4e33-4ed9-b783-26033493a0c5">


