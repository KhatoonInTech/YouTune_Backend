from gtts import gTTS
import os
import re
from datetime import datetime
from moviepy import *

# Function to extract NARRATOR lines
def extract_narration(script):
    """
    Extracts text following 'NARRATOR:' lines.
    """
    timestamps=[]
    narrator_parts = []
    for line in script.splitlines():  
        if line.startswith('**(Narrator)**'):
            narrator_text = line.replace('**(Narrator)**', '').strip()
            narrator_parts.append(narrator_text)
            
    return narrator_parts

def clean_script(text):
    """
    Extract Narator lines and Removes Markdown special characters from the script.
    """
    # Extract NARRATOR lines
    text = ''.join(extract_narration(text)) 
    
    # Remove headings (#)
    text = re.sub(r'#+', '', text)
    
    # Remove bold/italic markers (*, _, **, __)
    text = re.sub(r'\*+|_+', '', text)

    # Remove blockquotes (>)
    text = re.sub(r'>+', '', text)

    # Remove code blocks and inline code (`...`)
    text = re.sub(r'`+', '', text)

    # Remove dashes (-) used in lists
    text = re.sub(r'-+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # print('\n\ntext=',len(text.split(',')))

    return text

def voice_over(script, output_file="../Projects/narration.wav"):
    
    #Check if output_file dir exists
    if not os.path.exists(output_file):
         os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Clean the script to remove unwanted characters
    narration = clean_script(script)
    tts = gTTS(text=narration, lang="en", slow=False)
    tts.save(output_file)
    # os.system(f"start {output_file}")  # Adjust this for your OS (e.g., `open` on macOS)
    return narration,output_file


# if __name__ == "__main__":
#     script='''
# **(Scene # 1)**  A bustling street scene filled with vibrant food stalls, aromas wafting through the air. The narrator stands amidst the crowd, a curious smile on their face.
# **(TIMING :)** 00:00 - 00:14
# **(Narrator)** Forget fancy restaurants, today we're diving headfirst into a world of flavor – street food! 

# **(Scene # 2)** Close-ups of sizzling skewers, colorful tacos, steaming bowls of noodles, and other mouthwatering dishes. The narrator points and gestures excitedly.
# **(TIMING :)** 00:14 - 00:40
# **(Narrator)** From spicy samosas to melt-in-your-mouth bao buns, street food is a global tapestry of culinary delights. Every corner offers a unique adventure for your taste buds.

# **(Scene # 3)**  The narrator interacts with a friendly street vendor, trying a dish and offering enthusiastic praise.
# **(TIMING :)** 00:40 - 01:09
# **(Narrator)**  This sizzling skewer? *divine!*  It's a symphony of textures and spices, and the aroma alone is enough to make you drool. 

# **(Scene # 4)**  A montage of diverse people enjoying street food – families sharing meals, friends laughing over bowls of noodles, solo travelers savoring a delicious bite.
# **(TIMING :)** 01:09 - 01:37
# **(Narrator)**  Street food isn't just about the food; it's about the experience. It's the energy of the crowd, the stories shared over a plate, the joy of discovering something new.

# **(Scene # 5)** The narrator stands against a backdrop of colorful street food stalls, offering a final thought.
# **(TIMING :)** 01:37 - 01:58
# **(Narrator)**  So, next time you're craving a culinary adventure, step off the beaten path and explore the world of street food. You won't regret it!

# **Word Count: 197** 

#         '''
#     audio,sub=voice_over(script=script, output_file="../Projects/narration.wav")
#     audio_clip = AudioFileClip(audio)
#     audio_duration = audio_clip.duration
#     print(f"Audio duration: {audio_duration:.2f} seconds")
#     print(f"Subtitles duration: {sum(list(sub.keys())):.2f} seconds") 

#     if sum(list(sub.keys())) != int(audio_duration):
#         new_sub={}
#         for dur,txt in sub.items():
#             new_sub[len(txt.split())/2.5]=sub[dur]
#         sub=new_sub
#     print(f"Subtitles duration: {sum(list(sub.keys())):.2f} seconds") 
#     print('subtitles=',sub)