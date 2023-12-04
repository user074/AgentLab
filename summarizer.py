
import openai
import os
# import fitz  # PyMuPDF
# from nougat_ocr import Nougat

summary_instructions = "Now you are reviewing the summarized version of the paper.\
Give a concise summary of the paper for the literature review. \
Answer following questions in the summary:\
What problem is addressed in the paper?\
Is it a new problem? If so, why does it matter? If not, why does it still matter?\
What is the key to the solution? What is the main contribution?\
Do the experiments sufficiently support the claims?"

summary = instruct_text_file('condensed_condensed_paper.txt', summary_instructions)

#strengths
strengths_instructions = "Now you are reviewing the summarized version of the paper.\
Give a concise statement of the strengths of the paper for the literature review. \
What about the paper provides value - - interesting ideas that are experimentally validated, an insightful organization of related work, new tools,\
impressive results. Most importantly, what can someone interested in the topic learn from the paper. What are the key contributions and why do they matter?\
Use bullet points to write the strengths statement."

strengths = instruct_text_file('condensed_condensed_paper.txt', strengths_instructions)

#weaknesses
weaknesses_instructions = "Now you are reviewing the summarized version of the paper.\
Give a concise statement of the weaknesses of the paper for the literature review. \
What detracts from the contributions -- Does the paper lack controlled experiments to validate the contributions?\
Are there misleading claims or technical errors? Is it possible to understand (and ideally reproduce) the method and experimental \
setups by reading the paper?What are the key contributions and why do they matter? What aspects of the paper most need improvement?\
Use bullet points to write the weaknesses statement."

weaknesses = instruct_text_file('condensed_condensed_paper.txt', weaknesses_instructions)

final_summary = '**Summary**'+'\n'+summary + '\n\n' + '**Strengths**'+'\n'+strengths + '\n\n' + '**Weaknesses**'+'\n'+weaknesses

with open('literature_review.txt', 'w') as file:
    file.write(final_summary)

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo-0613":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows {role/name}\n{content}\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
     
#read text from file and convert to list of messages for openai api

def read_without_references(filename):
    os.system(f"nougat {filename}")
    filename= filename.split('.pdf')[0]+'.mmd'
    with open(filename, 'r') as file:
        content = file.readlines()

    # Define a variable to store the final content without references
    final_content = []

    # Flag to indicate if the "References" section has started
    references_started = False

    for line in content:
        if "References" in line:
            references_started = True
        if not references_started:
            final_content.append(line)

    return ''.join(final_content)

def convert_text_to_messages(text, user_instructions=None):
    messages = [
    {"role": "system", "content": "You are an expert academic journal reviewer in CVPR, IEEE, and ACM.\
        You are reviewing a paper.\
        You need to be constructive to the authors. It is necessary to be critical, but avoid offending the authors.\
        Instead, suggest how they could make the paper better.\
        "},
    # {"role": "user", "content": "Help me to polish following text."},
    ]
    if user_instructions:
        messages.extend([{"role": "user", "content": user_instructions} ])

    messages.extend([{"role": "user", "content": text} ])
    return messages


def convert_messages_to_text(messages):
    text = ''
    for message in messages:
        if message['role'] == 'user':
            text += 'Human: ' + message['text'] + '\n'
        elif message['role'] == 'assistant':
            text += 'AI: ' + message['text'] + '\n'
    return text

def write_text_to_file(text, filename):
    with open(filename, 'w') as file:
        file.write(text)

def write_messages_to_file(messages, filename):
    write_text_to_file(convert_messages_to_text(messages), filename)

#count tokens in text
def num_tokens_from_text(text, model = "gpt-3.5-turbo-0613"):
    messages = convert_text_to_messages(text)
    return num_tokens_from_messages(messages, model)

#read the text file, then return a list of texts whereas each contains less than given number of tokens
def split_text_into_list(text, max_tokens=4096):
    messages = []
    message = ''
    for line in text.splitlines():
        message_token = num_tokens_from_messages(convert_text_to_messages(message))
        line_token = num_tokens_from_messages(convert_text_to_messages(line))
        if message_token + line_token < max_tokens/2:
            message += line + '\n'
        else:
            messages.append(message)
            message = line + '\n'
    messages.append(message)
    return messages

#call openai api to polish the text
def instruct_text(text,user_instructions, model = "gpt-3.5-turbo"):
    messages = convert_text_to_messages(text, user_instructions=user_instructions)
    response = openai.ChatCompletion.create(model=model, messages=messages)
    return response

#Polish an entire txt file then write the results into a new file
def summarize_text_file(filename, model = "gpt-3.5-turbo"):
    text = read_without_references(filename)
    paragraphs = split_text_into_list(text, max_tokens=4096)
    polished_text = ''
    user_instructions = "The paper is too long. Now you are summarizing it part to part. Provide a summary of given section. Make it shorter but keep all the technical details."
    for paragraph in paragraphs:
        result = instruct_text(paragraph, user_instructions, model)
        polished_text += result['choices'][0]["message"]["content"]
    return polished_text

def write_text_to_file(text, filename):
    with open(filename, 'w') as file:
        file.write(text)

def summarize_text_file_to_file(filename, outputFileName, model = "gpt-3.5-turbo"):
    text = summarize_text_file(filename, model)
    write_text_to_file(text, outputFileName)

def cost_estimation(filename):
    text = read_without_references(filename)
    messages = convert_text_to_messages(text)
    model = "gpt-3.5-turbo-0613"
    paragraphs = split_text_into_list(text, max_tokens=4096)
    estimated_cost = num_tokens_from_messages(messages, model) * (0.0015 + 0.002) / 1000
    print(f"{num_tokens_from_messages(messages, model)} prompt tokens counted.")
    print(f"Number of paragraphs to process: {len(paragraphs)}")
    print(f"Estimated cost using gpt-3.5-turbo: ${estimated_cost}")

def instruct_text_file(filename, user_instructions, model = "gpt-3.5-turbo"):
    text = read_text_from_file(filename)
    paragraphs = split_text_into_list(text, max_tokens=4096)
    polished_text = ''
    for paragraph in paragraphs:
        result = instruct_text(paragraph, user_instructions, model)
        polished_text += result['choices'][0]["message"]["content"]
    return polished_text

def instruct_text_wfile(text, user_instructions, model = "gpt-3.5-turbo"):
    paragraphs = split_text_into_list(text, max_tokens=4096)
    polished_text = ''
    for paragraph in paragraphs:
        result = instruct_text(paragraph, user_instructions, model)
        polished_text += result['choices'][0]["message"]["content"]
    return polished_text
