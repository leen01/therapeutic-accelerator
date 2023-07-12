import tensorflow as tf
import tensorflow_hub as hub


### Instead of summarization can be used for classification of papers
def biobert_classifier(
    embedding_size=200,
    input_dimensions=3,
    hidden_layers=0,
    max_sequence_length=512,
    learning_rate=0.01,
):
    input_ids = tf.keras.layers.Input(shape=embedding_size, name="input_ids")
    token_type_ids = tf.keras.layers.Input(shape=embedding_size, name="token_type_id")
    attention_mask = tf.keras.layers.Input(shape=embedding_size, name="attention_mask")

    model_inputs = {
        "input_ids": input_ids,
        "token_type_ids": token_type_ids,
        "attention_mask": attention_mask,
    }

    embedding_matrix = tf.keras.layers.Embedding(200)

    normalization_layer = tf.keras.layers.BatchNormalization()

    attention_layer = tf.keras.layers.Attention()

    pooler_layer = bio_bert_model(model_inputs)[0]

    dense_layer = tf.keras.layers.Dense(100, activation="relu")(pooler_layer)

    dropout_layer = tf.keras.layers.Dropout(0.3)(dense_layer)

    final_layer = tf.keras.layers.Dense(1, activation="relu")(dropout_layer)

    classification_layer = tf.keras.layers.Dense(1, activation="sigmoid")(final_layer)

    model = tf.keras.Model(
        inputs=[input_ids, token_type_ids, attention_mask],
        outputs=[classification_layer],
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss=tf.keras.losses.BinaryCrossentropy,
        metrics=[tf.keras.metrics.Accuracy, tf.keras.metrics.Precision],
    )

    return model


### T5 Abstractive Text Summarization Model
def t5summary_model(tokenizer, text, t5model):
    summarize = "summarize: "
    encoding = tokenizer([summarize + text], return_tensors="tf")
    output = t5model.generate(
        encoding.input_ids,
        num_beams=3,
        no_repeat_ngram_size=2,
        top_k=10,
        top_p=80,
        max_length=50,
        min_length=30,
    )
    return [
            tokenizer.decode(
                w, skip_special_tokens=True, clean_up_tokenization_spaces=True
            )
            for w in output
        ]