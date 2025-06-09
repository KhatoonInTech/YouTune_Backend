import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

# Load API keys rom environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(temperature=0.7, model_name="Gemma2-9b-It", groq_api_key=GROQ_API_KEY)
conversation = [
    {
        "role": "system",
        "content": "You are an AI that generates SEO optimized descriptions and hashtags for YT videos."
    }
]
def parse_response(response):
        if hasattr(response, 'content'):
            response_raw = response.content.strip()
        else:
            response_raw = str(response).strip()
        response_raw = response_raw.replace('``````', '').strip()
        response_raw = response_raw.replace('#', '').strip()
        response_clean = re.search(r'(\[.*\]|\{.*\})', response_raw, re.DOTALL)
        try:
            response_str = response_clean.group(0)
            return json.loads(response_str)
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            raise ValueError(f"JSON decoding failed. Raw response: {response_raw}\nError: {e}")

def gen_description_and_hashtags(title,script, filename='descriptions/description.json'):
    """Generates an SEO optimized description and hashtags for a YouTube video based on the provided title."""
    
    conversation.append({
        'role': 'user', 
        'content': f"""
        You are an expert in creating SEO optimized YouTube video descriptions and hashtags.
        
        ## TASK:
        Write a compelling and SEO optimized YouTube video description based on the Title: {title} and Script: {script}.
        
        ## REQUIREMENTS:
        1. The description should be between 150 to 250 words.
        2. Include relevant keywords naturally throughout the description.
        3. Provide a list of 5-10 relevant keywords/hashtags at the end of the description.
        4. The tone should be engaging, informative, and suitable for a YouTube audience.
        5. Ensure that the description encourages viewers to like, share, and subscribe.
        6. Instead of using **bold** or *italic* formatting, use a well-structured description with clear sentences or use unicode charaters instead.
        7 use emojis in description where necessary to make it eye-catching.
        ## Output Format:
        Your response must contain:
            - A well-structured description
            - Return keywords / hashtags as a JSON array of lowercase strings: [\"keywords1\", \"keywords2\", \"keywords3\", ...]
        
        **MAKE SURE TO GO THROUGH YOUR RESPONSE AND CHECK IF IT IS in REQUIRED FORMAT. If the description is not as required, REGENERATE it**        
    """})
    
    response = llm.invoke(conversation)
    content = response.content.strip()
    
    # Split content into description and hashtags
    parts = content.split('\n')
    description = '\n'.join(parts[:-1]).strip()
    hashtags = parse_response(parts[-1])
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump({'description': description, 'hashtags': hashtags}, f, indent=4)
    
    return {'description': description, 'hashtags': hashtags}

# re=gen_description_and_hashtags(
#     title="Laptop Maintenance Tips for Beginners",
#     script="""
#    Ever feel like your laptop is running slower than a snail in molasses? We've all been there!  
#    But don't worry, it's not a lost cause.  With a few simple maintenance tricks, you can give your laptop a much-needed performance boost. 
#    First, let's tackle the dust bunnies.  Use compressed air to blow out any debris from the vents, and wipe down your keyboard with a soft cloth.  
#    Next, run a disk cleanup utility to free up some valuable space. This will help your laptop run smoother and faster.
#    Finally, make sure your operating system is up to date. Security updates and bug fixes can make a huge difference in your laptop's performance. 
#    So there you have it, folks! Easy peasy laptop maintenance for beginners.  Give these tips a try and watch your laptop come back to life. Don't forget to like, share, and subscribe for more tech tips and tricks!
#     """,
#      filename=r'C:\Users\Super\OneDrive\Desktop\Youtube Automation\Projects\Laptop_Maintenance_Tips_for_Beginners\description.json'
#      )    

# print(f"Description: {re['description']}\n\n")
# print(f"Hashtags: {re['hashtags']}")     
# print(type(re['hashtags']))