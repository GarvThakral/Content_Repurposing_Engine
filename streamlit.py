import streamlit as st
from langchain_openai import ChatOpenAI
from os import getenv
from langchain.prompts import ChatPromptTemplate 
from langchain_core.messages import SystemMessage , HumanMessage , AIMessage
from langchain_community.document_loaders import YoutubeLoader
from typing import List, Optional
from pydantic import BaseModel
import streamlit.components.v1 as components
import pypdf
import requests
from bs4 import BeautifulSoup


# creating a pdf reader object

def get_openrouter(model="x-ai/grok-4-fast:free") -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        openai_api_base="https://openrouter.ai/api/v1"
    )   

def prompt_to_generate_media(list_of_media_to_generate , instructions_of_media_to_generate , userInput , context):
    media_instructions = {
        "twitter": [
            "Generate post content",
            "Add relevant hashtags",
            "Include engaging call-to-action",
            "Keep it concise within character limits"
        ],
        "instagram": [
            "Generate post content",
            "Add visually appealing captions",
            "Use trending hashtags",
            "Suggest image/video ideas",
            "Include call-to-action in caption"
        ],
        "email": [
            "Generate email newsletter snippets",
            "Craft engaging subject lines",
            "Write short but valuable body content",
            "Add CTA links or buttons"
        ],
        "tiktok scripts": [
            "Generate full TikTok video scripts",
            "Include attention-grabbing hooks",
            "Structure with storytelling",
            "Add trending sounds/effects suggestions",
            "Include clear CTA at the end"
        ],
        "reel scripts": [
            "Generate full Instagram Reel scripts",
            "Include opening hook",
            "Write engaging narration/dialogue",
            "Suggest visuals and transitions",
            "End with CTA or punchline"
        ] 
    }
    list_of_media_to_generate_string = " ,".join(list_of_media_to_generate)
    print(list_of_media_to_generate_string)

    media_instructions_string = " ".join(["'" + k + " instruction' : " + " ,".join(v) + "\n" for k,v in media_instructions.items() if k in list_of_media_to_generate])
    print(media_instructions_string)

    user_instructions_string = " ".join(["'" + k + " instruction' : " + v + "\n" for k,v in instructions_of_media_to_generate.items() if k in list_of_media_to_generate])
    print(user_instructions_string)

    user_input = userInput + " \n\n Context : " + context    

    prompt = ChatPromptTemplate.from_messages([
        ("system",""""
            You are a content generation AI agent , you are supposed to generate content for {list_of_media_to_generate_string} . Based on the
            following user instructions : {user_instructions_string} . You have to follow certain System instructions to reach the desired output , these instructins are {media_instructions_string}.
            Generate all what is asked using the context/transcripts of the content provided by the user . 
        """),

        ("human","{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    result = prompt.invoke({"input":user_input , "list_of_media_to_generate_string":list_of_media_to_generate_string , "media_instructions_string":media_instructions_string , "user_instructions_string":user_instructions_string})

    return result
    
demo_instructions = {
        

    "twitter": "I am writing a post about World Health Day. Generate a Twitter post with a short impactful message and hashtags.",
    
    "instagram": "I am launching my handmade candle business. Write an Instagram caption with emojis, trendy hashtags, and suggest a reel idea.",
    
    "email": "Draft an email newsletter snippet for my online bookstore’s fall sale, including a catchy subject line and a short promo paragraph.",
    
    "tiktok scripts": "Create a TikTok script about quick morning workouts at home. Include an engaging hook, step-by-step demo ideas, and a strong CTA.",
    
    "reel scripts": "Write an Instagram Reel script about coffee brewing hacks. Add a fun opening line, step-by-step narration, and suggest transitions."
}

multi_media_to_generate = ["twitter","instagram","email","tiktok scripts","reel scripts"]

placeholders = {
    "twitter": "Generate me a Twitter post for my new product launch, keep it short and impactful with hashtags.",
    "instagram": "Write me an Instagram caption with emojis and trendy hashtags for my handmade business post.",
    "email": "Draft an email newsletter snippet announcing a seasonal sale with a catchy subject line and short body.",
    "tiktok scripts": "Create a TikTok script about a quick workout routine, include an engaging hook and step-by-step flow.",
    "reel scripts": "Write an Instagram Reel script about coffee brewing hacks, with a fun opening and smooth transitions."
}


def extract_content(content_type , input_context):
  if content_type == "Youtube Video":
    loader = YoutubeLoader.from_youtube_url(
        input_context
    )
    content = loader.load()[0].page_content
    print(content)
  elif content_type == "Blog post":
    response = requests.get(input_context)
    soup = BeautifulSoup(response.text, "html.parser")
    all_text = soup.get_text(separator=" ", strip=True)
    print(all_text)
  elif content_type == "PDF":
    content = "" 
    
    if input_context:
      reader = pypdf.PdfReader(input_context)
      for x in reader.pages:
        text = x.extract_text()
        clean_string = ' '.join(text.split())
        if text:
            content += " " + clean_string


# def generate_content():
#     model = get_openrouter()
#     prompt = prompt_to_generate_media(multi_media_to_generate , demo_instructions ,"Generate a post for instagram and twitter ." , loader.load()[0].page_content)

    
content_type_dropbox = st.selectbox(
    "Select the content type you want to post about !",
    ("Youtube Video","Blog post","PDF","Text input"),
    placeholder="Select content type...",
)


if content_type_dropbox == "Youtube Video":
  input_context = st.text_input("Enter video URL", value=None, max_chars=None, key=None, type="default", help=None, autocomplete=None, placeholder="https://youtube.com/watch/4141e12?1221", label_visibility="visible", width="stretch")

elif content_type_dropbox == "Blog post":
  input_context = st.text_input("Enter BlogPost URL", value=None, max_chars=None, key=None, type="default", help=None, autocomplete=None, placeholder="https://medium.com/engage/collective-be-....", label_visibility="visible", width="stretch")
elif content_type_dropbox == "PDF":
  input_context = st.file_uploader("Upload your PDF", type="pdf", accept_multiple_files=False, key=None, help=None, on_change=None, 
  args=None,  disabled=False, label_visibility="visible", width="stretch")


elif content_type_dropbox == "Text input":
    input_context = st.text_area("Enter your content as plain text !", value="", height=None, max_chars=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible", width="stretch")



st.title("Pick the platforms you want to generate content/scripts for .", anchor=None, help=None, width="stretch")


selected = {}
selected_instructions = {}

for option in multi_media_to_generate:
    selected[option] = st.checkbox(
        option,     
        value=None,
        key=option.lower().replace(" ", "_")
    )
    if selected.get(option):
        selected_instructions[option] = st.text_area(option[0].upper() + option + " Post Instructions", value="", height=None, max_chars=None, key=None, help=None, on_change=None, args=None, kwargs=None , placeholder=placeholders[option], disabled=False, label_visibility="visible", width="stretch")

button_gen = st.button("Generate content", key=None, help=None, on_click=None, args=None, kwargs=None, type="primary", icon=None, disabled=False, use_container_width=None, width="content")

if button_gen:
   extract_content(content_type_dropbox,input_context)

st.write(selected)


twitter_string = """
    <!-- ===== Twitter-like Post Card (Drop-in HTML+CSS) ===== -->
<div class="tweet">
  <!-- Avatar -->
  <img class="tweet-avatar" src="https://picsum.photos/seed/avatar/96" alt="Avatar" />

  <!-- Body -->
  <div class="tweet-body">
    <!-- Header -->
    <div class="tweet-header">
      <span class="tweet-name">Jane Doe</span>
      <span class="tweet-verified" aria-label="Verified">✔︎</span>
      <span class="tweet-handle">@janedoe</span>
      <span class="tweet-dot">·</span>
      <time class="tweet-time" datetime="2025-10-01T09:24:00Z">2h</time>
    </div>

    <!-- Content (EDIT THIS TEXT) -->
    <div class="tweet-text">
      Launching my new project today — lightning fast, privacy-first, and open source. 🚀
      Can’t wait to hear your thoughts!
            Launching my new project today — lightning fast, privacy-first, and open source. 🚀

    </div>

    <!-- Optional media (remove if not needed) -->
    <!-- <div class="tweet-media">
      <img src="https://picsum.photos/seed/project/800/450" alt="Attached image" />
    </div> -->

    <!-- Hashtags (ADD / REMOVE a tags as needed) -->
    <div class="tweet-tags">
      <a href="#" class="tweet-tag">#OpenSource</a>
      <a href="#" class="tweet-tag">#Privacy</a>
      <a href="#" class="tweet-tag">#LaunchDay</a>
    </div>

    <!-- Actions -->
    <div class="tweet-actions">
      <button class="tweet-action" aria-label="Reply">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M14 9V5l-7 7 7 7v-4h5V9z"/></svg>
        <span>32</span>
      </button>
      <button class="tweet-action" aria-label="Repost">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M7 7h9V4l5 4-5 4V9H7V7zm10 10H8v3l-5-4 5-4v3h9v2z"/></svg>
        <span>120</span>
      </button>
      <button class="tweet-action" aria-label="Like">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12.1 21.35l-1.1-1.02C5.14 14.87 2 12.06 2 8.5 2 6 4 4 6.5 4c1.74 0 3.41.9 4.3 2.28C11.09 4.9 12.76 4 14.5 4 17 4 19 6 19 8.5c0 3.56-3.14 6.37-8.9 11.83l-1 1.02z"/></svg>
        <span>987</span>
      </button>
      <button class="tweet-action" aria-label="Bookmark">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 2h12a1 1 0 0 1 1 1v19l-7-4-7 4V3a1 1 0 0 1 1-1z"/></svg>
      </button>
    </div>
  </div>
</div>

<style>
  /* ------- Minimal Twitter-like styles ------- */
  :root {
    --bg: #0f1419;              /* dark background */
    --card: #15202b;            /* card background */
    --text: #e6e9ec;            /* primary text */
    --muted: #8b98a5;           /* secondary text */
    --accent: #1d9bf0;          /* Twitter blue */
    --border: #263340;          /* subtle border */
    --tag-bg: rgba(29,155,240,0.12);
    --radius: 16px;
  }
  /* Light mode (optional): add class="light" to html or body to switch */
  .light :root, .light-root {
    --bg: #ffffff;
    --card: #ffffff;
    --text: #0f1419;
    --muted: #536471;
    --accent: #1d9bf0;
    --border: #eff3f4;
    --tag-bg: rgba(29,155,240,0.10);
  }

  .tweet {
    display: grid;
    grid-template-columns: 48px 1fr;
    gap: 12px;
    max-width: 620px;
    padding: 12px 16px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
    color: var(--text);
  }

  .tweet-avatar {
    width: 48px;
    height: 48px;
    border-radius: 999px;
    object-fit: cover;
  }

  .tweet-body { display: flex; flex-direction: column; gap: 8px; }

  .tweet-header {
    display: flex; align-items: center; gap: 6px;
    font-size: 15px; line-height: 1.2;
  }
  .tweet-name { font-weight: 700; color: var(--text); }
  .tweet-verified { font-size: 13px; color: var(--accent); }
  .tweet-handle, .tweet-time, .tweet-dot { color: var(--muted); }

  .tweet-text {
    font-size: 15px; line-height: 1.5; white-space: pre-wrap;
  }

  .tweet-media {
    border: 1px solid var(--border);
    border-radius: 12px; overflow: hidden;
  }
  .tweet-media img { display: block; width: 100%; height: auto; }

  .tweet-tags { display: flex; flex-wrap: wrap; gap: 6px; }
  .tweet-tag {
    display: inline-block;
    padding: 6px 10px;
    font-size: 14px;
    color: var(--accent);
    background: var(--tag-bg);
    border-radius: 999px;
    text-decoration: none;
  }

  .tweet-actions {
    display: flex; align-items: center; gap: 18px;
    padding-top: 6px; border-top: 1px solid var(--border);
  }
  .tweet-action {
    display: inline-flex; align-items: center; gap: 6px;
    background: transparent; border: 0; color: var(--muted);
    font-size: 13px; cursor: pointer; padding: 6px 8px; border-radius: 999px;
  }
  .tweet-action:hover { background: rgba(255,255,255,0.06); color: var(--text); }
  .tweet-action svg { fill: currentColor; display: block; }
</style>
<!-- ===== End Card ===== -->
"""
instagram_string = """
<!-- ===== Instagram Post Card (Drop-in HTML+CSS) ===== -->
<div class="ig-card">
  <!-- Header -->
  <div class="ig-header">
    <img class="ig-avatar" src="https://picsum.photos/seed/iguser/80" alt="Avatar" />
    <div class="ig-user">
      <div class="ig-user-top">
        <span class="ig-name">jane.doe</span>
        <span class="ig-verified" aria-label="Verified">✔︎</span>
      </div>
      <div class="ig-meta">Bengaluru, India</div>
    </div>
    <button class="ig-more" aria-label="More">•••</button>
  </div>

  <!-- Media -->
  <div class="ig-media">
    <!-- Replace with your image/video -->
    <img src="https://picsum.photos/seed/igmedia/1080/1080" alt="Post media" />
    <!-- For video, swap to: <video controls src="..."></video> -->
  </div>

  <!-- Actions -->
  <div class="ig-actions">
    <div class="ig-actions-left">
      <button class="ig-btn" aria-label="Like" title="Like">
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M12.1 21.35l-1.1-1.02C5.14 14.87 2 12.06 2 8.5 2 6 4 4 6.5 4c1.74 0 3.41.9 4.3 2.28C11.09 4.9 12.76 4 14.5 4 17 4 19 6 19 8.5c0 3.56-3.14 6.37-8.9 11.83l-1 1.02z"/></svg>
      </button>
      <button class="ig-btn" aria-label="Comment" title="Comment">
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M21 6h-2v9H7l-4 4V6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"/></svg>
      </button>
      <button class="ig-btn" aria-label="Share" title="Share">
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M18 8a3 3 0 1 0-2.82-4H15a3 3 0 0 0 0 6h.18A3.002 3.002 0 0 0 18 8zM6 14a3 3 0 1 0 2.82 4H9a3 3 0 0 0 0-6H8.82A3.002 3.002 0 0 0 6 14zm12 0a3 3 0 1 0 2.82 4H21a3 3 0 0 0 0-6h-.18A3.002 3.002 0 0 0 18 14z"/></svg>
      </button>
    </div>
    <button class="ig-btn ig-save" aria-label="Save" title="Save">
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M6 2h12a1 1 0 0 1 1 1v19l-7-4-7 4V3a1 1 0 0 1 1-1z"/></svg>
    </button>
  </div>

  <!-- Likes -->
  <div class="ig-likes">8,942 likes</div>

  <!-- Caption -->
  <div class="ig-caption">
    <span class="ig-name">jane.doe</span>
    <span class="ig-text">
      Launch day ✨ Built with love and late nights. Drop your thoughts below!
    </span>
    <span class="ig-tags">
      <a href="#" class="ig-tag">#Startups</a>
      <a href="#" class="ig-tag">#Creator</a>
      <a href="#" class="ig-tag">#Reels</a>
    </span>
  </div>

  <!-- View comments -->
  <button class="ig-view-comments">View all 127 comments</button>

  <!-- Time -->
  <div class="ig-time">2 HOURS AGO</div>
</div>

<style>
  :root {
    --bg: #000;
    --card: #0f0f0f;
    --text: #eaeaea;
    --muted: #a1a1a1;
    --border: #262626;
    --chip: #1f1f1f;
    --accent: #ff2d55; /* IG vibe */
    --radius: 14px;
    --font: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
  }
  .ig-card {
    width: 100%;
    max-width: 540px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin: 0 auto;
    background: var(--card);
    color: var(--text);
    font-family: var(--font);
    overflow: hidden;
  }
  .ig-header {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 14px;
  }
  .ig-avatar {
    width: 38px; height: 38px; border-radius: 999px; object-fit: cover;
    border: 2px solid transparent;
    background:
      radial-gradient(#fff 0 0) padding-box,
      conic-gradient(#f58529, #feda77, #dd2a7b, #8134af, #515bd4, #f58529) border-box;
  }
  .ig-user { display: flex; flex-direction: column; line-height: 1.15; }
  .ig-user-top { display: flex; align-items: center; gap: 6px; }
  .ig-name { font-weight: 700; font-size: 14px; }
  .ig-verified { font-size: 12px; color: #58a6ff; }
  .ig-meta { color: var(--muted); font-size: 12px; }
  .ig-more {
    margin-left: auto; background: transparent; color: var(--text);
    border: 0; font-size: 20px; cursor: pointer;
  }

  .ig-media img, .ig-media video { display: block; width: 100%; height: auto; background: #111; }

  .ig-actions {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 10px;
  }
  .ig-actions-left { display: flex; gap: 10px; }
  .ig-btn {
    background: transparent; border: 0; color: var(--text);
    padding: 6px; cursor: pointer; border-radius: 999px;
  }
  .ig-btn:hover { background: #151515; }
  .ig-save { margin-left: auto; }

  .ig-likes {
    font-weight: 700; font-size: 14px; padding: 0 12px; margin-top: 2px;
  }
  .ig-caption {
    padding: 6px 12px 0 12px; font-size: 14px; line-height: 1.45;
  }
  .ig-caption .ig-name { margin-right: 6px; }
  .ig-text { color: var(--text); }
  .ig-tags { display: inline; }
  .ig-tag { color: #a8c6ff; text-decoration: none; margin-left: 6px; }
  .ig-tag:hover { text-decoration: underline; }

  .ig-view-comments {
    display: block; background: transparent; border: 0; color: var(--muted);
    font-size: 14px; padding: 6px 12px; cursor: pointer; text-align: left;
  }
  .ig-time {
    color: var(--muted); font-size: 11px; letter-spacing: .2px;
    padding: 6px 12px 12px 12px;
  }
</style>
"""
scripts_string = """
<!-- ===== Short-form Video Script Card (TikTok/Reels/Shorts) ===== -->
<div class="sc-card">
  <!-- Header -->
  <div class="sc-header">
    <div class="sc-title">
      <span class="sc-name">Productivity Hack in 30s</span>
      <span class="sc-badges">
        <span class="sc-badge">TikTok</span>
        <span class="sc-badge sc-alt">Reels</span>
        <span class="sc-badge sc-alt2">Shorts</span>
      </span>
    </div>
    <div class="sc-meta">
      <span>~30s</span>
      <span class="sc-dot">•</span>
      <span>Hook & 4 beats</span>
    </div>
  </div>

  <!-- Script Content -->
  <div class="sc-body">
    <!-- Hook -->
    <div class="sc-block">
      <div class="sc-block-title">Hook (0:00–0:03)</div>
      <div class="sc-block-text">“Stop scrolling. This 30-second habit doubled my focus — here’s how.”</div>
    </div>

    <!-- Beats -->
    <div class="sc-grid">
      <div class="sc-block">
        <div class="sc-block-title">Beat 1 (0:03–0:08)</div>
        <div class="sc-block-text">Show messy desk → quick timer app shot. VO: “Set a 25-minute timer.”</div>
      </div>
      <div class="sc-block">
        <div class="sc-block-title">Beat 2 (0:08–0:14)</div>
        <div class="sc-block-text">Cut to doing 1 task only. VO: “Pick one task — just one.”</div>
      </div>
      <div class="sc-block">
        <div class="sc-block-title">Beat 3 (0:14–0:22)</div>
        <div class="sc-block-text">Overlay checklist anim. VO: “No tabs. No notifications.”</div>
      </div>
      <div class="sc-block">
        <div class="sc-block-title">Beat 4 (0:22–0:27)</div>
        <div class="sc-block-text">Show timer hitting zero. VO: “Break for 3 minutes.”</div>
      </div>
    </div>

    <!-- CTA -->
    <div class="sc-block sc-cta">
      <div class="sc-block-title">CTA (0:27–0:30)</div>
      <div class="sc-block-text">“Save this and try one Pomodoro today. Comment ‘DONE’ when you finish.”</div>
    </div>

    <!-- Extras -->
    <div class="sc-extras">
      <div class="sc-tags">
        <span class="sc-chip">#Productivity</span>
        <span class="sc-chip">#StudyWithMe</span>
        <span class="sc-chip">#Focus</span>
      </div>
      <div class="sc-note">Notes: Replace text with your generated script. Adjust timings for platform.</div>
    </div>
  </div>
</div>

<style>
  :root {
    --bg: #0a0a0a;
    --card: #121316;
    --text: #e8eaed;
    --muted: #a3a7ad;
    --border: #262a31;
    --accent: #7c3aed;   /* purple */
    --accent2: #22c55e;  /* green */
    --accent3: #ef4444;  /* red */
    --chip: #1d1f24;
    --radius: 16px;
    --font: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
  }
  .sc-card {
    width: 100%; max-width: 820px; margin: 0 auto;
    background: var(--card); color: var(--text);
    border: 1px solid var(--border); border-radius: var(--radius);
    font-family: var(--font); overflow: hidden;
  }
  .sc-header {
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 12px; padding: 16px 18px; border-bottom: 1px solid var(--border);
  }
  .sc-title { display: flex; flex-direction: column; gap: 6px; }
  .sc-name { font-size: 20px; font-weight: 800; letter-spacing: .2px; }
  .sc-badges { display: flex; gap: 8px; }
  .sc-badge {
    background: var(--accent); color: white; font-weight: 700;
    padding: 4px 10px; border-radius: 999px; font-size: 12px;
  }
  .sc-badge.sc-alt { background: var(--accent2); }
  .sc-badge.sc-alt2 { background: var(--accent3); }
  .sc-meta { color: var(--muted); font-size: 13px; }

  .sc-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
  .sc-grid {
    display: grid; gap: 12px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .sc-block {
    background: #15171c; border: 1px solid var(--border); border-radius: 12px;
    padding: 12px;
  }
  .sc-block-title { font-weight: 800; margin-bottom: 6px; font-size: 14px; }
  .sc-block-text { color: var(--text); font-size: 14px; line-height: 1.55; }
  .sc-cta { border: 1px dashed #353a44; background: #14161a; }
  .sc-extras { display: flex; flex-direction: column; gap: 10px; margin-top: 4px; }
  .sc-tags { display: flex; flex-wrap: wrap; gap: 8px; }
  .sc-chip {
    background: var(--chip); color: #cbd5e1; border: 1px solid #2a2f37;
    padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
  }
  .sc-note { color: var(--muted); font-size: 12px; }
  @media (max-width: 640px) { .sc-grid { grid-template-columns: 1fr; } }
</style>
"""
gmail_string = """
<!-- ===== Gmail-like Email Preview (Drop-in HTML+CSS) ===== -->
<div class="gm-card">
  <!-- Header -->
  <div class="gm-row gm-header">
    <div class="gm-left">
      <div class="gm-avatar">J</div>
      <div class="gm-from">
        <div class="gm-from-line">
          <span class="gm-name">Jane Doe</span>
          <span class="gm-email">&lt;jane@example.com&gt;</span>
        </div>
        <div class="gm-to">to me</div>
      </div>
    </div>
    <div class="gm-right">
      <span class="gm-date">Oct 1, 2025, 9:24 AM</span>
      <button class="gm-icon" aria-label="Star">☆</button>
      <button class="gm-icon" aria-label="More">⋮</button>
    </div>
  </div>

  <!-- Subject -->
  <div class="gm-row gm-subject">
    <span class="gm-subject-text">Launch plan & next steps</span>
    <div class="gm-labels">
      <span class="gm-label">Important</span>
      <span class="gm-label gm-label-alt">Product</span>
    </div>
  </div>

  <!-- Body -->
  <div class="gm-body">
    <p>Hey there,</p>
    <p>
      Sharing the final launch checklist and owner assignments. Please review and reply with any blockers.
      We go live at <b>18:00 IST</b>.
    </p>
    <ul>
      <li>Landing page: final copy & UTM</li>
      <li>Docs: quickstart + FAQ</li>
      <li>Community: announcement draft</li>
    </ul>
    <p>Cheers,<br/>Jane</p>
  </div>

  <!-- Actions -->
  <div class="gm-actions">
    <button class="gm-btn">Reply</button>
    <button class="gm-btn gm-secondary">Reply all</button>
    <button class="gm-btn gm-secondary">Forward</button>
  </div>
</div>

<style>
  :root {
    --bg: #0b0b0b;
    --card: #111214;
    --text: #e7e9ea;
    --muted: #9aa0a6;
    --border: #2a2c30;
    --accent: #1a73e8;
    --label: #1f2937;
    --label-alt: #2a3c23;
    --radius: 14px;
    --font: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
  }
  .gm-card {
    width: 100%; max-width: 760px; margin: 0 auto;
    background: var(--card); color: var(--text);
    border: 1px solid var(--border); border-radius: var(--radius);
    font-family: var(--font);
    overflow: hidden;
  }
  .gm-row { display: flex; align-items: center; gap: 12px; padding: 14px 18px; }
  .gm-header { border-bottom: 1px solid var(--border); justify-content: space-between; }
  .gm-left { display: flex; align-items: center; gap: 12px; }
  .gm-right { display: flex; align-items: center; gap: 10px; color: var(--muted); }
  .gm-avatar {
    width: 36px; height: 36px; border-radius: 999px;
    background: #26406a; display: grid; place-items: center; font-weight: 700;
  }
  .gm-from-line { display: flex; gap: 6px; align-items: baseline; }
  .gm-name { font-weight: 700; }
  .gm-email { color: var(--muted); font-size: 13px; }
  .gm-to { color: var(--muted); font-size: 12px; }
  .gm-icon {
    background: transparent; border: 0; color: var(--muted);
    font-size: 18px; cursor: pointer; padding: 6px; border-radius: 8px;
  }
  .gm-icon:hover { background: #15171a; color: var(--text); }

  .gm-subject { justify-content: space-between; border-bottom: 1px solid var(--border); }
  .gm-subject-text { font-weight: 700; font-size: 18px; }
  .gm-labels { display: flex; gap: 8px; }
  .gm-label, .gm-label-alt {
    display: inline-block; font-size: 12px; padding: 4px 8px; border-radius: 999px;
    background: var(--label); color: #e5e7eb; border: 1px solid #3b3f46;
  }
  .gm-label-alt { background: var(--label-alt); border-color: #3a4a34; }

  .gm-body { padding: 14px 18px; line-height: 1.6; }
  .gm-body p, .gm-body ul { margin: 0 0 10px 0; }
  .gm-body ul { padding-left: 18px; }

  .gm-actions {
    display: flex; gap: 10px; padding: 14px 18px; border-top: 1px solid var(--border);
  }
  .gm-btn {
    padding: 8px 14px; border-radius: 10px; border: 1px solid #2b2f36;
    background: var(--accent); color: white; font-weight: 600; cursor: pointer;
  }
  .gm-btn.gm-secondary {
    background: #191c20; color: var(--text);
    border: 1px solid #2b2f36;
  }
  .gm-btn:hover { filter: brightness(1.05); }
</style>
"""


html_snippets = {
    "twitter": twitter_string,
    "instagram": instagram_string,
    "email": gmail_string,
    "tiktok scripts": scripts_string,
    "reel scripts": scripts_string,
}

# Build the ordered list of selected content types
selected_types = [k for k, v in selected.items() if v and k in html_snippets]

if not selected_types:
    st.info("No content selected.")
    st.stop()

# Keep track of which slide is active
if "carousel_idx" not in st.session_state:
    st.session_state.carousel_idx = 0

# Clamp index if selection changes
st.session_state.carousel_idx %= len(selected_types)

# Navigation
c1, c2, c3 = st.columns([1, 6, 1])
with c1:
    if st.button("⬅️ Prev"):
        st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % len(selected_types)
with c3:
    if st.button("Next ➡️"):
        st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % len(selected_types)

# Current content type and HTML
ctype = selected_types[st.session_state.carousel_idx]
st.caption(f"Showing: **{ctype}**")

# Render
html = html_snippets.get(ctype, "<div style='padding:16px'>No HTML for this type.</div>")
components.html(html, height=720, scrolling=True)