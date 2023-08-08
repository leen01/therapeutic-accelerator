# Therapeutic Accelerator: An AI Research Assistant
Authors: Nicholas Lee, Vani Vijayakumar, Nic Brathwaite

## Mission
Our mission is to use artificial intelligence to accelerate pharmaceutical development by reducing time spent on literature reviews more time in the lab

## Product
With our innovative and insightful tool, we strive to disseminate biomedical knowledge in a digestible format. Founded in 2023, our team of Data Scientists worked tirelessly to bring to you ThaGPT, a chatbot tool for summaries and Q&A on articles from repositories such as Pubmed, Arxiv, bioRxiv, and medRxiv. As Data Scientists, it is part of our job to be stewards of information and we hope that this tool can help you stay on top of your field.

# Using this repo
## Organization of this Repository
- Setup: for building virtual environment. We used poetry to handle dependencies. The virtual environment can be setup using [these instructions](https://python-poetry.org/docs/) from poetry
- Scripts: Automation of data extraction

### Database Work: 
We attemped multiple solutions for setting up our initial database using tools such as Chroma and VectorStores. However, we ultimatley decided to set up our Postgresql Database using PostgresML to retrieve relevant papers using cosine distance.  


### Models:
- Base models: Our initial models consisted of using the huggingface library packages [here](https://huggingface.co/docs/transformers/index) to test the limit and fluency of the transformer model generated answers and summaries. We began by using google collab to create T5, BioBERT, and BioGPT models to condense the abstract of papers we had previously encoded.
Our initial findings showed that the T5 model worked best for loading, tokenizing, embedding and decoding our abstracts to generate summeries and Q&A. While BioBERT and BioGPT worked, they required more computational power to run and were significantly slower than T5. Our best performing model was a combination of OpenAI and LangChain. LangChain provided its own methods for reforming papers that enabled us to work with full text documents to generate answers and summaries quicker than the huggingface models.

T5 is an encoder - decoder model pre-trained on various tasks that works well with text tranformation and self supervised or unsupervised learning T5 Documentation: [here](https://huggingface.co/docs/transformers/model_doc/t5). 

- Similarity: In order to improve the time and accuracy of our summarization and Q&A models we developed a similiarity model to find the most relevant papers based on a users input. Using PostgresML with web_search we created similarity scores based on the distance and frequency of words found within papers and a user's search terms. The model is also capable of directly finding papers with the provided paper id or abstract.

- Model Work: LangChain
