from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from transformers import T5Tokenizer


def get_input():
    input_string = input("Enter a question: ")
    print("You entered: " + input_string)
    return input_string


# Text splitter for processing input into chunks
recursive_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ".", "?", "!"],
    chunk_size=500,
    chunk_overlap=20,
    length_function=len,
)

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=500,
    chunk_overlap=20,
    length_function=len
)

max_sequence_length = 1200
embedding_size = 200

T5tokens = T5Tokenizer.from_pretrained(
    't5-base', model_max_length=max_sequence_length)

def split_tokenize(prompt):
    """ Split text into chunks and tokenize each chunk"""
    tokens = [T5tokens.encode(chunk) for chunk in text_splitter.split_text(prompt)]
    print(tokens)
    return tokens

if __name__ == '__main__':
    split_tokenize(get_input())
