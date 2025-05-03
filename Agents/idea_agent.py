import os
import re
from dotenv import load_dotenv

from googleapiclient.discovery import build
# import pprint
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage


# Load API keys from environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
# Initialize YouTube API
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
#Initialize LLM
llm = ChatGroq(temperature=0.7,model_name="Gemma2-9b-It", groq_api_key=GROQ_API_KEY)

def api_call(category):
    """Fetch top 10 trending YouTube videos related to the given category."""
    request = youtube.search().list(
        part="snippet",
        maxResults=5,  # Fetch top 5 trending videos
        q=category,
        type="video",
        order="viewCount"
    )
    response = request.execute()
    # pprint.pprint(response)

    return response
    
def trending_titles(category):
    """Return the top trending YouTube video related to the given category."""
    titles = api_call(category)
    if titles:
        return [item["snippet"]["title"] for item in titles.get("items", [])]
    else:
        return "No trending videos found for this category."
    
#remove hashtags from titles
def clean_titles(titles):
    """Remove hashtags,spaecial symbols, extra spaces,etc from video titles."""
    return [re.sub(r"[^\w\s]", " ", title).strip() for title in titles]

#suggest similar titles with ai
def suggest_titles(title):
    """Suggest 5 similar titles to the selected title using AI."""
    prompt = f"""Your job is to Generate 5 similar titles to the one title, given to you. Make sure that these titles hold all the trending and search engine optimized keywords and are similar in niche and tone to the provided title. Output the titles in a non-numbered list i.e., start a new title from a new line, without any additional explanations.

     Title: {title}"""
    response=llm.invoke([SystemMessage(content=prompt)])
    # print(response.content.splitlines())
    return response.content.splitlines()

#user choice for selection of the title
def user_select_title(titles,purpose):
    """User selects a title from the top 5 trending titles."""
    user_choice =input(f"\nDo you want {purpose} from any of the above titles? (y/n): ")
    if user_choice.lower() == "y" or user_choice.lower() == "yes":
        title_number = int(input(f"\nEnter a title number from above titles {purpose}: "))
        if title_number>5 or title_number<1:
            print("\nInvalid title number. Please try again.")
            return user_select_title(purpose)  
        return titles[title_number-1]
    else:
       return input(f"\nPlease enter a custom title {purpose}: ")

# Display results
def display_results(response,query="Trending"):
    print(f"\nTop 5 {query} YouTube Video Titles  are:\n{'-'*50}\n")
    for idx, item in enumerate(response, start=1):
        print(f"{idx}. {item}")
        if idx == 5:
            break
    print("-"*150)    

# Main function
def main():
    topic = input("Enter a niche (e.g., tech, gaming, finance): ").strip()
    response = trending_titles(topic)
    final_response = clean_titles(response)
    display_results(final_response)
    # display_results(response)  
     
    # Select a specific title
    selected_title= user_select_title(final_response," to generate similar titles")
    similar_titles = suggest_titles(selected_title)

    display_results(similar_titles,query="Similar, AI-Suggested")

    final_title=user_select_title(similar_titles," to continue and generate script based on this title")
    # print(f"Final Title: {final_title}")
    return final_title

# Run the main function
if __name__ == "__main__":
    main()            