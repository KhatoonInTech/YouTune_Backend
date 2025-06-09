from rich.console import Console
from rich.markdown import Markdown
import os
import re
from Agents import idea_agent
from Agents import scriptagent
from Agents import text_to_speech_agent as tts_agent
from Agents import video_agent
from Agents import seoAgent
from Agents import uploadAgent
# from Agents import text_speech
def main():
    # Run the idea agent to generate a title
    title = idea_agent.main()
    print("\nThe Finalized Title is:", title)
    print(f"\n{'-'*150}")

# keep track of projects through their respective directories
    filename = re.sub(r'[?*/\\<>|":]', '_', "_".join(title.split()))
    project_dir = f"Projects/{filename}"
    if not os.path.exists(project_dir):
        os.makedirs(project_dir, exist_ok=True)
    # Run the script agent to script
    script_agent_response = scriptagent.gen_script_and_scenes(title, filename=f'{project_dir}/scripts/{filename}.md')
    script=script_agent_response.get('script')
    print(f"\nGenerated Script:")
    console=Console()
    console.print(Markdown(script))
    # print(script)
    print(f"\n{'-'*150}")

    #Run the text_to_speech Agent
    # print(f"\nGenerating Voice Over:")
    # scrpt=tts_agent.clean_script(script)
    # voiceover=text_speech.speech(scrpt, f'{project_dir}/voiceovers/{filename}.wav')
    # print(f"Success: The voice over is successfully generated as {voiceover}")
    # print(f"\n{'-'*150}")

    # Run the text_to_speech Agent
    print(f"\nGenerating Voice Over:")
    subtitles,voiceover=tts_agent.voice_over(script, output_file=f'{project_dir}/voiceovers/{filename}.wav')
    print(f"Success: The voice over is successfully generated as {voiceover}")
    # os.startfile(fr'C:\Users\Super\OneDrive\Desktop\Youtube Automation\{voiceover}')

    print(f"\n{'-'*150}")


    ## Generating Scenes
    thumbnail=video_agent.search_img(title)  #str
    scenes=script_agent_response.get('scenes')       #dict of scenes and their respective keywords
    # print(f"\n\nscenes: {scenes}")
    keywords = [keyword for scene in scenes.values() for keyword in scene]         #list of keywords
    # print(f"\n\nKeywords:{keywords}\n\n Total no of keywords: {len(keywords)}")
    final_video=video_agent.generate_video(keywords, project_dir,f'{project_dir}/{filename}.mp4', voiceover,subtitles)
    print(f"\n\nSuccess: The video is successfully generated as {final_video}")
    os.startfile(fr'C:\Users\Super\OneDrive\Desktop\Youtube Automation\{final_video}')

    print(f"\n{'-'*150}")
    


    #Genenerating SEO optimized description and hashtags
    description_response = seoAgent.gen_description_and_hashtags(title, subtitles, filename=f'{project_dir}/{filename}.json')
    description = description_response.get('description')  #str
    hashtags = description_response.get('hashtags')   #list of hashtags
    print(f"Success: The SEO optimized description and hashtags are stored at : {project_dir}/{filename}.json")
    print(f"\n{'-'*150}")

    #Running Upload Agent
    video_id = uploadAgent.upload_api_call(
        video_file=rf"C:\Users\Super\OneDrive\Desktop\Youtube Automation\{final_video}",
        title=title,
        description=description,
        tags=hashtags
    )
    if video_id is None:
        print("Error: Video upload failed.")
    else:
        print(f"\n\nSuccess: Your video is live at https://www.youtube.com/watch?v={video_id}")
        print(f"\n{'-'*150}")
# Run the main function
if __name__ == "__main__":
    main()    