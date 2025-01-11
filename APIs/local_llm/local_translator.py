from transformers import AutoProcessor, SeamlessM4TModel

# Initialize the processor and model
processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")


def translate_text(text: str, src_lang: str = "eng", tgt_lang: str = "ind") -> str:
    # Tokenize the input text with source and target languages
    inputs = processor(text, src_lang=src_lang, return_tensors="pt")

    # Generate translation
    output_tokens = model.generate(**inputs, tgt_lang=tgt_lang, generate_speech=False)

    translated_text_from_text = processor.decode(
        output_tokens[0].tolist()[0], skip_special_tokens=True
    )

    return translated_text_from_text


if __name__ == "__main__":
    foreign_text = "What is the capital of France?"
    response = translate_text(foreign_text, src_lang="eng", tgt_lang="fra")
    print(response)
