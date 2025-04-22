from transformers import pipeline
import random

# Load the question-answering pipeline

# qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2", device=-1)  # forces CPU
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=-1)


def generate_flashcards(summary_text, num_questions=5):
    """
    Generate flashcards from summarized text.
    
    Args:
        summary_text (str): The text to generate flashcards from.
        num_questions (int): Number of flashcards to generate.

    Returns:
        List[Tuple[str, str]]: A list of (question, answer) pairs.
    """
    sentences = [s.strip() for s in summary_text.split('.') if len(s.split()) > 5]
    flashcards = []

    for _ in range(num_questions):
        if not sentences:
            break

        sentence = random.choice(sentences)
        question = f"What does this mean: '{sentence[:50]}...'?"

        try:
            result = qa_pipeline(question=question, context=summary_text)
            answer = result['answer']
            flashcards.append((question, answer))
        except Exception as e:
            flashcards.append((question, f"(Error generating answer: {e})"))

    return flashcards
