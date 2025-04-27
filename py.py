import os
from yt_dlp import YoutubeDL

# קרא את נתיב קובץ העוגיות מתוך משתנה הסביבה
cookies_path = os.getenv("COOKIES_PATH")

if not cookies_path:
    raise ValueError("הקובץ של העוגיות לא מוגדר ב-SECRET. יש להוסיף אותו למשתנה הסביבה COOKIES_PATH.")

# הגדרות עבור yt-dlp
ydl_opts = {
    'cookiefile': cookies_path,  # שימוש בקובץ העוגיות
    'outtmpl': '%(title)s.%(ext)s',  # שם הקובץ שיורד
    'format': 'bestvideo+bestaudio/best',  # בחירת האיכות הטובה ביותר
}

# URL של הסרטון להורדה
video_url = input("https://www.youtube.com/watch?v=OkZ30zLdHTY")

# הורדת הסרטון
with YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])
