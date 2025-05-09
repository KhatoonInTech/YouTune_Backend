from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from rich.console import Console
from rich.markdown import Markdown
import os
import re
from Agents import idea_agent
from Agents import scriptagent
from Agents import text_to_speech_agent as tts_agent
from Agents import video_agent

app = FastAPI(
    title="YouTube Automation API",
    description="An API for automating the creation of YouTube videos.",
    version="1.0.0",
)

class ProjectResponse(BaseModel):
    title: str
    script: str
    voiceover: str
    video: str
    subtitles: List[Dict[str, str]]

class TitleResponse(BaseModel):
    title: str

class ScriptResponse(BaseModel):
    script: str

class VoiceOverResponse(BaseModel):
    voiceover: str
    subtitles: List[Dict[str, str]]

class VideoResponse(BaseModel):
    video: str

class ProjectCreationRequest(BaseModel):
    title: str

@app.get("/", summary="Welcome to the YouTube Automation API")
async def welcome():
    """
    Welcome to the YouTube Automation API!  This API provides endpoints for automating the creation of YouTube videos.

    Available endpoints:

    - `/docs`: Get API documentationa and test endpoints seemlessly.
    - `/generate_title`: Generates a video title using the idea agent.
    - `/generate_script/{title}`: Generates a video script and scenes for a given title.
    - `/generate_voiceover/{title}`: Generates a voiceover for a given script (script is generated from the given title).
    - `/generate_video/{title}`: Generates a video using the generated script and voiceover from the given title.
    - `/create_project`: Creates a full project using all agents, based on a request body containing project title.
    """
    return {
        "message": "Welcome to the YouTube Automation API!",
        "version": "1.0.0",
        "endpoints": {
            "/docs": "This API documentation.",
            "/generate_title": "GET: Generate a video title using the idea agent.",
            "/generate_script/{title}": "GET: Generate a video script and scenes for a given title.",
            "/generate_voiceover/{title}": "GET: Generate a voiceover for a given script.",
            "/generate_video/{title}": "GET: Generate a video using the generated script and voiceover.",
            "/create_project": "POST: Create a full project using all agents, based on a request body containing project title."
        }
    }


@app.get("/generate_title", response_model=TitleResponse, summary="Generate a Video Title")
async def generate_title():
    """
    Generates a video title using the idea agent.
    """
    try:
        title = idea_agent.main()
        return TitleResponse(title=title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate_script/{title}", response_model=ScriptResponse, summary="Generate a Video Script")
async def generate_script(title: str):
    """
    Generates a video script and scenes for a given title.
    """
    try:
        filename = re.sub(r'[?*/\\<>|":]', '_', "_".join(title.split()))
        project_dir = f"Projects/{filename}"  # Correctly construct the project directory name.
        os.makedirs(os.path.join(project_dir, 'scripts'), exist_ok=True)
        script_agent_response = scriptagent.gen_script_and_scenes(title, filename=f'{project_dir}/scripts/{filename}.md')
        script = script_agent_response.get('script')
        return ScriptResponse(script=script)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate_voiceover/{title}", response_model=VoiceOverResponse, summary="Generate a Voiceover")
async def generate_voiceover(title: str):
    """
    Generates a voiceover for a video using the generated script.
    """
    try:
        filename = re.sub(r'[?*/\\<>|":]', '_', "_".join(title.split()))
        project_dir = f"Projects/{filename}"
        os.makedirs(os.path.join(project_dir, 'voiceovers'), exist_ok=True)

        # Assuming you need to generate the script first to get the voiceover...
        script_agent_response = scriptagent.gen_script_and_scenes(title, filename=f'{project_dir}/scripts/{filename}.md')
        script = script_agent_response.get('script')

        subtitles, voiceover_file = tts_agent.voice_over(script, output_file=f'{project_dir}/voiceovers/{filename}.wav')
        return VoiceOverResponse(voiceover=voiceover_file, subtitles=subtitles)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/generate_video/{title}", response_model=VideoResponse, summary="Generate a Video")
async def generate_video(title: str):
    """
    Generates a video using the generated script and voiceover.
    """
    try:
        filename = re.sub(r'[?*/\\<>|":]', '_', "_".join(title.split()))
        project_dir = f"Projects/{filename}"

        # Ensure necessary directories exist
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'voiceovers'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scripts'), exist_ok=True)


        # Re-generate the script and voiceover if they aren't already available
        script_agent_response = scriptagent.gen_script_and_scenes(title, filename=f'{project_dir}/scripts/{filename}.md')
        script = script_agent_response.get('script')
        subtitles, voiceover_file = tts_agent.voice_over(script, output_file=f'{project_dir}/voiceovers/{filename}.wav')


        # Generating Scenes
        thumbnail=video_agent.search_img(title)  #str
        scenes=script_agent_response.get('scenes')       #dict of scenes and their respective keywords
        keywords = [keyword for scene in scenes.values() for keyword in scene]         #list of keywords

        final_video_file=video_agent.generate_video(keywords, project_dir,f'{project_dir}/{filename}.mp4', voiceover_file, subtitles)


        return VideoResponse(video=final_video_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/create_project", response_model=ProjectResponse, summary="Create a Full Project")
async def create_project(project_request: ProjectCreationRequest):
    """
    Creates a full project, generating a title, script, voiceover, and video.
    """
    console = Console()

    try:
        title = project_request.title

        # Project Directory Setup
        filename = re.sub(r'[?*/\\<>|":]', '_', "_".join(title.split()))
        project_dir = f"Projects/{filename}"
        os.makedirs(project_dir, exist_ok=True)
        scripts_dir = os.path.join(project_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        voiceovers_dir = os.path.join(project_dir, "voiceovers")
        os.makedirs(voiceovers_dir, exist_ok=True)

        # Generate Script
        script_agent_response = scriptagent.gen_script_and_scenes(title, filename=f'{scripts_dir}/{filename}.md')
        script = script_agent_response.get('script')
        console.print("\nGenerated Script:")
        console.print(Markdown(script))

        # Generate Voiceover
        subtitles, voiceover_file = tts_agent.voice_over(script, output_file=f'{voiceovers_dir}/{filename}.wav')

        # Generate Video
        thumbnail=video_agent.search_img(title)  #str
        scenes=script_agent_response.get('scenes')       #dict of scenes and their respective keywords
        keywords = [keyword for scene in scenes.values() for keyword in scene]         #list of keywords
        final_video_file=video_agent.generate_video(keywords, project_dir,f'{project_dir}/{filename}.mp4', voiceover_file, subtitles)


        return ProjectResponse(
            title=title,
            script=script,
            voiceover=voiceover_file,
            video=final_video_file,
            subtitles=subtitles
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)