import os
import requests
import json
from dotenv import load_dotenv
from moviepy import *
import numpy as np
import nltk
NLTK_DATA_DIR=r'.\nltk_data'
nltk.data.path.clear()
nltk.data.path.append(NLTK_DATA_DIR)
# print(nltk.data.path)
assert(NLTK_DATA_DIR==nltk.data.path[0])
nltk.download('punkt',download_dir=NLTK_DATA_DIR)
nltk.download('punkt_tab',download_dir=NLTK_DATA_DIR)
from nltk.tokenize import sent_tokenize

# Load API keys from environment variables
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def search_img(query,per_page=1):
    """Search for images on Pexels based on the provided query."""
    base_url= "https://api.pexels.com/v1/search"
    headers={"Authorization": PEXELS_API_KEY}
    params={
        'query': query,
        'orientation': 'landscape',
        'size':'medium', #medium=12 MP
        'per_page': per_page,
    }

    response = requests.get(base_url, headers=headers, params=params)

    #Checking if response is valid or not
    if response.status_code== 200:
        data=response.json()
        # print(json.dumps(data, indent=4))
        photo= data['photos'][0]['src']['landscape']
        # print(photo)
        return photo
    else:
        print(f"Error: {response.status_code}")
        return None


def search_videos(query, per_page=5):
    base_url='https://api.pexels.com/videos/search'
    headers={'Authorization':PEXELS_API_KEY}
    params={
        'query': query,
        'size':'medium', #medium=FUll HD
        'per_page': per_page,
        'orientation':'landscape'
    }

    response= requests.get(base_url, headers=headers, params=params)
    #Checking if response is valid or not
    if response.status_code== 200:
        data=response.json()
        # print(json.dumps(data, indent=4))
        for video in data['videos']:
            if video['duration'] <= 15 and video['duration'] >= 9:
                for vid in video['video_files']:
                    if vid['quality'] == 'hd':
                       return vid['link']
                return video['video_files'][0]['link']
        return None
    else:
        print(f"Error: {response.status_code}")
        return None


def fetch_clips(keywords:list):
    """Generate a video based on the provided keywords."""
    video=[]   
    num_vid, num_img=0,0
    for keyword in keywords[0:16]:
        clips=search_videos(keyword)
        if clips:
            video.append(clips)
            num_vid+=1
        else:
            clips=search_img(keyword)
            if clips:
                video.append(clips)
                num_img+=1
            else: 
                continue    
    return video,num_vid,num_img   

#download all the fetched clips 
def download_clips(clips: list, project_name: str):
    """Download the video clips from the provided URLs."""
    # Create a directory to save the clips
    folder = f'{project_name}/clips/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    video_files = []
    for i, clip in enumerate(clips):
        # Determine file extension
        if clip.endswith('.mp4'):
            file_path = os.path.join(folder, f'{i}.mp4')
        else:
            file_path = os.path.join(folder, f'{i}.jpg')
        # Download the video clip or image
        response = requests.get(clip, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            video_files.append(file_path)
        else:
            print(f"Error downloading clip ({clip}): {response.status_code}")
    return video_files


def add_subtitles(VideoFile, narration:str, audio_duration: float):
    """Add subtitles to the provided video file."""

    # Step 1: Split script into real sentences
    sentences = sent_tokenize(narration)

    # Step 2: Calculate word count and speaking speed
    word_count = sum(len(s.split()) for s in sentences)
    audio_speed = word_count / audio_duration  # words/sec

    # Step 3: Build subtitles with correct durations
    subtitles = {}
    for sentence in sentences:
        dur = round(len(sentence.split()) / audio_speed, 2)
        subtitles[dur] = sentence

    # Step 4: Rescale if needed
    total_sub_dur = sum(list(subtitles.keys()))
    scaling_factor = audio_duration / total_sub_dur

    if abs(total_sub_dur - audio_duration) > 0.1:
        subtitles = {round(d * scaling_factor, 2): txt for d, txt in subtitles.items()}


    # Accumulate time
    start_time = 0
    subtitle_clips = []

    for duration, sub in subtitles.items():
        # Create a text clip
       try:
            txt_clip = TextClip(
                font=r"C:\Users\Super\OneDrive\Desktop\Youtube Automation\GEO_AI__.ttf",
                text=sub,
                font_size=35,
                text_align='center',
                color='#000000',
                stroke_color='#000000',
                bg_color='#C4C4C4',
                size=(int(VideoFile.w * 0.8), None),
                method='caption'
            ).with_duration(duration).with_position(('center', 'bottom')).with_start(start_time)

            subtitle_clips.append(txt_clip)
            start_time += duration  # update for next subtitle
       except Exception as e:
            print(f"Error creating subtitle clip: {e}")

    # Combine original video and subtitles
    try:
        finalvideo = CompositeVideoClip([VideoFile, *subtitle_clips])
    except Exception as e:
            print(f"Error compositing subtitle clip: {e}")    
    return finalvideo


def generate_video(keywords: list, project_dir: str, filename: str, voiceover: str, subtitles: dict):
    """Generate a video from the generated subtitles, scenes, voiceovers."""
    try:
        audio_clip = AudioFileClip(voiceover)
        audio_duration = audio_clip.duration
        print(f"Audio duration: {audio_duration:.2f} seconds")
        
        if not keywords:
            # No keywords, use black screen with full audio duration
            black_clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8)).with_duration(audio_duration)
            processed_clips = [black_clip]
        else:
            # Fetch and download clips
            fetched_clips,num_videos,num_images = fetch_clips(keywords)
            print(f"\n\nFetched items: {fetched_clips}")
                        
            video_total_duration = (num_videos * 5) if num_images >0 else audio_duration
            print(f"\n\nNumber of video clips: {num_videos}\nTotal video clip duration: {video_total_duration:.2f} seconds")
           
            # iMAGES lOGIC
            image_duration = max((audio_duration - video_total_duration) / num_images, 0) if (num_images >0 or (audio_duration+5) > video_total_duration ) else 0
            print(f"\n\nNumber of image clips: {num_images}\nImage clip duration: {image_duration:.2f} seconds")
            num_images= num_images if image_duration > 0 else 0

            clip_duration = 5 if num_images >0 or (audio_duration+5) > video_total_duration else (audio_duration / num_videos) if num_videos > 0 else audio_duration
            print(f" \n\nper Video clip duration: {clip_duration:.2f} seconds\n\n")
            
            fetched_clips=[clip for clip in fetched_clips if clip.lower().startswith('"https://player.vimeo.com/') or clip.lower().startswith('https://videos.pexels.com/') or clip.lower().endswith('.mp4') ] if num_images==0 or image_duration==0 else fetched_clips
            print(f"\n\nFiltered clips: {fetched_clips}")
            clips = download_clips(fetched_clips, project_dir)
            # print(f"\n\nDownloaded clips: {clips}")
            
            processed_clips = []

            
            
            # Process video clips
            for clip_path in clips:
                if clip_path.lower().endswith('.mp4'):
                    try:
                        clip = VideoFileClip(clip_path)
                        resized_clip = clip.resized(height=1080, width=1920)
                        trimmed_clip = resized_clip.subclipped(start_time=0, end_time=min(clip.duration, clip_duration))
                        processed_clips.append(
                            trimmed_clip.with_effects(
                                [vfx.FadeIn(1), vfx.FadeOut(2)]
                            ))
                    except Exception as e:
                        print(f"Error processing video clip {clip_path}: {e}")

                elif clip_path.lower().endswith(".jpg") and num_images>0:
                    try:
                        clip = ImageClip(clip_path).with_duration(image_duration)
                        resized_clip = clip.resized(height=1080, width=1920)
                        processed_clips.append(
                            resized_clip.with_effects(
                                    [vfx.FadeIn(1), vfx.FadeOut(2)]
                                ))
                    except Exception as e:
                        print(f"Error processing image clip {clip_path}: {e}")
                        
        if not processed_clips:
            black_clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8)).with_duration(audio_duration)
            processed_clips = [black_clip]
            print("No valid clips to process. Exiting video generation.")
            return None
        
        
        # Create final video
        final_video = concatenate_videoclips(processed_clips, method="compose", padding=-0.5)
        
        # Add voiceover audio
        final_video = final_video.with_audio(audio_clip)
        
        #Add subtitles
        final_video = add_subtitles(final_video, subtitles, audio_duration) if subtitles else final_video
        
        # writeback the final video at the specified path
        final_video.write_videofile(filename, fps=30, audio=True, audio_fps=44100, write_logfile=False, logger=None)
        return filename

    except Exception as e:
        print(f"An error occurred during video generation: {e}")
        return None

    finally:
        # Clean up resources
        try:
            audio_clip.close()
        except:
            pass
        for clip in locals().get('processed_clips', []):
            try:
                clip.close()
            except:
                pass
        try:
            final_video.close()
        except:
            pass

# Run the main function
# if __name__ == "__main__":

#     # Define the directory path
#     dir_path = r"C:\Users\Super\OneDrive\Desktop\Youtube Automation\Projects\Law_of_Attraction_Secrets__Attract_Happiness_and_Fulfillment_into_Your_Life\clips"

#     # Base path you want to include in the final string
#     base_path = "Projects/Law_of_Attraction_Secrets__Attract_Happiness_and_Fulfillment_into_Your_Life/clips"

#     # List all files in the directory
#     filenames = [
#         f"{base_path}/{filename}"
#         for filename in os.listdir(dir_path)
#         if os.path.isfile(os.path.join(dir_path, filename))
#     ]

#     print(generate_video(dwnld=filenames, project_dir='Projects', filename='filename', voiceover='Projects/Law_of_Attraction_Secrets__Attract_Happiness_and_Fulfillment_into_Your_Life/voiceovers/Law_of_Attraction_Secrets__Attract_Happiness_and_Fulfillment_into_Your_Life.wav'))

#     # print(f'\n\n{search_videos('mountains', per_page=5)}\n\n')
#     # clips=['clips/0.mp4', 'clips/1.jpg', 'clips/2.mp4', 'clips/3.jpg']
#     # print(generate_video(clips))
#     # # # print(search_img('business presentation', per_page=1))
#     # # keywords = {
#     # #             "scene_1": ["office meeting", "business presentation"],
#     # #             "scene_2": ["forest", "sunlight through trees",]
#     # #             }
    # # print(download_clips(fetch_clips(keywords)), 'happy for you')