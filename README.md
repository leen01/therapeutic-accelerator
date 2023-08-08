# Therapeutic Accelerator: An AI Research Assistant
Authors: Nicholas Lee, Vani Vijayakumar, Nic Brathwaite

## Mission
Our mission is to use artificial intelligence to accelerate pharmaceutical development by reducing time spent on literature reviews more time in the lab

## Product
With our innovative and insightful tool, we strive to disseminate biomedical knowledge in a digestible format. Founded in 2023, our team of Data Scientists worked tirelessly to bring to you ThaGPT, a chatbot tool for summaries and Q&A on articles from repositories such as Pubmed, Arxiv, bioRxiv, and medRxiv. As Data Scientists, it is part of our job to be stewards of information and we hope that this tool can help you stay on top of your field.

## Using this repo

##### Repo Dependencies

For building virtual environment. We used poetry to handle dependencies. The virtual environment can be setup using [these instructions](https://python-poetry.org/docs/) from poetry. 

##### Model Instructions
In order to run these models on your local device, you will need to install the packages within our required.txt file. The notebook files will contain the correct import calls.

## Links to deliverables

Web Deliverable: https://vanivk14.wixsite.com/tagpt 

Demo of App: https://app.hex.tech/604dd43f-9bf2-4f53-b2ad-a57886ed9dc6/app/d8ff2ed8-06ad-4d32-892e-def0c050dd4f/latest

Final Presentation: Therapeutic Accelerator - Final Presentation.pdf in main branch

## Organization of this Repository
  
##### data Folder

API Calls / S3 data file / Duck DB work to get data from Semantic Scholar.  

##### EDA Folder

Exploratory analysis for dataset, including filtering process for data. 

##### similiarty Folder 

Notebooks, SQL script, and Terminal code related to Similiarity model.  Notebook "Final Similiarity" has all of the final functions. 

##### Base_Models & latest_models Folder

All work related to summarization and Q&A modeling, wit latest_models containing the final notebooks of each model we tested. 

##### Model Eval Folder

Notebooks related to T5 Model and Langchain Model evaluation. 

##### Web Deliverable Folder

Final Notebook for hex web app.


## Database Work
We attemped multiple solutions for setting up our initial database using tools such as Chroma and VectorStores. However, we ultimatley decided to set up our Postgresql Database using PostgresML to retrieve relevant papers using cosine distance.  


## Models
#### Base models
Our initial models consisted of using the huggingface library packages [here](https://huggingface.co/docs/transformers/index) to test the limit and fluency of the transformer model generated answers and summaries. We began by using google collab to create T5, BioBERT, and BioGPT models to condense the abstract of papers we had previously encoded.
Our initial findings showed that the T5 model worked best for loading, tokenizing, embedding and decoding our abstracts to generate summeries and Q&A. While BioBERT and BioGPT worked, they required more computational power to run and were significantly slower than T5. Our best performing model was a combination of OpenAI and LangChain. LangChain provided its own methods for reforming papers that enabled us to work with full text documents to generate answers and summaries quicker than the huggingface models.

T5 is an encoder - decoder model pre-trained on various tasks that works well with text tranformation and self supervised or unsupervised learning T5 Documentation: [here](https://huggingface.co/docs/transformers/model_doc/t5). 

#### Similarity
In order to allow users to expand their knowledge base of a topic, we created a model that would find similiar papers based on a corpusID or texr input. We also used this function improve the time and accuracy of our summarization and Q&A models, we developed a similiarity model to find the most relevant papers based on a users input. Using Septer Embeddings and PostgresML with Postgres Full Text search, we created similarity scores based on the distance and frequency of words found within papers and a user's search terms. 

#### Model Work 
LangChain provides the software architecture necessary to process large volumes of textual data paired with LLMs. For our project, we chose OpenAi because of how well it integrates with LangChain and it's flexibility to handle abstracts, full text documents, and perform Q&A with the LangChain framework. The structure for the summarization model handles text by mapping and reducing documents into partitioned segments to be fed into our model and generating a solution that encompasses each portion of a document. While our Q&A model uses a refined approach by thoroughly reviewing a given document and continuosly updating its generated answer as it parses it through the model.
  
The hugging face transformers required additional functions to handle larger inputs of text and our research led us to discover models such as LED (LongtransformerEncoderDecoder), BigBirdPegasus, variations of T5, variations of LED, and pipelines that utilize a combination of tokenizers and models to perform specific tasks. When generating solutions we adjusted additional parameters of the model such as the search beams, repeat n gram size, probability distribution threshold, unique word count, next word prediction, and overall length of each response.

## Evaluation
Our best evaluation and fluency check was using the L1 and L2 rouge scores to compare the common occurence of words from our generated summaries with the abstracts themseleves. Thid was a low cost and standardized way to benchmark our models. 

## Conclusion
We hope that phramacist, scientist, researchers, students, and those who come across our project find the best suitable use for it within their professional and academic careers.

