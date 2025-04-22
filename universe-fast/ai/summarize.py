from transformers import pipeline
from PyPDF2 import PdfReader

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_notes(uploaded_file):
    reader = PdfReader(uploaded_file)
    raw_text = ""
    for page in reader.pages:
        raw_text += page.extract_text() + "\n"

    text = raw_text.replace("\n", " ")
    sentences = text.split(". ")

    max_chunk_chars = 800
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_chars:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())

    full_summary = ""
    for i, chunk in enumerate(chunks):
        try:
            input_length = len(chunk.split(" "))
            max_length = min(250, int(input_length * 0.6))  # Make sure summary is shorter
            min_length = max(30, int(input_length * 0.3))   # Ensure it’s not too short

            result = summarizer(
                chunk,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]['summary_text']

            full_summary += f"Chunk {i+1} Summary:\n{result}\n\n"

        except Exception as e:
            full_summary += f"(Error summarizing chunk {i+1}: {e})\n\n"

    return full_summary
