import spacy

def split_into_sentence_windows(text, window_size):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = list(doc.sents)
    if len(sentences) <= window_size:
        return [sentences]
    else:
        sentence_windows = [sentences[i:i+window_size] for i in range(0, len(sentences) - window_size + 1, window_size)]
        return sentence_windows
    
def loop_over_chunks(i, full_sentence_windows):
    chunk_prompt = f"""
    A chunk of text from a student's essay is shown
    below:
    --- START PAPER CHUNK ---
    { full_sentence_windows[i] }
    --- END PAPER CHUNK ---
    Write " Ready " if you have understood the assignment.
    You will then be given tasks.
    """
    return chunk_prompt

def chunk_essay_text(essay_text):
    sentence_windows = split_into_sentence_windows(essay_text, window_size=8)
    full_sentence_windows = []
    for window in sentence_windows:
        merged_text = ' '.join([str(sent) for sent in window])
        full_sentence_windows.append(merged_text)
    return full_sentence_windows