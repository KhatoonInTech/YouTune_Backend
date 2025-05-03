import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

# Load API keys from environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(temperature=0.7, model_name="Gemma2-9b-It", groq_api_key=GROQ_API_KEY)
conversation = [
    {
        "role": "system",
        "content": "You are an AI that generates scripts, and scene prompts in one session."
    }
]

def gen_script_and_scenes(title, filename='scripts/script.md'):
    """Generates a script and prompts for pexel stock images and videos for a YouTube video based on the provided title."""
   
    ## SCRIPT GENERATION
    conversation.append({
        'role': 'user', 
        'content': f"""
        You are an experienced storyteller and content writer, best known for creating YouTube video scripts.

        ## TASK:
        Write a compelling and concise YouTube video script based on the Title: {title}.

        ## STRICT REQUIREMENTS:
        1. CRITICAL: The total word count for ALL **(Narrator)** lines COMBINED must be BETWEEN 150 and 225 words. You MUST count the words accurately.
        2. Use a narrator's speaking rate of 2.5 words per second to calculate the time duration of each **(Narrator)** section. For example, a 35-word line takes 14 seconds.
        3. Include timestamp ranges for each scene or narration block,strictly before corresponding **(Narrator)** line.
        CRITICAL:    STRICTLY CALCULATE timestamp ranges AS FOLLOWS 
                    duration of timestamp = no. of words after "**(Narrator)**" /2.5   
        4. Format each scene clearly on a new line and provide 3-5 scenes total.
        5. The script should be suitable for a SHORT video (1.5 to 2 minutes).
        6. Structure should include:
            - A strong hook at the beginning
            - An informative and entertaining body
            - A concise conclusion
        7. Tone should be conversational, engaging, and informative.
        CRITICAL: Make Sure to include a CALL-TO-ACTION at the end of the script, encouraging viewers to like, share, and subscribe.
        8. Use unique phrasing and storytelling – no clichés or generic commentary.
        9. IMPORTANT: Every line the narrator says MUST start with "**(Narrator)**", followed by the spoken line.
        10. If the word count is outside 150-225, revise until it’s within range.
        11. DO NOT include any explanations or extra text beyond the final script and word count.
        ## Output Format:
                Your response must contain timestamps and narrator's lines as following format:

                        **(Scene # 1)** describe the  visuals and background of the narrator's words
                        **(TIMING :)** -:-- - -:-- 
                        **(Narrator)** First line of the scene


        REPEAT THIS PATTERN STRICTLY FOR ALL THE SCENES.
        **MAKE SURE TO GO THROUGH YOUR RESPONSE AND CHECK IF IT IS in REQUIRED FORMAT. If the script is not as required, REGENERATE it**        
    """
    }) 
    
    script_response = llm.invoke(input=conversation)
    script = script_response.content
    conversation.append({
        'role': 'assistant', 
        'content': script
    })
    #Check if filename dir exists
    if not os.path.exists(filename):
         os.makedirs(os.path.dirname(filename), exist_ok=True)
    # Save the script to a file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(script)

    ## SCENES GENERATION     
    '''
    Now generate scenes for our video.
    These scenes are obtained by the open-source lib of PEXELS stock images and stock videos.
    Thus for now we have to obtain keywords to search PEXES libraries for stock images and videos.
    These keywords are obtained by the LLM itself from its previously generated script.
    '''
    
    conversation.append({
        'role': 'user', 
        'content': f"""
            ## TASK:
                You are given a YouTube video title: **{title}**, along with its supporting script. Your main goal is to derive the **core visual themes** from the *title*, using the script only as a **supplementary reference** to expand or clarify visual ideas implied by the title. Based on this, generate **EXACTLY 15 descriptive and visually rich keywords** suitable for searching stock videos/images on Pexels. The keywords must be tightly aligned with the **central theme of the title**, not loosely derived from incidental details in the script.

                For example, if the title is about “Luxury Desert Living,” then the keywords must reflect *desert landscapes*, *luxurious lifestyles*, *camels*, *modern villas*, etc.—even if the script mentions general things like "sunsets" or "water." Avoid generic or visually ambiguous terms like “freedom” or “texture” that could lead to irrelevant results.

             """ + """
             ## STRICT REQUIREMENTS:
                1. Focus on the **title** as the core source of thematic direction. Use the script only to deepen or clarify visuals that support the title’s message.
                2. Identify **3 distinct visual sections/scenes** based on the narrative arc suggested by the title and script.
                3. For each scene, generate **4–5 precise, visually-descriptive keywords**, totaling **exactly 15 keywords** overall.
                4. Keywords must be **concrete, visual, and searchable** on Pexels (e.g., "camel ride", "sand dunes", "gold jewelry", etc.).
                5. Avoid abstract, metaphorical, or non-visual words (e.g., "opulence", "power", "emotion").
                6. Double-check that the keywords are **not repetitive**, not off-theme, and that the full set represents the **visual story implied by the title**.
                7. Return only the 3 scene headers and their associated keywords.

                ## Output Format:
                Your response must contain strictly a total of 15 descriptive keywords only for the entire script 
                Provide your response STRICTLY in valid python dictionary written in txt format as shown below:
                
                {"scene_1": ["keyword1", "keyword2", "keyword3, "keyword4", "keyword5"],"scene_2": ["keyword6", "keyword7", "keyword8", "keyword9", "keyword10"],"scene_3": ["keyword11", "keyword12", "keyword13", "keyword14", "keyword15"]}
                
                **MAKE SURE TO Count your keywords again to verify the total is between 12-15 keywords.
                **DO NOT include any additional explanations or context.**
                """
                    })
    
    scene_response = llm.invoke(input=conversation)
    # print(scene_response.content)
    try:
          scenes = json.loads(scene_response.content)  # Convert JSON string to dict
    except json.JSONDecodeError:
          print("Failed to parse JSON response")
          scenes = {}

    return {'script': script, 'scenes': scenes}


if __name__ == '__main__':
    title = "The Future of AI: What Lies Ahead"
    result = gen_script_and_scenes(title)
    print("Generated Script:")
    print(result.get('script'))
    # print(json.dumps(result.get('script'), indent=4))